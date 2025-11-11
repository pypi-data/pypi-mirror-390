"""
Function signature inspection utilities for type-hinted API.

This module provides tools to extract type hints from function signatures
and convert them into usable metadata for schema generation and validation.
"""

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, get_args, get_origin, get_type_hints


@dataclass
class ParameterInfo:
    """Information about a function parameter."""

    name: str
    type_hint: Type
    default: Any
    has_default: bool

    @property
    def is_optional(self) -> bool:
        """Check if parameter is Optional (Union[T, None])."""
        origin = get_origin(self.type_hint)
        if origin is not None:
            args = get_args(self.type_hint)
            return len(args) == 2 and type(None) in args
        return False

    @property
    def inner_type(self) -> Type:
        """Get the inner type for Optional types, or the type itself."""
        if self.is_optional:
            args = get_args(self.type_hint)
            return next(arg for arg in args if arg is not type(None))
        return self.type_hint


@dataclass
class FunctionSignature:
    """Complete signature information for a function."""

    parameters: Dict[str, ParameterInfo]
    return_type: Optional[Type]
    has_request_param: bool

    def get_non_request_parameters(self) -> Dict[str, ParameterInfo]:
        """Get all parameters except the request parameter."""
        return {name: param for name, param in self.parameters.items() if name != "request"}

    def get_required_parameters(self) -> Dict[str, ParameterInfo]:
        """Get parameters that are required (no default value and not optional)."""
        return {
            name: param
            for name, param in self.get_non_request_parameters().items()
            if not param.has_default and not param.is_optional
        }

    def get_optional_parameters(self) -> Dict[str, ParameterInfo]:
        """Get parameters that are optional (have default or are Optional type)."""
        return {
            name: param
            for name, param in self.get_non_request_parameters().items()
            if param.has_default or param.is_optional
        }


def inspect_function_signature(func: Callable) -> FunctionSignature:
    """
    Extract type hints and parameter information from a function signature.

    Args:
        func: Function to inspect

    Returns:
        FunctionSignature with complete parameter and return type information

    Raises:
        ValueError: If function signature is invalid for type-hinted API
    """
    # Get function signature
    sig = inspect.signature(func)

    # Get type hints (this resolves string annotations)
    try:
        type_hints = get_type_hints(func)
    except (NameError, AttributeError) as e:
        raise ValueError(
            f"Could not resolve type hints for function {func.__name__}: {e}. "
            "Make sure all types are properly imported."
        ) from e

    # Extract parameters
    parameters: Dict[str, ParameterInfo] = {}
    has_request_param = False

    for param_name, param in sig.parameters.items():
        # Check if this is the request parameter
        if param_name == "request":
            has_request_param = True
            # Skip request parameter in our analysis
            continue

        # Get type hint for this parameter
        param_type = type_hints.get(param_name)
        if param_type is None:
            raise ValueError(f"Parameter '{param_name}' in function {func.__name__} must have a type hint")

        # Check for default value
        has_default = param.default is not inspect.Parameter.empty
        default_value = param.default if has_default else None

        parameters[param_name] = ParameterInfo(
            name=param_name, type_hint=param_type, default=default_value, has_default=has_default
        )

    # Extract return type
    return_type = type_hints.get("return")

    # Validate that we have a request parameter
    if not has_request_param:
        raise ValueError(f"Function {func.__name__} must have a 'request' parameter as the first argument")

    return FunctionSignature(parameters=parameters, return_type=return_type, has_request_param=has_request_param)


def is_list_type(type_hint: Type) -> bool:
    """Check if a type hint represents a List type."""
    origin = get_origin(type_hint)
    return origin is list or origin is List


def get_list_item_type(type_hint: Type) -> Optional[Type]:
    """Get the item type from a List type hint."""
    if is_list_type(type_hint):
        args = get_args(type_hint)
        return args[0] if args else None
    return None


def is_basic_type(type_hint: Type) -> bool:
    """Check if a type hint is a basic Python type that we can handle directly."""
    from datetime import date, datetime

    basic_types = {int, float, str, bool, bytes, dict, list, datetime, date}
    return type_hint in basic_types


def validate_type_compatibility(type_hint: Type, param_name: str) -> None:
    """
    Validate that a type hint is compatible with our schema generation system.

    Args:
        type_hint: Type hint to validate
        param_name: Parameter name for error messages

    Raises:
        ValueError: If type is not supported
    """
    # Import Any here to avoid circular imports
    from typing import Any

    # Allow Any type (we're permissive with unknown types)
    if type_hint is Any:
        return

    # Handle Optional types
    if get_origin(type_hint) is not None:
        args = get_args(type_hint)
        # For Optional[T], validate the inner type
        if len(args) == 2 and type(None) in args:
            inner_type = next(arg for arg in args if arg is not type(None))
            return validate_type_compatibility(inner_type, param_name)
        # For List[T], validate the item type
        elif is_list_type(type_hint):
            item_type = get_list_item_type(type_hint)
            if item_type:
                return validate_type_compatibility(item_type, param_name)

    # Check if it's a basic type
    if is_basic_type(type_hint):
        return

    # Check if it has __annotations__ (likely a dataclass or similar)
    if hasattr(type_hint, "__annotations__"):
        return

    # If we get here, it's not a supported type
    raise ValueError(
        f"Type {type_hint} for parameter '{param_name}' is not supported. "
        "Supported types: int, float, str, bool, bytes, List[T], Optional[T], Any, "
        "and classes with type annotations (dataclasses, etc.)"
    )
