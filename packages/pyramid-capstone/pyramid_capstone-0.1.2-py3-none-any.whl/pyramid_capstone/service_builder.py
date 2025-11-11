"""
Cornice service builder for type-hinted API views.

This module creates Cornice services dynamically from decorated functions,
handling validation, serialization, and integration with Pyramid.
"""

from typing import Any, Callable, Optional, Type

from cornice import Service
from marshmallow import Schema
from pyramid.config import Configurator

from .context import ParameterContext, validate_path_pattern
from .exceptions import ServiceRegistrationError
from .handler import create_view_handler
from .inspection import inspect_function_signature
from .schema_generator import generate_input_schema, generate_output_schema

# Registry keys for storing pending views and registered actions
PENDING_VIEWS_KEY = "api.pending_views"
REGISTERED_ACTIONS_KEY = "api.registered_actions"


def register_type_hinted_view(config: Configurator, func: Callable, method: str, path: str, **kwargs: Any) -> None:
    """
    Register a type-hinted view function as a Cornice service.

    This collects views by path and defers service creation until all views
    for a path are collected, allowing multiple HTTP methods per service.

    Args:
        config: Pyramid configurator
        func: Decorated function to register
        method: HTTP method (GET, POST, etc.)
        path: URL path pattern
        **kwargs: Additional service configuration
    """
    try:
        # Validate path pattern
        validate_path_pattern(path)

        # Filter out 'method' from kwargs to avoid conflicts
        filtered_kwargs = {k: v for k, v in kwargs.items() if k != "method"}

        # Get or create pending views registry
        registry = config.registry
        if not hasattr(registry, PENDING_VIEWS_KEY):
            setattr(registry, PENDING_VIEWS_KEY, {})
        if not hasattr(registry, REGISTERED_ACTIONS_KEY):
            setattr(registry, REGISTERED_ACTIONS_KEY, set())

        pending_views = getattr(registry, PENDING_VIEWS_KEY)
        registered_actions = getattr(registry, REGISTERED_ACTIONS_KEY)

        # Add this view to the pending registry
        if path not in pending_views:
            pending_views[path] = []

        pending_views[path].append((method, func, filtered_kwargs))

        # Register a callback to create services after all scanning is complete
        # Only register the action once per path
        if path not in registered_actions:
            registered_actions.add(path)
            config.action(
                discriminator=("api_service_creation", path),
                callable=_create_service_for_path,
                args=(config, path),
                order=-20,  # Execute before Cornice's internal actions
            )

    except Exception as e:
        raise ServiceRegistrationError(f"Failed to register view {func.__name__} for {method} {path}: {e}") from e


def _create_service_for_path(config: Configurator, path: str) -> None:
    """
    Create a single Cornice service for all methods registered to a path.

    Args:
        config: Pyramid configurator
        path: URL path pattern
    """
    registry = config.registry

    # Get pending views from registry
    if not hasattr(registry, PENDING_VIEWS_KEY):
        return

    pending_views = getattr(registry, PENDING_VIEWS_KEY)
    if path not in pending_views:
        return

    views = pending_views[path]
    if not views:
        return

    try:
        # Use the first view's kwargs as base configuration
        # (assuming all views for the same path have compatible config)
        base_kwargs = views[0][2] if views else {}

        # Create a single service for this path
        service_name = f"service_{path.replace('/', '_').replace('{', '').replace('}', '').strip('_')}"
        service = create_cornice_service(name=service_name, path=path, **base_kwargs)

        # Add all methods to this service
        for method, func, kwargs in views:
            # Inspect function signature
            signature = inspect_function_signature(func)

            # Create parameter context and validate
            context = ParameterContext(path)
            context.validate_no_conflicts(signature)

            # Generate schemas
            input_schema = generate_input_schema(signature, f"{func.__name__}InputSchema")
            output_schema = generate_output_schema(signature.return_type, f"{func.__name__}OutputSchema")

            # Create view handler
            view_handler = create_view_handler(
                original_func=func,
                signature=signature,
                context=context,
                input_schema=input_schema,
                output_schema=output_schema,
            )

            # Create validator for this specific view
            validators = []
            if input_schema:
                def make_validator(schema):
                    """Create a validator function for this schema."""
                    def validate_request(request, **kwargs):
                        """Validate request data using Marshmallow schema."""
                        try:
                            # Extract data based on request method
                            if request.method in ("POST", "PUT", "PATCH"):
                                data = request.json_body if request.content_type == "application/json" else dict(request.POST)
                            else:
                                data = dict(request.GET)

                            # Add path parameters
                            if hasattr(request, "matchdict") and request.matchdict:
                                data.update(request.matchdict)

                            # Validate using schema
                            schema_instance = schema()
                            validated_data = schema_instance.load(data)

                            # Store validated data on request (Cornice convention)
                            request.validated = validated_data

                        except Exception as e:
                            request.errors.add("body", "validation", str(e))
                    
                    return validate_request
                
                validators.append(make_validator(input_schema))

            # Prepare pycornmarsh predicates for OpenAPI documentation
            pcm_kwargs = _build_pycornmarsh_predicates(
                func=func,
                input_schema=input_schema,
                output_schema=output_schema,
                kwargs=kwargs
            )

            # Add this method to the service with its validators and pycornmarsh predicates
            service.add_view(
                method.upper(), 
                view_handler, 
                permission=kwargs.get("permission"),
                validators=tuple(validators) if validators else (),
                **pcm_kwargs
            )

        # Register the service with Pyramid
        config.add_cornice_service(service)

        # Clean up the pending views for this path
        del pending_views[path]

    except Exception as e:
        raise ServiceRegistrationError(f"Failed to create service for path {path}: {e}") from e


def create_cornice_service(name: str, path: str, **kwargs: Any) -> Service:
    """
    Create a Cornice service with the specified configuration.

    Args:
        name: Service name
        path: URL path pattern
        **kwargs: Additional service configuration

    Returns:
        Configured Cornice service
    """
    # Convert path pattern from {param} to Pyramid's {param} format
    # (they're already compatible, but we could add validation here)
    pyramid_path = path

    # Create the service
    service = Service(
        name=name,
        path=pyramid_path,
        description=kwargs.get("description", f"Service for {path}"),
        **{k: v for k, v in kwargs.items() if k != "description"},
    )

    return service


def add_validation_to_service(
    service: Service, input_schema: Optional[Type[Schema]], output_schema: Optional[Type[Schema]]
) -> None:
    """
    Add validation schemas to a Cornice service.

    Args:
        service: Cornice service to configure
        input_schema: Schema for request validation
        output_schema: Schema for response validation
    """
    if input_schema:
        # Add request validation
        def validate_request(request, **kwargs):
            """Validate request data using the input schema."""
            try:
                # Extract data based on request method
                if request.method in ("POST", "PUT", "PATCH"):
                    # For body methods, validate JSON body
                    data = request.json_body if request.content_type == "application/json" else dict(request.POST)
                else:
                    # For GET/DELETE, validate query parameters
                    data = dict(request.GET)

                # Add path parameters
                if hasattr(request, "matchdict") and request.matchdict:
                    data.update(request.matchdict)

                # Validate using schema
                schema_instance = input_schema()
                validated_data = schema_instance.load(data)

                # Store validated data on request for handler to use
                request.validated_data = validated_data

            except Exception as e:
                request.errors.add("body", "validation", str(e))

        service.add_validator(validate_request)

    if output_schema:
        # Add response validation/serialization
        def serialize_response(request, response):
            """Serialize response data using the output schema."""
            try:
                if hasattr(response, "json") and response.json:
                    schema_instance = output_schema()
                    serialized_data = schema_instance.dump(response.json)
                    response.json = serialized_data
            except Exception:
                # If serialization fails, let the original response through
                pass

        service.add_filter(serialize_response)


def convert_path_to_pyramid_route(path: str) -> str:
    """
    Convert a path pattern to Pyramid route format if needed.

    Args:
        path: Path pattern (e.g., '/users/{user_id}')

    Returns:
        Pyramid-compatible route pattern
    """
    # For now, the formats are compatible
    # This function exists for future compatibility if needed
    return path


def extract_service_metadata(func: Callable) -> dict:
    """
    Extract metadata from a decorated function for service configuration.

    Args:
        func: Decorated function

    Returns:
        Dictionary of service metadata
    """
    metadata = {}

    # Extract docstring for description
    if func.__doc__:
        metadata["description"] = func.__doc__.strip()

    # Extract any custom attributes set by decorators
    for attr_name in dir(func):
        if attr_name.startswith("__api_"):
            key = attr_name[7:]  # Remove '__api_' prefix
            metadata[key] = getattr(func, attr_name)

    return metadata


def _build_pycornmarsh_predicates(
    func: Callable,
    input_schema: Optional[Type[Schema]],
    output_schema: Optional[Type[Schema]],
    kwargs: dict,
) -> dict:
    """
    Build pycornmarsh predicates for OpenAPI documentation generation.

    Args:
        func: Original decorated function
        input_schema: Generated input schema (optional)
        output_schema: Generated output schema (optional)
        kwargs: Additional kwargs from the decorator

    Returns:
        Dictionary of pycornmarsh predicates to be added to the view
    """
    pcm_kwargs = {}

    # Add request schema if available
    # pycornmarsh expects pcm_request with schemas for different locations (body, querystring, etc.)
    if input_schema:
        pcm_kwargs["pcm_request"] = {"body": input_schema}

    # Add response schemas if available
    # pycornmarsh expects pcm_responses as a dict with status codes as keys
    if output_schema:
        # Handle ListSchemaInfo (for list return types)
        if hasattr(output_schema, "is_list_schema") and output_schema.is_list_schema:
            # For lists, pass the item schema with many=True
            pcm_kwargs["pcm_responses"] = {"200": output_schema.item_schema(many=True)}
        else:
            pcm_kwargs["pcm_responses"] = {"200": output_schema}

    # Add summary from docstring first line if available
    if func.__doc__:
        doc_lines = func.__doc__.strip().split("\n")
        if doc_lines:
            pcm_kwargs["pcm_summary"] = doc_lines[0].strip()
            # Add full docstring as description
            pcm_kwargs["pcm_description"] = func.__doc__.strip()

    # Add tags if provided in kwargs
    if "tags" in kwargs:
        pcm_kwargs["pcm_tags"] = kwargs["tags"] if isinstance(kwargs["tags"], list) else [kwargs["tags"]]

    # Add show version if provided (for versioned APIs)
    # Default to "v1" if not specified
    pcm_kwargs["pcm_show"] = kwargs.get("api_version", "v1")

    return pcm_kwargs
