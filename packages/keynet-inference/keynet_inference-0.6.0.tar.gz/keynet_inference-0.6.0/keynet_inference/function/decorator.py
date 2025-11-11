"""Decorators for serverless functions"""

import functools
import inspect
import threading
from typing import Any, Callable, Optional, TypeVar, cast

# Thread-local storage for tracking decorator usage
_context = threading.local()

F = TypeVar("F", bound=Callable[..., Any])


class UserInput(dict):
    """
    User input dictionary with environment variables excluded.

    This class extends dict and provides singleton access via class methods,
    allowing easy access to user input from anywhere in the decorated function.

    Attributes:
        All user-provided input parameters (environment variables excluded)

    Class Methods:
        get(key, default=None): Get value from current UserInput instance
        get_current(): Get current UserInput instance

    Example:
        @keynet_function("detection")
        def main(user_input):
            # Method 1: Direct access
            url = user_input["image_url"]

            # Method 2: From helper functions (singleton)
            process_image()

        def process_image():
            # Access from anywhere via singleton
            threshold = UserInput.get("threshold", 0.5)
            debug = UserInput.get("debug", False)

    """

    _context = threading.local()

    def __init__(self, original_args: dict):
        """
        Create UserInput from original args, excluding environment variables.

        Args:
            original_args: Original args dict containing both env vars and user input

        """
        from ..config import ENV_VAR_KEYS

        # Filter out environment variable keys
        user_data = {k: v for k, v in original_args.items() if k not in ENV_VAR_KEYS}
        super().__init__(user_data)

    @classmethod
    def get_current(cls) -> Optional["UserInput"]:
        """
        Get the current UserInput instance for this thread.

        Returns:
            Current UserInput instance, or None if not set

        """
        return getattr(cls._context, "current", None)

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get value from current UserInput instance (singleton access).

        This allows accessing user input from anywhere within the decorated function,
        including nested helper functions.

        Args:
            key: Key to retrieve
            default: Default value if key not found

        Returns:
            Value for the key, or default if not found

        Raises:
            RuntimeError: If UserInput is not initialized (not inside @keynet_function)

        Example:
            threshold = UserInput.get("threshold", 0.5)

        """
        current = cls.get_current()
        if current is None:
            raise RuntimeError(
                "UserInput is not initialized. "
                "Make sure you're inside a @keynet_function decorated function."
            )
        return dict.get(current, key, default)

    @classmethod
    def _set_current(cls, instance: "UserInput") -> None:
        """Set current UserInput instance (internal use only)."""
        cls._context.current = instance

    @classmethod
    def _clear_current(cls) -> None:
        """Clear current UserInput instance (internal use only)."""
        if hasattr(cls._context, "current"):
            del cls._context.current


def keynet_function(name: str) -> Callable[[F], F]:
    """
    Decorator to mark a function as a Keynet serverless function.

    This decorator must be applied to the main function to enable validation,
    packaging, and deployment through FunctionBuilder. Once applied to main,
    it enables usage in nested function calls.

    The decorated function must have exactly one parameter named 'args'.
    Environment variables are automatically loaded and UserInput singleton is set.

    Args:
        name: The name of the function (required)

    Returns:
        The decorated function

    Example:
        @keynet_function("my-serverless-function")
        def main(args):
            # Environment variables are automatically loaded from args.
            # Args can contain both env vars and function parameters:
            # {"MLFLOW_TRACKING_URI": "...", "image_url": "s3://..."}

            # Access user input via UserInput singleton (env vars excluded)
            image_url = UserInput.get("image_url")
            threshold = UserInput.get("threshold", 0.5)

            storage = Storage()  # Uses auto-loaded env vars
            return {"message": "Hello World"}

    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Function name must be a non-empty string")

    def decorator(func: F) -> F:
        # Validate function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # Must have exactly one parameter named 'args'
        if len(params) != 1 or params[0] != "args":
            raise ValueError(
                f"@keynet_function decorated function must have exactly one parameter "
                f"named 'args'. Found: {params}"
            )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Set context to indicate we're inside a keynet function
            is_root = not hasattr(_context, "inside_keynet_function")
            if is_root:
                _context.inside_keynet_function = True

            try:
                # Automatically load environment variables from args and create UserInput
                if args and len(args) > 0:
                    # Validate args[0] is a dict
                    if not isinstance(args[0], dict):
                        raise TypeError(
                            f"Expected 'args' parameter to be a dict, got {type(args[0]).__name__}"
                        )

                    # Load environment variables from args
                    from ..config import load_env

                    load_env(args[0])

                    # Create UserInput instance (env vars excluded)
                    user_input = UserInput(args[0])

                    # Set as singleton for thread-local access
                    UserInput._set_current(user_input)

                    # Call function with original args (not UserInput)
                    # User accesses input via UserInput.get() singleton
                    result = func(*args, **kwargs)
                    return result
                else:
                    # No args provided
                    result = func(*args, **kwargs)
                    return result
            finally:
                # Clear UserInput singleton
                UserInput._clear_current()

                # Clear context only if this was the root function
                if is_root and hasattr(_context, "inside_keynet_function"):
                    del _context.inside_keynet_function

        # Add metadata to the function
        wrapper._keynet_function = True  # type: ignore[attr-defined]
        wrapper._keynet_name = name  # type: ignore[attr-defined]

        return cast("F", wrapper)

    return decorator


def is_inside_keynet_function() -> bool:
    """
    Check if the current execution context is inside a keynet function.

    Returns:
        True if currently executing inside a function decorated with @keynet_function

    """
    return getattr(_context, "inside_keynet_function", False)


def get_function_metadata(func: Callable) -> Optional[dict[str, Any]]:
    """
    Get metadata for a keynet function.

    Args:
        func: The function to check

    Returns:
        Dictionary with metadata if the function is decorated, None otherwise

    """
    if hasattr(func, "_keynet_function") and getattr(func, "_keynet_function", False):
        return {"name": getattr(func, "_keynet_name", ""), "is_keynet_function": True}
    return None
