"""
Automatic Marshmallow schema generation from type hints.

This module converts Python type hints into Marshmallow schemas for
request validation and response serialization.
"""

from datetime import date, datetime
from enum import Enum
from typing import Optional, Type, get_args, get_origin

from marshmallow import Schema, fields, validate

from .exceptions import SchemaGenerationError
from .inspection import FunctionSignature, get_list_item_type, is_basic_type, is_list_type

# Mapping from Python types to Marshmallow fields
TYPE_TO_FIELD_MAPPING = {
    int: fields.Integer,
    float: fields.Float,
    str: fields.String,
    bool: fields.Boolean,
    bytes: fields.Raw,
    datetime: fields.DateTime,
    date: fields.Date,
}


def generate_input_schema(signature: FunctionSignature, schema_name: str = "InputSchema") -> Type[Schema]:
    """
    Generate a Marshmallow schema for request validation from function signature.

    Args:
        signature: Function signature information
        schema_name: Name for the generated schema class

    Returns:
        Marshmallow schema class for validating request parameters

    Raises:
        SchemaGenerationError: If schema generation fails
    """
    try:
        # Build schema fields from function parameters
        schema_fields = {}

        for param_name, param_info in signature.get_non_request_parameters().items():
            field = _create_field_from_type(param_info.type_hint, param_name)

            # Set field properties based on parameter info
            if param_info.has_default:
                field.default = param_info.default
                field.missing = param_info.default
                field.allow_none = param_info.default is None
            elif param_info.is_optional:
                field.allow_none = True
                field.missing = None
                field.default = None
            else:
                field.required = True

            schema_fields[param_name] = field

        # Create the schema class dynamically
        schema_class = type(schema_name, (Schema,), schema_fields)

        return schema_class

    except Exception as e:
        raise SchemaGenerationError(f"Failed to generate input schema: {e}") from e


def generate_output_schema(return_type: Type, schema_name: str = "OutputSchema") -> Optional[Type[Schema]]:
    """
    Generate a Marshmallow schema for response serialization from return type.

    Args:
        return_type: Function return type annotation
        schema_name: Name for the generated schema class

    Returns:
        Marshmallow schema class for serializing responses, or None if no schema needed

    Raises:
        SchemaGenerationError: If schema generation fails
    """
    if return_type is None:
        return None

    try:
        # Handle List types
        if is_list_type(return_type):
            item_type = get_list_item_type(return_type)
            if item_type and not is_basic_type(item_type):
                # Create schema for the item type
                item_schema = _create_schema_from_type(item_type, f"{schema_name}Item")

                # For list serialization, return a special marker that includes the item schema
                # We'll handle this in the handler
                class ListSchemaInfo:
                    def __init__(self, item_schema):
                        self.item_schema = item_schema
                        self.is_list_schema = True

                return ListSchemaInfo(item_schema)
            else:
                # List of basic types - no schema needed
                return None

        # Handle basic types
        if is_basic_type(return_type):
            return None  # No schema needed for basic types

        # Handle complex types (classes with annotations)
        return _create_schema_from_type(return_type, schema_name)

    except Exception as e:
        raise SchemaGenerationError(f"Failed to generate output schema for type {return_type}: {e}") from e


def _create_field_from_type(type_hint: Type, field_name: str) -> fields.Field:
    """
    Create a Marshmallow field from a type hint.

    Args:
        type_hint: Python type hint
        field_name: Name of the field for error messages

    Returns:
        Marshmallow field instance

    Raises:
        SchemaGenerationError: If type is not supported
    """
    # Handle Optional types
    origin = get_origin(type_hint)
    if origin is not None:
        args = get_args(type_hint)

        # Optional[T] -> Union[T, None]
        if len(args) == 2 and type(None) in args:
            inner_type = next(arg for arg in args if arg is not type(None))
            field = _create_field_from_type(inner_type, field_name)
            field.allow_none = True
            return field

        # List[T]
        elif is_list_type(type_hint):
            item_type = get_list_item_type(type_hint)
            if item_type:
                item_field = _create_field_from_type(item_type, f"{field_name}_item")
                return fields.List(item_field)
            else:
                return fields.List(fields.Raw())

    # Handle basic types
    if type_hint in TYPE_TO_FIELD_MAPPING:
        field_class = TYPE_TO_FIELD_MAPPING[type_hint]
        return field_class()

    # Handle Enum types
    if isinstance(type_hint, type) and issubclass(type_hint, Enum):
        # Use Marshmallow's built-in Enum field
        # by_value=True means we serialize/deserialize using the enum's value (not name)
        return fields.Enum(type_hint, by_value=True)

    # Handle complex types (classes with annotations)
    if hasattr(type_hint, "__annotations__"):
        nested_schema = _create_schema_from_type(type_hint, f"{field_name.title()}Schema")
        return fields.Nested(nested_schema)

    # Fallback to Raw field for unsupported types
    return fields.Raw()


def _create_schema_from_type(type_hint: Type, schema_name: str) -> Type[Schema]:
    """
    Create a Marshmallow schema from a type with annotations.

    Args:
        type_hint: Type with __annotations__ attribute
        schema_name: Name for the schema class

    Returns:
        Marshmallow schema class

    Raises:
        SchemaGenerationError: If schema creation fails
    """
    if not hasattr(type_hint, "__annotations__"):
        raise SchemaGenerationError(f"Type {type_hint} does not have annotations and cannot be converted to a schema")

    schema_fields = {}

    # Process each annotated field
    for field_name, field_type in type_hint.__annotations__.items():
        try:
            field = _create_field_from_type(field_type, field_name)
            schema_fields[field_name] = field
        except Exception as e:
            raise SchemaGenerationError(f"Failed to create field '{field_name}' of type {field_type}: {e}") from e

    # Add a custom dump method that handles both expected objects and arbitrary dictionaries
    def custom_dump(self, obj, **kwargs):
        # If obj is a dict and doesn't match our expected fields, return it as-is
        if isinstance(obj, dict):
            schema_field_names = set(self.fields.keys())
            obj_keys = set(obj.keys())

            # If the object has keys that don't match our schema fields,
            # it's probably an error response or other arbitrary dict
            if not obj_keys.issubset(schema_field_names):
                return obj

        # Otherwise, use normal Marshmallow serialization
        return super(schema_class, self).dump(obj, **kwargs)

    schema_fields["dump"] = custom_dump

    # Create the schema class
    schema_class = type(schema_name, (Schema,), schema_fields)

    return schema_class


def validate_schema_compatibility(type_hint: Type) -> None:
    """
    Validate that a type hint can be converted to a Marshmallow schema.

    Args:
        type_hint: Type hint to validate

    Raises:
        SchemaGenerationError: If type is not compatible
    """
    try:
        _create_field_from_type(type_hint, "test_field")
    except Exception as e:
        raise SchemaGenerationError(f"Type {type_hint} is not compatible with schema generation: {e}") from e
