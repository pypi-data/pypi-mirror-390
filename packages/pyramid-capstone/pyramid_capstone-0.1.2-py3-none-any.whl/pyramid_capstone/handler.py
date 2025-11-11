"""
Request handler that bridges Cornice services with type-hinted functions.

This module creates view handlers that extract parameters from requests,
call the original functions with proper type conversion, and handle responses.
"""

from typing import Any, Callable, Optional, Type

from marshmallow import Schema
from pyramid.request import Request

from .context import ParameterContext
from .exceptions import ParameterMissingError
from .inspection import FunctionSignature


def create_view_handler(
    original_func: Callable,
    signature: FunctionSignature,
    context: ParameterContext,
    input_schema: Optional[Type[Schema]],
    output_schema: Optional[Type[Schema]],
) -> Callable:
    """
    Create a view handler that bridges Cornice and the original function.

    Args:
        original_func: Original decorated function
        signature: Function signature information
        context: Parameter context for extraction
        input_schema: Schema for request validation (optional)
        output_schema: Schema for response serialization (optional)

    Returns:
        View handler function compatible with Cornice
    """

    def view_handler(request: Request) -> Any:
        """
        Handle the HTTP request by calling the original function.

        Args:
            request: Pyramid request object

        Returns:
            Response data (will be serialized by Cornice/Pyramid)
        """
        # Use validated data from Cornice (set by validators)
        # Cornice stores validated data in request.validated
        if hasattr(request, 'validated'):
            # Cornice has already validated - use the validated data
            function_args = {'request': request}
            function_args.update(request.validated)
        else:
            # Fallback: build arguments manually (for non-validated endpoints)
            function_args = context.build_function_arguments(request, signature)

        # Call the original function
        result = original_func(**function_args)

        # Handle the response
        return handle_response(result, output_schema, request)


    # Copy metadata from original function
    view_handler.__name__ = f"{original_func.__name__}_handler"
    view_handler.__doc__ = original_func.__doc__
    view_handler.__module__ = original_func.__module__

    return view_handler


def handle_response(result: Any, output_schema: Optional[Type[Schema]], request: Request) -> Any:
    """
    Handle the response from the original function.

    Args:
        result: Return value from the original function
        output_schema: Schema for response serialization (optional)
        request: Pyramid request object

    Returns:
        Processed response data
    """

    # If no result, return empty response
    if result is None:
        request.response.status_code = 204  # No Content
        return None

    # Always use schema serialization for consistency
    # If output schema is provided, serialize the result
    if output_schema:
        try:
            # Check if this is a list schema info (special case for lists)
            if hasattr(output_schema, "is_list_schema") and output_schema.is_list_schema:
                # Handle list serialization
                if isinstance(result, list):
                    item_schema_instance = output_schema.item_schema()
                    serialized_result = [item_schema_instance.dump(item) for item in result]
                    return serialized_result
                else:
                    return result
            else:
                # Handle regular schema serialization
                schema_instance = output_schema()
                serialized_result = schema_instance.dump(result)
                return serialized_result
        except Exception:
            # If serialization fails, return the raw result (e.g., error dictionaries)
            # This handles cases where we return error responses that don't match the expected schema
            return result

    # Return result as-is for basic types or when no schema
    return result


def create_error_handler(error_type: str) -> Callable:
    """
    Create a standardized error handler.

    Args:
        error_type: Type of error to handle

    Returns:
        Error handler function
    """

    def error_handler(request: Request, exception: Exception) -> dict:
        """Handle errors in a standardized way."""
        if error_type == "validation":
            request.response.status_code = 400
            return {"error": "Validation Error", "message": str(exception), "type": "validation_error"}
        elif error_type == "missing_parameter":
            request.response.status_code = 400
            return {"error": "Bad Request", "message": str(exception), "type": "missing_parameter"}
        else:
            request.response.status_code = 500
            return {"error": "Internal Server Error", "message": str(exception), "type": "internal_error"}

    return error_handler


def extract_validated_data(request: Request) -> dict:
    """
    Extract validated data from request (set by Cornice validators).

    Args:
        request: Pyramid request object

    Returns:
        Dictionary of validated data
    """
    # Check if Cornice has already validated and stored data
    if hasattr(request, "validated_data"):
        return request.validated_data

    # Fallback to extracting raw data
    data = {}

    # Add path parameters
    if hasattr(request, "matchdict") and request.matchdict:
        data.update(request.matchdict)

    # Add query parameters
    data.update(dict(request.GET))

    # Add body parameters for POST/PUT/PATCH
    if request.method in ("POST", "PUT", "PATCH"):
        if request.content_type == "application/json":
            try:
                json_data = request.json_body
                if isinstance(json_data, dict):
                    data.update(json_data)
            except (ValueError, TypeError):
                pass
        else:
            data.update(dict(request.POST))

    return data


def set_response_headers(request: Request, content_type: str = "application/json") -> None:
    """
    Set appropriate response headers.

    Args:
        request: Pyramid request object
        content_type: Content type for the response
    """
    request.response.content_type = content_type

    # Add CORS headers if needed (this could be configurable)
    request.response.headers["Access-Control-Allow-Origin"] = "*"
    request.response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    request.response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"


def create_options_handler() -> Callable:
    """
    Create a handler for OPTIONS requests (CORS preflight).

    Returns:
        OPTIONS request handler
    """

    def options_handler(request: Request) -> dict:
        """Handle OPTIONS requests for CORS."""
        set_response_headers(request)
        request.response.status_code = 200
        return {}

    return options_handler
