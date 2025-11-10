"""
Runtime Pydantic Model Generator

This module creates Pydantic models at runtime based on MetaNode inheritance
while preserving the existing inheritance resolution logic.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

# Import Pydantic components
try:
    from pydantic import BaseModel, ConfigDict, Field, create_model
    from pydantic.fields import FieldInfo

    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = object

    def Field(*args, **kwargs):
        return None

    def create_model(*args, **kwargs):
        return None

    ConfigDict = dict
    FieldInfo = object
    PYDANTIC_AVAILABLE = False

# Import project components
from .meta import MetaNode, MetaPropertyType, PropValueType

if TYPE_CHECKING:
    from .element_store import ElementStore


class ModelGeneratorError(Exception):
    """Exception raised by ModelGenerator."""

    pass


class ModelGenerator:
    """Generates Pydantic models at runtime based on MetaNode inheritance."""

    def __init__(self, store: Optional["ElementStore"] = None):
        """Initialize the model generator.

        Args:
            store: ElementStore containing MetaNode definitions
        """
        self.store = store
        self._model_cache: Dict[str, Type[BaseModel]] = {}
        self._field_cache: Dict[str, Dict[str, Tuple[type, FieldInfo]]] = {}

    def generate_model(
        self, meta_node: MetaNode, model_name: Optional[str] = None
    ) -> Type[BaseModel]:
        """Generate a Pydantic model for a MetaNode with full inheritance resolution.

        Args:
            meta_node: The MetaNode to generate a model for
            model_name: Optional custom name for the generated model

        Returns:
            A Pydantic BaseModel class with all inherited properties and validation

        Raises:
            ModelGeneratorError: If Pydantic is not available or generation fails
        """
        if not PYDANTIC_AVAILABLE:
            raise ModelGeneratorError(
                "Pydantic is not available. Install pydantic>=2.0.0 to use runtime model generation."
            )

        # Use class_id as cache key
        cache_key = meta_node.class_id
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        # Generate model name
        if not model_name:
            model_name = f"{meta_node.class_id.title().replace('-', '').replace('_', '')}Properties"

        # Resolve all property types using existing MetaNode inheritance logic
        all_property_types = meta_node.all_prop_types

        # Convert MetaPropertyTypes to Pydantic field definitions
        field_definitions = self._convert_property_types_to_fields(all_property_types)

        # Create the Pydantic model
        try:
            if PYDANTIC_AVAILABLE:
                config = ConfigDict(
                    extra="allow",  # Allow dynamic properties
                    validate_assignment=True,  # Validate on assignment
                    arbitrary_types_allowed=True,  # Allow complex types
                    populate_by_name=True,  # Allow field aliases
                )

                model_class = create_model(
                    model_name, __config__=config, **field_definitions
                )
            else:
                # Fallback when Pydantic is not available
                model_class = None

            # Cache the generated model
            if model_class:
                self._model_cache[cache_key] = model_class

            return model_class

        except Exception as e:
            raise ModelGeneratorError(
                f"Failed to generate model for {meta_node.class_id}: {e}"
            )

    def _convert_property_types_to_fields(
        self, property_types: Dict[str, MetaPropertyType]
    ) -> Dict[str, Tuple[type, FieldInfo]]:
        """Convert MetaPropertyTypes to Pydantic field definitions.

        Args:
            property_types: Dictionary of property types from MetaNode

        Returns:
            Dictionary of field definitions for create_model
        """
        field_definitions = {}

        for key, prop_type in property_types.items():
            field_type, field_info = self._convert_single_property_type(prop_type)
            field_definitions[key] = (field_type, field_info)

        return field_definitions

    def _convert_single_property_type(
        self, prop_type: MetaPropertyType
    ) -> Tuple[type, FieldInfo]:
        """Convert a single MetaPropertyType to Pydantic field definition.

        Args:
            prop_type: The MetaPropertyType to convert

        Returns:
            Tuple of (field_type, FieldInfo) for the property
        """
        # Determine Python type
        python_type = self._get_python_type(prop_type)

        # Create field constraints
        field_kwargs = {}

        # Basic field info
        if prop_type.description:
            field_kwargs["description"] = prop_type.description

        # Handle default values
        if prop_type.default is not None:
            if callable(prop_type.default):
                # For callable defaults (like timestamp functions), set default_factory
                field_kwargs["default_factory"] = prop_type.default
            else:
                field_kwargs["default"] = prop_type.default
        elif not prop_type.required:
            field_kwargs["default"] = None

        # String constraints
        if prop_type.type == PropValueType.STRING and prop_type.regex:
            field_kwargs["pattern"] = prop_type.regex

        # Number constraints
        if prop_type.type == PropValueType.NUMBER:
            if prop_type.min is not None:
                field_kwargs["ge"] = prop_type.min
            if prop_type.max is not None:
                field_kwargs["le"] = prop_type.max

        # Array handling
        if prop_type.array:
            # Wrap the type in a List
            from typing import List

            python_type = List[python_type] if python_type != Any else List[Any]
            if not prop_type.required:
                python_type = Optional[python_type]
        elif not prop_type.required:
            # Make optional if not required
            python_type = Optional[python_type]

        # Create Field with constraints
        if field_kwargs:
            field_info = Field(**field_kwargs)
        else:
            # Use Ellipsis for required fields without constraints, None for optional
            field_info = Field(...) if prop_type.required else Field(None)

        return python_type, field_info

    def _get_python_type(self, prop_type: MetaPropertyType) -> type:
        """Get the Python type for a MetaPropertyType.

        Args:
            prop_type: The MetaPropertyType to get the type for

        Returns:
            The corresponding Python type
        """
        type_mapping = {
            PropValueType.STRING: str,
            PropValueType.NUMBER: Union[int, float],
            PropValueType.BOOLEAN: bool,
            PropValueType.DATE: str,  # ISO date string
            PropValueType.DATETIME: str,  # ISO datetime string
            PropValueType.JSON: Dict[str, Any],
            PropValueType.ELEMENT: str,  # Element ID as string
            PropValueType.ELEMENT_ARRAY: List[str],  # List of element IDs
            PropValueType.FUNCTION: Any,  # Functions can return anything
            PropValueType.OPTIONS: str,  # Selected option as string
            PropValueType.LISTITEM: Dict[str, Any],  # ListItem as dict
        }

        return type_mapping.get(prop_type.type, Any)

    def create_instance(self, meta_node: MetaNode, **data) -> BaseModel:
        """Create an instance of the generated model with data.

        Args:
            meta_node: The MetaNode to create a model instance for
            **data: The data to initialize the instance with

        Returns:
            An instance of the generated Pydantic model
        """
        model_class = self.generate_model(meta_node)
        return model_class(**data)

    def clear_cache(self) -> None:
        """Clear the model cache. Useful when MetaNode definitions change."""
        self._model_cache.clear()
        self._field_cache.clear()

    def get_cached_models(self) -> Dict[str, Type[BaseModel]]:
        """Get all cached models.

        Returns:
            Dictionary mapping class_id to generated model classes
        """
        return self._model_cache.copy()


# Global instance for easy access
_global_generator: Optional[ModelGenerator] = None


def get_model_generator(store: Optional["ElementStore"] = None) -> ModelGenerator:
    """Get the global ModelGenerator instance.

    Args:
        store: Optional ElementStore to use. If provided on first call, becomes the default.

    Returns:
        The global ModelGenerator instance
    """
    global _global_generator
    if _global_generator is None:
        _global_generator = ModelGenerator(store)
    elif store is not None and _global_generator.store != store:
        # Update the store if a different one is provided
        _global_generator.store = store
    return _global_generator


def generate_model_for_meta_node(
    meta_node: MetaNode, model_name: Optional[str] = None
) -> Type[BaseModel]:
    """Convenience function to generate a model for a MetaNode.

    Args:
        meta_node: The MetaNode to generate a model for
        model_name: Optional custom name for the generated model

    Returns:
        A Pydantic BaseModel class
    """
    generator = get_model_generator(meta_node.store)
    return generator.generate_model(meta_node, model_name)


def create_model_instance(meta_node: MetaNode, **data) -> BaseModel:
    """Convenience function to create a model instance for a MetaNode.

    Args:
        meta_node: The MetaNode to create a model instance for
        **data: The data to initialize the instance with

    Returns:
        An instance of the generated Pydantic model
    """
    generator = get_model_generator(meta_node.store)
    return generator.create_instance(meta_node, **data)
