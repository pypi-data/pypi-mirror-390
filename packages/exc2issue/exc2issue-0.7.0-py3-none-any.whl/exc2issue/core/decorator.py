"""Main bug hunter decorator class with comprehensive error handling.

This module provides the core BugHunterDecorator class that wraps functions
to automatically create GitHub issues when errors occur. The decorator handles:

- Function wrapping with error collection context
- Exception and SystemExit handling
- Integration with consolidated handlers for log errors
- Signal and exit termination handling
- Configuration management for resilience features

The decorator coordinates with other core modules for background processing,
signal handling, issue creation, and registry management.
"""

import contextlib
import functools
import inspect
import logging
import re
import time
import types
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal, cast

from exc2issue.core.background_worker import ensure_background_worker
from exc2issue.core.client_factory import create_ai_client, create_github_client
from exc2issue.core.config_types import AuthConfig, BugHunterConfig, ProcessingConfig
from exc2issue.core.error_collection import ErrorCollection, ErrorCollectionContext
from exc2issue.core.error_handling import (
    handle_exit_cleanup,
    handle_signal_termination,
    handle_system_exit,
)
from exc2issue.core.handlers import ConsolidatedHandlers
from exc2issue.core.issue_creator import process_error_collection
from exc2issue.core.registry import add_active_decorator
from exc2issue.core.signal_handling import setup_exit_handler, setup_signal_handlers
from exc2issue.observability import get_metrics_collector

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from exc2issue.adapters.gemini import GeminiClient
    from exc2issue.adapters.github import GitHubClient
    from exc2issue.adapters.vertexai import VertexAIClient
    from exc2issue.observability.metrics_collector import MetricsCollector


@dataclass
class _ExecutionState:
    """Track execution outcome for metrics and logging decisions."""

    start_time: float
    duration: float | None = None
    outcome: str | None = None
    exception: BaseException | None = None


class _ExecutionMonitor:
    """Context manager that orchestrates execution outcomes."""

    def __init__(
        self,
        decorator: "BugHunterDecorator",
        func: Callable[..., Any],
        collection: ErrorCollection,
        state: _ExecutionState,
    ) -> None:
        self._decorator = decorator
        self._func = func
        self._collection = collection
        self._state = state

    def __enter__(self) -> "_ExecutionMonitor":
        return self

    def on_success(self, result: Any) -> Any:
        """Handle successful execution and process collected errors."""
        self._state.duration = time.perf_counter() - self._state.start_time
        self._state.outcome = "success"

        if self._collection.has_errors():
            logger.warning(
                "Function completed with collected errors",
                extra={
                    "function": self._func.__name__,
                    "error_count": len(self._collection.errors),
                },
            )
            process_error_collection(self._decorator, self._collection)
        else:
            logger.debug(
                "Function completed successfully",
                extra={"function": self._func.__name__},
            )

        return result

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        _traceback: Any,
    ) -> Literal[False]:
        if exc is None:
            return False

        self._state.duration = time.perf_counter() - self._state.start_time
        self._state.exception = exc

        if isinstance(exc, SystemExit):
            self._state.outcome = "system_exit"
            logger.critical(
                "SystemExit caught",
                extra={
                    "function": self._func.__name__,
                    "exit_code": exc.code,
                },
            )
            handle_system_exit(exc, self._func, self._collection)
            process_error_collection(self._decorator, self._collection)
            return False

        if isinstance(exc, Exception):
            self._state.outcome = "error"
            logger.error(
                "Exception caught",
                extra={
                    "function": self._func.__name__,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                },
                exc_info=True,
            )
            self._decorator.consolidated_handlers.handle_exception(exc, self._func)
            process_error_collection(self._decorator, self._collection)

        return False


class _MetricsGuard:
    """Context manager that logs and suppresses metrics collector errors."""

    def __init__(self, func_name: str, collector_method: str) -> None:
        self._func_name = func_name
        self._collector_method = collector_method
        self.success = True

    def __enter__(self) -> "_MetricsGuard":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        _traceback: Any,
    ) -> bool:
        if exc is None:
            return False

        self.success = False
        logger.warning(
            "Metrics collection failed",
            extra={
                "function": self._func_name,
                "collector_method": self._collector_method,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            exc_info=True,
        )
        return True


class BugHunterDecorator:  # pylint: disable=too-many-instance-attributes
    """Bug hunter decorator with comprehensive error handling and resilience.

    This decorator provides complete error handling capabilities:
    1. Consolidated error handling for multiple related errors
    2. Multi-layered resilience for termination scenarios
    3. Configurable behavior through feature flags
    """

    def __init__(
        self,
        config: BugHunterConfig | None = None,
        repository: str | None = None,
        decorate_methods: list[str] | Literal["__all__"] | None = None,
        **kwargs: Any,
    ):
        """Initialize bug hunter decorator with comprehensive error handling.

        Args:
            config: Complete configuration object (preferred)
            repository: GitHub repository in format "owner/repo" (required if config not provided)
            decorate_methods: Controls which methods to decorate when applied to a class:
                            - None (default): Only __init__ is decorated (backward compatible)
                            - "__all__": All non-dunder methods are decorated
                            - List of names: Specific methods are decorated (e.g., ["process", "validate"])
                            - Supports wildcard patterns like "test_*" or "*_handler"
            **kwargs: Legacy parameters for backward compatibility
        """
        # Use provided config or create from legacy parameters
        if config is not None:
            self.config = config
        elif repository:
            # Create from repository and kwargs
            all_params = {"repository": repository, **kwargs}
            self.config = BugHunterConfig.create_legacy(**all_params)
        elif kwargs.get("repository"):
            # Create from kwargs only
            self.config = BugHunterConfig.create_legacy(**kwargs)
        else:
            raise ValueError("Repository is required for exc2issue decorator")

        # Store decorate_methods configuration
        self.decorate_methods: list[str] | Literal["__all__"] | None = decorate_methods

        # Initialize client attributes to avoid W0201, but don't create actual clients yet
        # Clients are created lazily when first accessed
        self._github_client: GitHubClient | None = None
        self._ai_client: GeminiClient | VertexAIClient | None = None

        # Instance tracking
        self._instance_id = str(uuid.uuid4())
        self._is_active = False
        self._error_collection_stack: list[ErrorCollection] = []  # Stack for nested calls
        self._active_depth = 0  # Track nesting depth for decorated method calls

        # Setup consolidated handlers
        self.consolidated_handlers = ConsolidatedHandlers(self)

        # Setup resilience mechanisms
        self._setup_resilience_mechanisms()

    # Backward compatibility properties
    @property
    def repository(self) -> str:
        """Get repository from config."""
        return self.config.repository

    @property
    def labels(self) -> list[str]:
        """Get labels from config."""
        return self.config.labels

    @property
    def assignees(self) -> list[str]:
        """Get assignees from config."""
        return self.config.assignees

    @property
    def auth_config(self) -> AuthConfig:
        """Get auth config."""
        return self.config.auth_config

    @property
    def processing_config(self) -> ProcessingConfig:
        """Get processing config."""
        return self.config.processing_config

    @property
    def consolidation_threshold(self) -> int:
        """Get consolidation threshold from processing config."""
        return self.config.processing_config.consolidation_threshold

    @property
    def enable_signal_handling(self) -> bool:
        """Get signal handling setting from processing config."""
        return self.config.processing_config.enable_signal_handling

    @property
    def enable_exit_handling(self) -> bool:
        """Get exit handling setting from processing config."""
        return self.config.processing_config.enable_exit_handling

    @property
    def enable_background_processing(self) -> bool:
        """Get background processing setting from processing config."""
        return self.config.processing_config.enable_background_processing

    @property
    def github_client(self) -> "GitHubClient":
        """Get GitHub client, creating it lazily if needed."""
        if self._github_client is None:
            self._github_client = create_github_client(
                self.config.auth_config.github_token
            )
        return self._github_client

    @property
    def ai_client(self) -> "GeminiClient | VertexAIClient | None":
        """Get AI client (VertexAI or Gemini), creating it lazily if needed.

        Uses create_ai_client() which prioritizes VertexAI over Gemini based on
        configuration. Returns None if no AI provider is configured.
        """
        if self._ai_client is None:
            self._ai_client = create_ai_client(
                gemini_api_key=self.config.auth_config.gemini_api_key,
                vertexai_project=self.config.auth_config.vertexai_project,
                vertexai_location=self.config.auth_config.vertexai_location,
            )
        return self._ai_client

    @property
    def gemini_client(self) -> "GeminiClient | VertexAIClient | None":
        """Get AI client (deprecated: use ai_client instead).

        This property is maintained for backward compatibility but now returns
        either a VertexAI or Gemini client based on configuration priority.
        """
        return self.ai_client

    # Public accessors for state management
    def is_active(self) -> bool:
        """Check if decorator is currently active."""
        return self._is_active

    def get_current_error_collection(self) -> ErrorCollection | None:
        """Get current error collection if available."""
        return self._error_collection_stack[-1] if self._error_collection_stack else None

    def _setup_resilience_mechanisms(self) -> None:
        """Setup signal handlers and exit handlers."""
        # Register this decorator
        add_active_decorator(self)

        # Setup global signal handlers (only once)
        if self.config.processing_config.enable_signal_handling:
            setup_signal_handlers()

        # Setup global exit handler (only once)
        if self.config.processing_config.enable_exit_handling:
            setup_exit_handler()

        # Ensure background worker is running
        if self.config.processing_config.enable_background_processing:
            ensure_background_worker()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorate the function or class with comprehensive error handling and resilience.

        For classes (e.g., Pydantic models), this wraps the __init__ method while
        preserving all class metadata including __annotations__ for proper type introspection.

        For functions, this wraps the function directly.
        """
        # Check if we're decorating a class
        if inspect.isclass(func):
            return self._wrap_class(func)
        return self._wrap_function(func)

    def _wrap_function(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap a function with comprehensive error handling and resilience."""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            """Execute decorated function with error handling, logging, and metrics.

            Metrics are collected for:
            - Duration (function execution time only, excludes error processing overhead)
            - Success (on successful completion)
            - Errors (on exceptions and SystemExit)
            """
            collector = get_metrics_collector()
            start_time = time.perf_counter()

            logger.debug(
                "Function execution started",
                extra={"function": func.__name__},
            )

            error_collection = ErrorCollection(
                function_name=func.__name__, args=args, kwargs=kwargs
            )

            # Track nesting depth and collection stack to handle nested decorated calls
            self._active_depth += 1
            self._error_collection_stack.append(error_collection)
            if self._active_depth == 1:
                # First (outermost) call - set active state
                self._is_active = True

            state = _ExecutionState(start_time=start_time)

            try:
                with ErrorCollectionContext(error_collection) as collection, \
                     _ExecutionMonitor(self, func, collection, state) as monitor:
                    result = func(*args, **kwargs)
                    return monitor.on_success(result)
            finally:
                self._finalize_execution(func.__name__, collector, state)
                # Decrement depth, pop collection, and clear state when exiting outermost call
                self._active_depth -= 1
                self._error_collection_stack.pop()
                if self._active_depth == 0:
                    self._is_active = False

        return wrapper

    def _should_decorate_method(  # pylint: disable=too-many-return-statements
        self, method_name: str, specified_methods: list[str] | Literal["__all__"] | None
    ) -> bool:
        """Determine if a method should be decorated based on configuration.

        Args:
            method_name: Name of the method to check
            specified_methods: Controls which methods to decorate

        Returns:
            True if the method should be decorated
        """
        # If None (default), only decorate __init__ for backward compatibility
        if specified_methods is None:
            return False

        # If empty list, only decorate __init__ (handled separately)
        if not specified_methods:
            return False

        # Handle explicit list of methods (including patterns)
        if isinstance(specified_methods, list):
            # Check if method name is in the list or matches a pattern
            for pattern in specified_methods:
                if self._matches_pattern(method_name, pattern):
                    # Method explicitly requested, allow even if private or dunder
                    return True
            # Not in explicit list, don't decorate
            return False

        # If "__all__", decorate all non-dunder, non-private methods
        if specified_methods == "__all__":
            # Skip dunder methods (except __init__ which is handled separately)
            if method_name.startswith("__") and method_name.endswith("__"):
                return False
            # Skip private methods (single underscore)
            if method_name.startswith("_"):
                return False
            # Decorate all other public methods
            return True

        return False

    def _matches_pattern(self, method_name: str, pattern: str) -> bool:
        """Check if method name matches a pattern (supports * wildcards).

        Args:
            method_name: Name of the method
            pattern: Pattern to match (e.g., "test_*", "*_handler", "exact_name")

        Returns:
            True if the method name matches the pattern
        """
        # Exact match
        if method_name == pattern:
            return True

        # Pattern matching with wildcards
        if "*" in pattern:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace("*", ".*")
            regex_pattern = f"^{regex_pattern}$"
            return re.match(regex_pattern, method_name) is not None

        return False

    def _get_methods_to_decorate(self, cls: type) -> list[tuple[str, Callable[..., Any]]]:
        """Get list of methods to decorate based on configuration.

        Args:
            cls: The class to inspect

        Returns:
            List of (method_name, method) tuples to decorate
        """
        methods_to_decorate = []

        # Always include __init__ first
        if hasattr(cls, "__init__"):
            methods_to_decorate.append(("__init__", getattr(cls, "__init__")))

        # If decorate_methods is None (default), only decorate __init__ for backward compatibility
        if self.decorate_methods is None:
            return methods_to_decorate

        # Get all methods from the class
        for name, obj in inspect.getmembers(cls):
            # Skip __init__ as we already handled it
            if name == "__init__":
                continue

            # Check if it's a method we should decorate
            # This includes:
            # - Regular Python functions/methods
            # - Static methods
            # - Class methods
            # - Method descriptors (from builtins like list.append, dict.get, etc.)
            is_method = (
                inspect.isfunction(obj) or
                inspect.ismethod(obj) or
                isinstance(obj, (staticmethod, classmethod)) or
                inspect.ismethoddescriptor(obj) or
                inspect.isbuiltin(obj)
            )

            if is_method and self._should_decorate_method(name, self.decorate_methods):
                methods_to_decorate.append((name, obj))

        return methods_to_decorate

    def _wrap_class(self, cls: type) -> type:
        """Wrap a class's methods while preserving all class metadata.

        This is crucial for Pydantic models and other classes that rely on
        type introspection, especially in Python 3.14+ with Pydantic 2.12+.

        Args:
            cls: The class to wrap

        Returns:
            The same class with its methods wrapped
        """
        # Get all methods to decorate
        methods_to_decorate = self._get_methods_to_decorate(cls)

        # Wrap each method
        for method_name, original_method in methods_to_decorate:
            if method_name == "__init__":
                wrapped = self._wrap_init_method(cls, original_method)
            else:
                wrapped = self._wrap_regular_method(cls, method_name, original_method)

            # Replace the method on the class
            setattr(cls, method_name, wrapped)

        # Return the class itself, not a wrapper - this preserves all class metadata
        # including __annotations__, __module__, __qualname__, etc.
        return cls

    def _wrap_init_method(self, cls: type, original_init: Callable[..., Any]) -> Callable[..., Any]:
        """Wrap a class's __init__ method with error handling.

        Args:
            cls: The class being decorated
            original_init: The original __init__ method

        Returns:
            Wrapped __init__ method
        """
        # Extract the underlying function from the method
        # cls.__init__ is a bound method (MethodType), so we need __func__ to get the function
        original_func = (
            original_init.__func__
            if hasattr(original_init, "__func__")
            else original_init
        )

        # Check if this is a builtin/descriptor (from C extensions)
        # These don't have __code__ attributes, so we handle them differently
        is_builtin = (
            inspect.ismethoddescriptor(original_func) or
            inspect.isbuiltin(original_func) or
            not hasattr(original_func, "__code__")
        )

        if is_builtin:
            # For builtin methods, we can't create a new function with modified __code__
            # Create a Python wrapper with qualified name for proper error tracking
            def qualified_builtin_init(*args: Any, **kwargs: Any) -> Any:
                return original_func(*args, **kwargs)
            qualified_builtin_init.__name__ = f"{cls.__name__}.__init__"
            qualified_builtin_init.__qualname__ = f"{cls.__qualname__}.__init__"
            init_with_qualified_name = qualified_builtin_init
        else:
            # Create a new function with the original code object but class-qualified name
            # This ensures error records have unique function names like "MyClass.__init__"
            # instead of just "__init__", preventing duplicate issue detection across classes
            # We use types.FunctionType to create a new function with original __code__
            # (for correct source info) but modified __name__ (for unique error tracking)
            original_func = cast(types.FunctionType, original_func)
            init_with_qualified_name = types.FunctionType(
                original_func.__code__,  # Use original code for correct source info
                original_func.__globals__,
                name=f"{cls.__name__}.__init__",  # Class-qualified name
                argdefs=getattr(original_func, "__defaults__", None),
                closure=getattr(original_func, "__closure__", None),
            )
            # Set __qualname__ separately as it's not a FunctionType parameter
            init_with_qualified_name.__qualname__ = f"{cls.__qualname__}.__init__"
            # Copy other attributes that functools.wraps would normally copy
            if hasattr(original_func, "__annotations__"):
                init_with_qualified_name.__annotations__ = original_func.__annotations__
            if hasattr(original_func, "__dict__"):
                init_with_qualified_name.__dict__.update(original_func.__dict__)

        @functools.wraps(original_init)
        def wrapped_init(instance: Any, *args: Any, **kwargs: Any) -> None:
            """Wrapped __init__ with error handling."""
            collector = get_metrics_collector()
            start_time = time.perf_counter()

            logger.debug(
                "Class initialization started",
                extra={"class": cls.__name__},
            )

            error_collection = ErrorCollection(
                function_name=f"{cls.__name__}.__init__", args=args, kwargs=kwargs
            )

            # Track nesting depth and collection stack to handle nested decorated calls
            self._active_depth += 1
            self._error_collection_stack.append(error_collection)
            if self._active_depth == 1:
                # First (outermost) call - set active state
                self._is_active = True

            state = _ExecutionState(start_time=start_time)

            try:
                # Pass init_with_qualified_name to monitor so func.__name__ is class-qualified
                with ErrorCollectionContext(error_collection) as collection, \
                     _ExecutionMonitor(self, init_with_qualified_name, collection, state) as monitor:
                    result = original_init(instance, *args, **kwargs)
                    monitor.on_success(result)
            finally:
                self._finalize_execution(f"{cls.__name__}.__init__", collector, state)
                # Decrement depth, pop collection, and clear state when exiting outermost call
                self._active_depth -= 1
                self._error_collection_stack.pop()
                if self._active_depth == 0:
                    self._is_active = False

        # Preserve the wrapped __init__'s annotations and other metadata
        # This is critical for Pydantic and other introspection-based libraries
        if hasattr(original_init, '__annotations__'):
            wrapped_init.__annotations__ = original_init.__annotations__.copy()

        return wrapped_init

    def _wrap_regular_method(  # pylint: disable=too-many-statements
        self, cls: type, method_name: str, original_method: Callable[..., Any]
    ) -> Any:
        """Wrap a regular class method (not __init__) with error handling.

        Args:
            cls: The class being decorated
            method_name: Name of the method
            original_method: The original method

        Returns:
            Wrapped method (may be a callable, staticmethod, or classmethod)
        """
        # Handle staticmethod and classmethod decorators
        # Note: Builtin classmethods (e.g., dict.fromkeys) are ClassMethodDescriptorType, not classmethod
        static_attr = inspect.getattr_static(cls, method_name)
        is_static = isinstance(static_attr, staticmethod)
        is_classmethod = isinstance(
            static_attr, (classmethod, types.ClassMethodDescriptorType)
        )

        # For builtin classmethods, store the descriptor for proper dispatch later
        original_classmethod_descriptor = (
            static_attr
            if is_classmethod and isinstance(static_attr, types.ClassMethodDescriptorType)
            else None
        )

        # Extract the underlying function
        if is_static or is_classmethod:
            # For static/class methods, the original_method is already the unwrapped function
            # Get it via __func__
            original_func = original_method.__func__ if hasattr(original_method, "__func__") else original_method
        else:
            # For regular methods
            original_func = (
                original_method.__func__
                if hasattr(original_method, "__func__")
                else original_method
            )

        # Check if this is a builtin/descriptor (from C extensions)
        is_builtin = (
            inspect.ismethoddescriptor(original_func) or
            inspect.isbuiltin(original_func) or
            not hasattr(original_func, "__code__")
        )

        if is_builtin:
            # For builtin methods, we can't create a new function with modified __code__
            # Create a Python wrapper with qualified name for proper error tracking
            def qualified_builtin_method(*args: Any, **kwargs: Any) -> Any:
                return original_func(*args, **kwargs)
            qualified_builtin_method.__name__ = f"{cls.__name__}.{method_name}"
            qualified_builtin_method.__qualname__ = f"{cls.__qualname__}.{method_name}"
            qualified_func = qualified_builtin_method
        else:
            # Create qualified name for error tracking
            original_func = cast(types.FunctionType, original_func)
            qualified_func = types.FunctionType(
                original_func.__code__,
                original_func.__globals__,
                name=f"{cls.__name__}.{method_name}",
                argdefs=getattr(original_func, "__defaults__", None),
                closure=getattr(original_func, "__closure__", None),
            )
            qualified_func.__qualname__ = f"{cls.__qualname__}.{method_name}"
            if hasattr(original_func, "__annotations__"):
                qualified_func.__annotations__ = original_func.__annotations__
            if hasattr(original_func, "__dict__"):
                qualified_func.__dict__.update(original_func.__dict__)

        if is_classmethod:
            # For classmethods, we need to handle wrapping differently
            # because the descriptor protocol adds cls automatically
            @functools.wraps(original_func)
            def wrapped_classmethod(clsarg: type, *args: Any, **kwargs: Any) -> Any:
                """Wrapped classmethod with error handling."""
                collector = get_metrics_collector()
                start_time = time.perf_counter()

                logger.debug(
                    "Class method execution started",
                    extra={"class": cls.__name__, "method": method_name},
                )

                error_collection = ErrorCollection(
                    function_name=f"{cls.__name__}.{method_name}", args=args, kwargs=kwargs
                )

                # Track nesting depth and collection stack to handle nested decorated calls
                self._active_depth += 1
                self._error_collection_stack.append(error_collection)
                if self._active_depth == 1:
                    # First (outermost) call - set active state
                    self._is_active = True

                state = _ExecutionState(start_time=start_time)

                try:
                    with ErrorCollectionContext(error_collection) as collection, \
                         _ExecutionMonitor(self, qualified_func, collection, state) as monitor:
                        # For builtin classmethods, use descriptor protocol to bind to correct class
                        if original_classmethod_descriptor is not None:
                            # Use __get__ to bind the descriptor to clsarg (the subclass)
                            # This ensures SubDict.fromkeys returns SubDict, not MyDict
                            # pylint: disable=unnecessary-dunder-call
                            bound_method = original_classmethod_descriptor.__get__(None, clsarg)
                            result = bound_method(*args, **kwargs)
                        else:
                            result = original_func(clsarg, *args, **kwargs)
                        return monitor.on_success(result)
                finally:
                    self._finalize_execution(f"{cls.__name__}.{method_name}", collector, state)
                    # Decrement depth, pop collection, and clear state when exiting outermost call
                    self._active_depth -= 1
                    self._error_collection_stack.pop()
                    if self._active_depth == 0:
                        self._is_active = False

            # Preserve annotations
            if hasattr(original_func, '__annotations__'):
                wrapped_classmethod.__annotations__ = original_func.__annotations__.copy()

            return classmethod(wrapped_classmethod)

        @functools.wraps(original_method)
        def wrapped_method(*args: Any, **kwargs: Any) -> Any:
            """Wrapped method with error handling."""
            collector = get_metrics_collector()
            start_time = time.perf_counter()

            logger.debug(
                "Method execution started",
                extra={"class": cls.__name__, "method": method_name},
            )

            error_collection = ErrorCollection(
                function_name=f"{cls.__name__}.{method_name}", args=args, kwargs=kwargs
            )

            # Track nesting depth and collection stack to handle nested decorated calls
            self._active_depth += 1
            self._error_collection_stack.append(error_collection)
            if self._active_depth == 1:
                # First (outermost) call - set active state
                self._is_active = True

            state = _ExecutionState(start_time=start_time)

            try:
                with ErrorCollectionContext(error_collection) as collection, \
                     _ExecutionMonitor(self, qualified_func, collection, state) as monitor:
                    result = original_method(*args, **kwargs)
                    return monitor.on_success(result)
            finally:
                self._finalize_execution(f"{cls.__name__}.{method_name}", collector, state)
                # Decrement depth, pop collection, and clear state when exiting outermost call
                self._active_depth -= 1
                self._error_collection_stack.pop()
                if self._active_depth == 0:
                    self._is_active = False

        # Preserve annotations
        if hasattr(original_method, '__annotations__'):
            wrapped_method.__annotations__ = original_method.__annotations__.copy()

        # Re-apply staticmethod decorator if needed
        if is_static:
            return staticmethod(wrapped_method)

        return wrapped_method

    def _finalize_execution(
        self,
        func_name: str,
        collector: "MetricsCollector | None",
        state: _ExecutionState,
    ) -> None:
        """Record metrics and log failures without interrupting execution."""
        if collector is None or state.duration is None or state.outcome is None:
            return

        with _MetricsGuard(func_name, "record_duration") as guard:
            collector.record_duration(func_name, state.duration)
        if not guard.success:
            return

        if state.outcome == "success":
            with _MetricsGuard(func_name, "record_success"):
                collector.record_success(func_name)
        elif state.outcome == "error" and state.exception is not None:
            with _MetricsGuard(func_name, "record_error"):
                collector.record_error(
                    func_name,
                    type(state.exception).__name__,
                    state.exception,
                )
        elif state.outcome == "system_exit" and state.exception is not None:
            with _MetricsGuard(func_name, "record_error"):
                collector.record_error(
                    func_name,
                    "SystemExit",
                    state.exception,
                )

    def handle_signal_termination(self, signum: int, frame: Any) -> None:
        """Handle signal-based termination by delegating to error handling module."""
        handle_signal_termination(self, signum, frame)

    def handle_exit_cleanup(self) -> None:
        """Handle exit cleanup by delegating to error handling module."""
        handle_exit_cleanup(self)

    def cleanup(self) -> None:
        """Clean up handlers and resources."""
        if hasattr(self, "consolidated_handlers"):
            self.consolidated_handlers.cleanup()

    def __del__(self) -> None:
        """Ensure cleanup on garbage collection."""
        with contextlib.suppress(Exception):
            self.cleanup()


def exc2issue(
    config: BugHunterConfig | None = None,
    decorate_methods: list[str] | Literal["__all__"] | None = None,
    **kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Bug hunter decorator with comprehensive error handling and resilience.

    This decorator provides comprehensive error handling and resilience:

    **Consolidated Error Handling:**
    - Collects multiple errors from single function execution
    - Creates single comprehensive GitHub issues for related errors
    - HYBRID logic: single errors use deterministic titles, multiple errors use consolidated format

    **Multi-Layered Resilience:**
    - Catches sys.exit() calls and creates GitHub issues
    - Handles signal termination (SIGTERM, SIGINT, SIGHUP)
    - Background processing with retry logic for reliable issue creation
    - Graceful cleanup and shutdown handling

    **Configurable Behavior:**
    - Feature flags to enable/disable specific resilience features
    - Adjustable consolidation threshold
    - Full backward compatibility

    **Class Method Decoration:**
    When applied to a class, the decorator can optionally wrap multiple methods:
    - If decorate_methods is None (default), only __init__ is decorated (backward compatible)
    - If decorate_methods is "__all__", all non-dunder methods are decorated
    - If decorate_methods is a list of method names, those specific methods are decorated
    - Supports wildcard patterns like "test_*" or "*_handler"

    Args:
        config: Complete configuration object (preferred)
        decorate_methods: Controls which methods to decorate when applied to a class:
                        - None (default): Only __init__ is decorated (backward compatible)
                        - "__all__": All non-dunder methods are decorated
                        - List of names: Specific methods are decorated
                        - Supports wildcard patterns like "test_*" or "*_handler"
        **kwargs: Legacy parameters for backward compatibility including:
            repository, labels, assignee, assignees, github_token, gemini_api_key,
            enable_signal_handling, enable_exit_handling, enable_background_processing,
            consolidation_threshold, auth_config, processing_config

    Returns:
        Decorated function that creates GitHub issues on various error/termination types

    Raises:
        ValueError: If neither config nor repository is provided

    Examples:
        # Only decorate __init__ (default, backward compatible)
        @exc2issue(repository="owner/repo")
        class MyClass:
            def __init__(self): ...
            def process(self): ...  # Not decorated

        # Decorate all methods
        @exc2issue(repository="owner/repo", decorate_methods="__all__")
        class MyClass:
            def process(self): ...  # Decorated
            def validate(self): ...  # Decorated

        # Decorate specific methods
        @exc2issue(repository="owner/repo", decorate_methods=["process", "validate"])
        class MyClass:
            def process(self): ...  # Decorated
            def validate(self): ...  # Decorated
            def helper(self): ...  # Not decorated

        # Use wildcard patterns
        @exc2issue(repository="owner/repo", decorate_methods=["test_*"])
        class MyTestClass:
            def test_feature(self): ...  # Decorated
            def test_edge_case(self): ...  # Decorated
            def setup(self): ...  # Not decorated
    """
    decorator_instance = BugHunterDecorator(
        config,
        decorate_methods=decorate_methods,
        **kwargs,
    )

    return decorator_instance
