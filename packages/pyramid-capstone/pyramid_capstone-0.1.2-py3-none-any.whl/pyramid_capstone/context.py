"""
Parameter context and dependency injection system.

This module provides pytest-style dependency injection for function parameters,
extracting values from different parts of the HTTP request (path, query, body).
"""

import re
from enum import Enum
from typing import Any, Dict, Set
from typing import List as ListType

from pyramid.request import Request

from .exceptions import ParameterConflictError, ParameterMissingError
from .inspection import FunctionSignature, ParameterInfo


class ParameterContext:
    """
    Manages parameter extraction and injection from HTTP requests.

    This class implements pytest-style dependency injection by building a context
    of available parameters from different request sources and matching them to
    function parameters.
    """

    def __init__(self, path_pattern: str) -> None:
        """
        Initialize parameter context.

        Args:
            path_pattern: URL path pattern (e.g., '/users/{user_id}')
        """
        self.path_pattern = path_pattern
        self.path_params = self._extract_path_parameters(path_pattern)

    def _extract_path_parameters(self, path_pattern: str) -> Set[str]:
        """
        Extract parameter names from path pattern.

        Args:
            path_pattern: URL path pattern with {param} placeholders

        Returns:
            Set of parameter names found in the path
        """
        # Find all {param_name} patterns in the path
        matches = re.findall(r"\{([^}]+)\}", path_pattern)
        return set(matches)

    def validate_no_conflicts(self, signature: FunctionSignature) -> None:
        """
        Validate that there are no parameter name conflicts at setup time.

        This method checks that no parameter name appears in multiple sources
        (path, query, body) which would create ambiguity.

        Args:
            signature: Function signature to validate

        Raises:
            ParameterConflictError: If conflicts are detected
        """
        # For now, we'll implement a simple strategy:
        # - Path parameters come from URL path
        # - Everything else comes from query params or request body
        # - Conflicts occur if a path param name matches a function param
        #   but the function param is expected to come from body/query

        function_params = set(signature.get_non_request_parameters().keys())
        path_params = self.path_params

        # Check if all path parameters are present in function signature
        missing_path_params = path_params - function_params
        if missing_path_params:
            raise ParameterConflictError(
                f"Path parameters {missing_path_params} are not present in function signature. "
                f"Function parameters: {function_params}"
            )

        # For now, we assume no conflicts since we have a clear hierarchy:
        # 1. Path parameters (from URL)
        # 2. Query parameters (from query string)
        # 3. Body parameters (from JSON body)
        # This will be expanded when we implement body parameter detection

    def extract_request_parameters(self, request: Request) -> Dict[str, Any]:
        """
        Extract all available parameters from the request.

        Args:
            request: Pyramid request object

        Returns:
            Dictionary mapping parameter names to values
        """
        context = {}

        # Extract path parameters (from URL matching)
        if hasattr(request, "matchdict") and request.matchdict:
            for param_name in self.path_params:
                if param_name in request.matchdict:
                    context[param_name] = request.matchdict[param_name]

        # Extract query parameters
        for key, value in request.params.items():
            if key not in context:  # Path params take precedence
                context[key] = value

        # Extract JSON body parameters (if present)
        # Check for JSON content type or if there's actual body content
        if (request.content_type and "application/json" in request.content_type) or (
            hasattr(request, "body") and request.body
        ):
            try:
                json_data = request.json_body
                if isinstance(json_data, dict):
                    for key, value in json_data.items():
                        if key not in context:  # Path and query params take precedence
                            context[key] = value
            except (ValueError, TypeError):
                # Invalid JSON or no JSON body - ignore
                pass

        return context

    def build_function_arguments(self, request: Request, signature: FunctionSignature) -> Dict[str, Any]:
        """
        Build function arguments by matching request parameters to function signature.

        Args:
            request: Pyramid request object
            signature: Function signature information

        Returns:
            Dictionary of function arguments ready to be passed to the function

        Raises:
            ParameterMissingError: If required parameters are missing
        """
        # Extract all available parameters from request
        available_params = self.extract_request_parameters(request)

        # Build function arguments
        function_args = {"request": request}  # Always include request

        # Process each function parameter
        for param_name, param_info in signature.get_non_request_parameters().items():
            if param_name in available_params:
                # Convert the parameter value to the expected type
                raw_value = available_params[param_name]
                converted_value = self._convert_parameter_value(raw_value, param_info, param_name)
                function_args[param_name] = converted_value
            elif param_info.has_default:
                # Use default value
                function_args[param_name] = param_info.default
            elif param_info.is_optional:
                # Optional parameter without value becomes None
                function_args[param_name] = None
            else:
                # Required parameter is missing
                raise ParameterMissingError(f"Required parameter '{param_name}' is missing from request")

        return function_args

    def _convert_parameter_value(self, raw_value: Any, param_info: ParameterInfo, param_name: str) -> Any:
        """
        Convert a raw parameter value to the expected type.

        Args:
            raw_value: Raw value from request (usually string)
            param_info: Parameter type information
            param_name: Parameter name for error messages

        Returns:
            Converted value

        Raises:
            ValueError: If conversion fails
        """
        target_type = param_info.inner_type  # Handle Optional types

        # If it's already the right type, return as-is
        if isinstance(raw_value, target_type):
            return raw_value

        # Handle Enum types
        if isinstance(target_type, type) and issubclass(target_type, Enum):
            try:
                # Try to convert string value to enum
                return target_type(raw_value)
            except ValueError:
                valid_values = [member.value for member in target_type]
                raise ValueError(
                    f"Invalid value '{raw_value}' for parameter '{param_name}'. "
                    f"Must be one of: {', '.join(str(v) for v in valid_values)}"
                )

        # Handle string conversion for basic types
        if isinstance(raw_value, str):
            try:
                if target_type is int:
                    return int(raw_value)
                elif target_type is float:
                    return float(raw_value)
                elif target_type is bool:
                    # Handle common boolean string representations
                    lower_value = raw_value.lower()
                    if lower_value in ("true", "1", "yes", "on"):
                        return True
                    elif lower_value in ("false", "0", "no", "off"):
                        return False
                    else:
                        raise ValueError(f"Cannot convert '{raw_value}' to boolean")
                elif target_type is str:
                    return raw_value
                elif target_type is bytes:
                    return raw_value.encode("utf-8")
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Cannot convert parameter '{param_name}' value '{raw_value}' to type {target_type.__name__}: {e}"
                ) from e

        # For complex types, we'll need more sophisticated conversion
        # This will be handled by the schema generation system
        return raw_value


def extract_path_parameters_from_pattern(path_pattern: str) -> ListType[str]:
    """
    Extract parameter names from a path pattern.

    Args:
        path_pattern: URL path pattern (e.g., '/users/{user_id}/posts/{post_id}')

    Returns:
        List of parameter names in order of appearance
    """
    matches = re.findall(r"\{([^}]+)\}", path_pattern)
    return matches


def validate_path_pattern(path_pattern: str) -> None:
    """
    Validate that a path pattern is well-formed.

    Args:
        path_pattern: URL path pattern to validate

    Raises:
        ValueError: If path pattern is invalid
    """
    if not path_pattern.startswith("/"):
        raise ValueError("Path pattern must start with '/'")

    # Check for balanced braces
    open_braces = path_pattern.count("{")
    close_braces = path_pattern.count("}")
    if open_braces != close_braces:
        raise ValueError("Unbalanced braces in path pattern")

    # Check for empty parameter names
    params = extract_path_parameters_from_pattern(path_pattern)
    for param in params:
        if not param.strip():
            raise ValueError("Empty parameter name in path pattern")
        if not param.isidentifier():
            raise ValueError(f"Invalid parameter name '{param}' - must be a valid Python identifier")
