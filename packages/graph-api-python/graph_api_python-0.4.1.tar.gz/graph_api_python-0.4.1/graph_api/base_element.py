import hashlib
import time
import uuid
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

try:
    from pydantic import BaseModel, ConfigDict, Field

    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback for environments without Pydantic
    BaseModel = object

    def Field(*args, **kwargs):
        return None

    ConfigDict = dict
    PYDANTIC_AVAILABLE = False

if TYPE_CHECKING:
    from .element_store import ElementStore
    from .meta import MetaNode, MetaPropertyType, ValidationResult


class NodeTypes(StrEnum):
    """Node types enumeration using StrEnum for better performance."""

    NODE = "node"
    META = "meta"
    EDGE = "edge"


@dataclass(frozen=True, slots=True)
class DataContext:
    """Data context for element operations.

    Using frozen=True for immutability and slots=True for memory efficiency.
    """

    property: Optional[str] = None
    source_id: Optional[str] = None
    legend: Optional[Dict[str, Any]] = None
    dv: Optional[Any] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return self.extra_data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.extra_data[key] = value


PropertyValue = Any


if PYDANTIC_AVAILABLE:
    from collections.abc import MutableMapping

    class Props(BaseModel):
        """Pydantic-based properties that all elements can have.

        Uses Pydantic BaseModel for validation and serialization while maintaining
        backward compatibility with dict-like access patterns.
        """

        model_config = ConfigDict(
            extra="allow",  # Allow dynamic properties
            validate_assignment=True,  # Validate on assignment
            arbitrary_types_allowed=True,  # Allow complex types
            populate_by_name=True,  # Allow field aliases
        )

        # Core properties with validation
        name: Optional[str] = Field(
            None, min_length=0, max_length=200
        )  # Allow empty strings
        description: Optional[str] = Field(None, max_length=2000)
        tags: Optional[List[str]] = Field(None)
        created_time: Optional[Union[int, str]] = Field(None, ge=0)
        created_by: Optional[Union[str, int]] = Field(None)
        updated_time: Optional[Union[int, str]] = Field(None, ge=0)
        approved_time: Optional[Union[int, str]] = Field(None, ge=0)
        approved_by: Optional[Union[str, int]] = Field(None)
        start: Optional[Any] = Field(None)
        end: Optional[Any] = Field(None)
        original: Optional[Any] = Field(None)
        ttl_protect: Optional[bool] = Field(None)
        color: Optional[str] = Field(None)  # Remove strict color validation
        icon: Optional[str] = Field(None, min_length=1, max_length=100)

        def __init__(self, **kwargs) -> None:
            """Initialize with backward compatibility for dict-like creation."""
            # Don't set automatic timestamps unless explicitly empty to maintain test compatibility
            super().__init__(**kwargs)

        @property
        def extra_properties(self) -> Dict[str, Any]:
            """Access extra properties for backward compatibility."""
            return getattr(self, "__pydantic_extra__", {})

        @property
        def _KNOWN_ATTRS(self) -> frozenset:
            """Known attributes for backward compatibility."""
            return frozenset(self.__class__.model_fields.keys())

        # Dict-like interface for backward compatibility
        def __getitem__(self, key: str) -> PropertyValue:
            """Get property value by key (dict-like access)."""
            try:
                return getattr(self, key)
            except AttributeError:
                # Check extra properties
                extra = getattr(self, "__pydantic_extra__", {})
                if key in extra:
                    return extra[key]
                raise KeyError(key)

        def __setitem__(self, key: str, value: PropertyValue) -> None:
            """Set property value by key (dict-like access)."""
            # Check if this is a known model field
            if key in self.__class__.model_fields:
                try:
                    setattr(self, key, value)
                except ValueError:
                    raise
            else:
                # For unknown fields, store in extra properties
                if not hasattr(self, "__pydantic_extra__"):
                    object.__setattr__(self, "__pydantic_extra__", {})
                self.__pydantic_extra__[key] = value

        def __delitem__(self, key: str) -> None:
            """Delete property by key (dict-like access)."""
            if key in self.__class__.model_fields:
                setattr(self, key, None)
            else:
                extra = getattr(self, "__pydantic_extra__", {})
                if key in extra:
                    del extra[key]
                else:
                    raise KeyError(key)

        def __contains__(self, key: object) -> bool:
            """Check if property key exists (dict-like access)."""
            if isinstance(key, str):
                # Check if it's a model field and has a non-None value
                if key in self.__class__.model_fields:
                    return getattr(self, key) is not None
                # Check extra properties
                extra = getattr(self, "__pydantic_extra__", {})
                return key in extra
            return False

        def __iter__(self):
            """Iterate over all property keys (dict-like access)."""
            # Yield model fields that are not None
            for field_name in self.__class__.model_fields:
                if getattr(self, field_name) is not None:
                    yield field_name
            # Yield extra properties
            extra = getattr(self, "__pydantic_extra__", {})
            yield from extra

        def __len__(self) -> int:
            """Get number of properties (dict-like access)."""
            count = sum(
                1
                for field_name in self.__class__.model_fields
                if getattr(self, field_name) is not None
            )
            extra = getattr(self, "__pydantic_extra__", {})
            return count + len(extra)

        def get(self, key: str, default: Any = None) -> Any:
            """Get property with default value (dict-like access)."""
            try:
                return self[key]
            except KeyError:
                return default

        def update(self, other: Any) -> None:
            """Update properties from dict or another ElementProperties."""
            if hasattr(other, "items"):
                for key, value in other.items():
                    self[key] = value
            elif hasattr(other, "keys"):
                for key in other:
                    self[key] = other[key]
            else:
                # Try dict-like access
                for key, value in dict(other).items():
                    self[key] = value

        def items(self):
            """Get items (dict-like access)."""
            for key in self:
                yield key, self[key]

        def keys(self):
            """Get keys (dict-like access)."""
            return iter(self)

        def values(self):
            """Get values (dict-like access)."""
            for key in self:
                yield self[key]

    # Register with MutableMapping ABC
    MutableMapping.register(Props)

else:
    # Fallback to original implementation when Pydantic is not available
    class Props(MutableMapping):
        """Properties that all elements can have.

        Inherits from MutableMapping for dict-like behavior with better performance.
        Uses __slots__ for memory efficiency.
        """

        __slots__ = (
            "name",
            "description",
            "tags",
            "created_time",
            "created_by",
            "updated_time",
            "approved_time",
            "approved_by",
            "start",
            "end",
            "original",
            "ttl_protect",
            "color",
            "icon",
            "extra_properties",
            "_KNOWN_ATTRS",
        )

        def __init__(self, **kwargs) -> None:
            """Initialize properties with any keyword arguments."""
            # Known attributes for efficient lookup
            self._KNOWN_ATTRS = frozenset(
                {
                    "name",
                    "description",
                    "tags",
                    "created_time",
                    "created_by",
                    "updated_time",
                    "approved_time",
                    "approved_by",
                    "start",
                    "end",
                    "original",
                    "ttl_protect",
                    "color",
                    "icon",
                }
            )

            # Initialize core properties
            self.name: Optional[str] = None
            self.description: Optional[str] = None
            self.tags: Optional[List[str]] = None
            self.created_time: Optional[int] = None
            self.created_by: Optional[str] = None
            self.updated_time: Optional[int] = None
            self.approved_time: Optional[int] = None
            self.approved_by: Optional[str] = None
            self.start: Optional[Any] = None
            self.end: Optional[Any] = None
            self.original: Optional[Any] = None
            self.ttl_protect: Optional[bool] = None
            self.color: Optional[str] = None
            self.icon: Optional[str] = None
            self.extra_properties: Dict[str, Any] = {}

            # Set default timestamps
            current_time = int(time.time() * 1000)
            if kwargs.get("created_time") is None:
                kwargs["created_time"] = current_time
            if kwargs.get("updated_time") is None:
                kwargs["updated_time"] = current_time

            # Set properties from kwargs
            for key, value in kwargs.items():
                if key in self._KNOWN_ATTRS:
                    setattr(self, key, value)
                else:
                    self.extra_properties[key] = value

        def __getitem__(self, key: str) -> PropertyValue:
            """Get property value by key."""
            if key in self._KNOWN_ATTRS:
                return getattr(self, key)
            return self.extra_properties[key]

        def __setitem__(self, key: str, value: PropertyValue) -> None:
            """Set property value by key."""
            if key in self._KNOWN_ATTRS:
                setattr(self, key, value)
            else:
                self.extra_properties[key] = value

        def __delitem__(self, key: str) -> None:
            """Delete property by key."""
            if key in self._KNOWN_ATTRS:
                setattr(self, key, None)
            else:
                del self.extra_properties[key]

        def __iter__(self):
            """Iterate over all property keys."""
            # Yield known attributes that are not None
            for attr in self._KNOWN_ATTRS:
                if getattr(self, attr) is not None:
                    yield attr
            # Yield extra properties
            yield from self.extra_properties

        def __len__(self) -> int:
            """Get number of properties."""
            count = sum(
                1 for attr in self._KNOWN_ATTRS if getattr(self, attr) is not None
            )
            return count + len(self.extra_properties)

        def __contains__(self, key: object) -> bool:
            """Check if property key exists."""
            if isinstance(key, str):
                if key in self._KNOWN_ATTRS:
                    return getattr(self, key) is not None
                return key in self.extra_properties
            return False

        def get(self, key: str, default: Any = None) -> Any:
            """Get property with default value."""
            try:
                return self[key]
            except KeyError:
                return default


@dataclass(slots=True)
class ElementDetails:
    """Complete element data structure with slots for memory efficiency."""

    id: str
    class_id: str
    type: NodeTypes
    properties: Props
    to_id: Optional[str] = None
    from_id: Optional[str] = None
    source: Optional[str] = None
    temp: Optional[bool] = None
    attributes: Optional[Dict[str, Any]] = None
    flat: Optional[Dict[str, Any]] = None


class KG(MutableMapping[str, "BaseElement"]):
    """Knowledge Graph container - Python equivalent to TypeScript KG<T extends BaseElement>.

    Inherits from MutableMapping to provide full dict-like interface automatically.
    Uses proper generic typing for better type safety.
    """

    __slots__ = ("_elements",)

    def __init__(self) -> None:
        """Initialize KG container."""
        self._elements: Dict[str, BaseElement] = {}

    def __getitem__(self, key: str) -> "BaseElement":
        """Get element by ID."""
        return self._elements[key]

    def __setitem__(self, key: str, value: "BaseElement") -> None:
        """Set element by ID."""
        self._elements[key] = value

    def __delitem__(self, key: str) -> None:
        """Delete element by ID."""
        del self._elements[key]

    def __iter__(self):
        """Iterate over element IDs."""
        return iter(self._elements)

    def __len__(self) -> int:
        """Get number of elements."""
        return len(self._elements)

    def __repr__(self) -> str:
        """String representation of KG."""
        return f"KG({len(self._elements)} elements)"

    @property
    def elements(self) -> Dict[str, "BaseElement"]:
        """Access to internal elements dict for compatibility."""
        return self._elements


class BaseElementEventEmitter:
    """Simple event emitter for BaseElement with slots for memory efficiency."""

    __slots__ = ("_listeners",)

    def __init__(self) -> None:
        """Initialize event emitter."""
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event: str, listener: Callable) -> None:
        """Add event listener."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(listener)

    def emit(self, event: str, *args, **kwargs) -> None:
        """Emit event to all listeners."""
        if event in self._listeners:
            for listener in self._listeners[event]:
                listener(*args, **kwargs)

    def off(self, event: str, listener: Callable) -> None:
        """Remove event listener."""
        if event in self._listeners and listener in self._listeners[event]:
            self._listeners[event].remove(listener)


class BaseElement(BaseElementEventEmitter):
    """Base class for elements like nodes and edges with optimized memory usage."""

    __slots__ = (
        "id",
        "class_id",
        "type",
        "store",
        "to_id",
        "from_id",
        "source",
        "temp",
        "attributes",
        "flat",
        "embedded",
        "suggestions",
        "hash_",
        "properties",
        "_initialized",
    )

    def __init__(
        self, data: ElementDetails, store: Optional["ElementStore"] = None
    ) -> None:
        """Initialize BaseElement with type safety and validation."""
        super().__init__()

        # Core properties - validate required fields
        if not data.id:
            raise ValueError("Element ID is required")
        if not data.class_id:
            raise ValueError("Element class_id is required")

        self.id: str = data.id
        self.class_id: str = data.class_id
        self.type: NodeTypes = data.type
        self.store: Optional[ElementStore] = store

        # Optional properties with proper defaults
        self.to_id: Optional[str] = data.to_id
        self.from_id: Optional[str] = data.from_id
        self.source: Optional[str] = data.source
        self.temp: Optional[bool] = getattr(data, "temp", None)
        self.attributes: Optional[Dict[str, Any]] = data.attributes or {}
        self.flat: Optional[Dict[str, Any]] = data.flat or {}

        # Initialize other properties with proper types
        self.embedded: Optional[KG] = None
        self.suggestions: Optional[Dict[str, Any]] = None
        self.hash_: Optional[int] = None

        # Initialize properties with validation
        self.properties: Props = self._init_properties(data.properties)

        # Mark as initialized
        self._initialized: bool = False
        self._initialize_element()

    def set_store(self, store: "ElementStore") -> None:
        """Set the element store reference."""
        self.store = store

    async def complete_data(self) -> None:
        """Complete data initialization."""
        pass

    async def init(self) -> None:
        """Initialize element."""
        pass

    def _init_properties(self, properties: Optional[Props] = None) -> Props:
        """Initialize properties with defaults and validation."""
        if properties is None:
            properties = Props()

        # Set defaults with proper time handling - only if values are None
        current_time = int(time.time() * 1000)  # milliseconds
        if getattr(properties, "name", None) is None:
            properties.name = ""
        if getattr(properties, "created_time", None) is None:
            properties.created_time = current_time
        if getattr(properties, "updated_time", None) is None:
            properties.updated_time = current_time

        return properties

    def _generate_id(self, data_id: Optional[str] = None) -> str:
        """Generate ID if not provided with proper validation."""
        if data_id and data_id.strip():
            return data_id.strip()
        return f"{self.class_id}-{generate_guid()}"

    def _initialize_element(self) -> None:
        """Initialize element with provided data and prevent double initialization."""
        if not self._initialized:
            # Ensure attributes and flat are not None
            if self.attributes is None:
                self.attributes = {}
            if self.flat is None:
                self.flat = {}

            self._initialized = True

    def has_val(self, key: str) -> bool:
        """Check if element has a specific property value."""
        return key in self.properties

    def val(
        self,
        prop: Union[str, "MetaPropertyType"],
        link_element: Optional["BaseElement"] = None,
    ) -> PropertyValue:
        """Retrieve property value considering linked elements and special types."""

        if isinstance(prop, str):
            return self.properties.get(prop)

        # Handle MetaPropertyType
        if hasattr(prop, "linked") and prop.linked and link_element:
            element_details = link_element.properties.get("element_details", {})
            if isinstance(element_details, dict) and self.id in element_details:
                return element_details[self.id].get(prop.key)
            return None

        if hasattr(prop, "type"):
            if (
                prop.type == "options"
                and hasattr(prop, "labels")
                and hasattr(prop, "options")
            ):
                try:
                    idx = prop.options.index(self.properties.get(prop.key))
                    if 0 <= idx < len(prop.labels):
                        return prop.labels[idx]
                except (ValueError, AttributeError):
                    pass

            if prop.type == "number" and hasattr(prop, "list"):
                value = self.properties.get(prop.key)
                for item in prop.list:
                    if hasattr(item, "value") and item.value == value:
                        return getattr(item, "title", None)

            if prop.type == "function":
                if hasattr(self, prop.key) and callable(getattr(self, prop.key)):
                    return getattr(self, prop.key)()
                elif hasattr(self, prop.key):
                    return getattr(self, prop.key)

        return self.properties.get(prop.key)

    @property
    def meta_node(self) -> Optional["MetaNode"]:
        """Get the MetaNode that describes this BaseElement."""
        return self.store.get_meta_node_by_id(self.class_id) if self.store else None

    def set_default_properties(self) -> None:
        """Set default properties based on meta node."""
        if self.meta_node and hasattr(self.meta_node, "set_default_properties"):
            self.meta_node.set_default_properties(self)

    def validate_against_schema(self) -> "ValidationResult":
        """Validate element's properties against MetaNode's JSON schema.

        Returns:
            ValidationResult with valid=True/False and optional error list.
            Returns valid=True if meta_node is None (implicit pass when schema unavailable).
        """
        if not self.meta_node:
            # Import here to avoid circular dependency at module level
            from .meta import ValidationResult

            return ValidationResult(valid=True, errors=None)
        return self.meta_node.validate(self.properties)

    @property
    def is_valid_against_schema(self) -> bool:
        """Quick boolean check if element is valid against schema.

        Returns:
            True if validation passes or schema unavailable.
            False if validation fails.
        """
        return self.validate_against_schema().valid

    def to_dict(self) -> Dict[str, Any]:
        """Convert element to dictionary format."""
        return {
            "id": self.id,
            "type": self.type.value,
            "class_id": self.class_id,
            "from_id": self.from_id,
            "to_id": self.to_id,
            "properties": (
                self.properties.items()
                if hasattr(self.properties, "items")
                else dict(self.properties)
            ),
            "source": self.source,
            "attributes": self.attributes,
        }

    def mark_updated(self) -> None:
        """Update the updated_time property to current time."""
        self.properties.updated_time = int(time.time() * 1000)

    def update_properties(self, new_props: Dict[str, PropertyValue]) -> None:
        """Update properties and recalculate hash."""
        self.properties.update(new_props)
        self.hash_ = self.get_hash()
        self.emit("properties_updated")

    def get_property_elements(self, prop: str) -> List["BaseElement"]:
        """Get elements referenced by a property."""
        if prop in self.properties:
            prop_value = self.properties[prop]
            if isinstance(prop_value, list):
                elements = []
                for element_id in prop_value:
                    element = self.store.get_element(element_id) if self.store else None
                    if element:
                        elements.append(element)
                return elements
            else:
                element = self.store.get_element(prop_value) if self.store else None
                return [element] if element else []
        return []

    def get_element(self, prop: str) -> Optional["BaseElement"]:
        """Get single element referenced by a property."""
        if prop in self.properties:
            element_id = self.properties[prop]
            return self.store.get_element(element_id) if self.store else None
        return None

    def get_hash(self) -> int:
        """Generate hash for the element."""
        hash_string = f"{self.id}-{self.properties.get('updated_time')}-{self.properties.get('created_time')}-{self.source}"
        return int(
            hashlib.md5(hash_string.encode(), usedforsecurity=False).hexdigest(), 16
        ) % (2**31)

    def get_color(self, context: Optional[DataContext] = None) -> str:
        """Get color representation for the element."""
        if self.properties.color:
            return self.properties.color

        if not context or not context.property:
            return (
                getattr(self.meta_node.properties, "color", "#6baed6")
                if self.meta_node
                else "#6baed6"
            )

        # Handle property-based coloring
        property_type = None
        if isinstance(context.property, str):
            if self.meta_node and hasattr(self.meta_node.properties, "property_types"):
                property_type = self.meta_node.properties.property_types.get(
                    context.property
                )
        else:
            property_type = context.property

        if (
            not property_type
            or not hasattr(property_type, "key")
            or property_type.key not in self.properties
        ):
            return "#6baed6"

        legend = context.legend or getattr(property_type, "legend", None)
        if legend:
            # Would need to implement Legend.get_color equivalent
            # return Legend.get_color(legend, self.properties[property_type.key], property_type)
            pass

        return "#6baed6"

    def get_icon(self, context: Optional[DataContext] = None) -> str:
        """Get icon representation for the element."""
        if not context or not context.property:
            return (
                self.properties.get("icon")
                or (
                    getattr(self.meta_node.properties, "icon", None)
                    if self.meta_node
                    else None
                )
                or "mdi mdi-circle"
            )

        # Handle property-based icons
        return "mdi mdi-circle"

    def reset_connections(self) -> None:
        """Reset connections (placeholder for override)."""
        pass

    @staticmethod
    def get_element_hash(element: "BaseElement") -> int:
        """Generate hash for an element."""
        return element.get_hash()


def generate_guid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())


def generate_hash(text: str) -> int:
    """Generate hash from text."""
    return int(hashlib.md5(text.encode(), usedforsecurity=False).hexdigest(), 16) % (
        2**31
    )


# Backward compatibility alias
ElementProperties = Props
