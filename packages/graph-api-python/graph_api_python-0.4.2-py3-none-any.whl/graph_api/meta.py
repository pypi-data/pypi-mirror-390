from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union
from weakref import WeakKeyDictionary

from .base_element import (
    BaseElement,
    ElementDetails,
    ElementProperties,
    NodeTypes,
)

if TYPE_CHECKING:
    from .element_store import ElementStore


class PropValueType(StrEnum):
    """Property value types using StrEnum for better performance."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    OPTIONS = "options"
    ELEMENT = "element"
    ELEMENT_ARRAY = "elementarray"
    FUNCTION = "function"
    JSON = "json"
    LISTITEM = "listitem"


@dataclass(frozen=True, slots=True)
class PropertyCondition:
    """Condition for property visibility/validation with immutability."""

    property: str
    operator: str
    value: List[Union[str, int, bool]]

    def __post_init__(self):
        """Validate condition after initialization."""
        if not self.property:
            raise ValueError("Property name is required")
        if not self.operator:
            raise ValueError("Operator is required")


@dataclass(frozen=True, slots=True)
class AgentTask:
    """Task configuration for AI agents with validation."""

    name: str
    agent_type: Optional[str] = None
    question: Any = None
    context: Optional[str] = None  # 'property' | 'element'
    skill_type: Optional[str] = None
    skill_tags: Optional[List[str]] = None
    skill_config: Optional[Any] = None
    skill_input: Optional[Any] = None

    def __post_init__(self):
        """Validate task configuration."""
        if not self.name:
            raise ValueError("Task name is required")
        if self.context and self.context not in ("property", "element"):
            raise ValueError("Context must be 'property' or 'element'")


@dataclass(slots=True)
class ListItem:
    """List item for listitem property type with dict-like access."""

    title: str
    value: str
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate list item."""
        if not self.title or not self.value:
            raise ValueError("Both title and value are required")

    def __getitem__(self, key: str) -> Any:
        """Get item value by key."""
        if key == "title":
            return self.title
        elif key == "value":
            return self.value
        return self.extra_data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item value by key."""
        if key == "title":
            object.__setattr__(self, "title", value)  # Bypass frozen if needed
        elif key == "value":
            object.__setattr__(self, "value", value)
        else:
            self.extra_data[key] = value


@dataclass(frozen=True, slots=True)
class PropertyRelation:
    """Property relation configuration with validation."""

    type: Optional[str] = None
    target: Optional[str] = None
    direction: Optional[str] = None  # 'in' | 'out' | 'both'

    def __post_init__(self):
        """Validate relation configuration."""
        if self.direction and self.direction not in ("in", "out", "both"):
            raise ValueError("Direction must be 'in', 'out', or 'both'")


@dataclass(frozen=True, slots=True)
class MonitorConfig:
    """Monitor configuration for properties."""

    enabled: bool = False


# Type alias for better readability
UniquePropertyValues = Dict[str, int]


def memoize_with_lru(maxsize: int = 128):
    """Enhanced memoization decorator using LRU cache."""

    def decorator(func: Callable) -> Callable:
        return lru_cache(maxsize=maxsize)(func)

    return decorator


# Weak cache for schema validators
schema_validator_cache: WeakKeyDictionary = WeakKeyDictionary()


@dataclass(slots=True)
class MetaPropertyType:
    """Represents a meta property type definition with comprehensive validation."""

    # Core required properties
    type: PropValueType
    label: str
    key: str

    # Optional properties with proper defaults
    hint: Optional[str] = None
    required: Optional[bool] = None
    readonly: Optional[bool] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    url_template: Optional[str] = None
    regex: Optional[str] = None

    # Options and lists
    options: Optional[List[str]] = None
    suggestions_list: Optional[str] = None
    labels: Optional[List[str]] = None
    list: Optional[List[ListItem]] = None

    # Relations and sections
    relation: Optional[PropertyRelation] = None
    section: Optional[str] = None
    card_section: Optional[str] = None  # 'header' | 'media' | 'content' | None
    inverse_title: Optional[str] = None

    # Grouping and elements
    can_group: Optional[bool] = None
    element_type: Optional[str] = None
    key_value: Optional[str] = None
    key_text: Optional[str] = None

    # Display and behavior
    hide: Optional[bool] = None
    group: Optional[str] = None
    linked: Optional[bool] = None
    default: Optional[Any] = None
    array: Optional[bool] = None
    prio: Optional[int] = None

    # Advanced features
    monitor: Optional[MonitorConfig] = None
    json_schema: Optional[Dict[str, Any]] = None
    tasks: Optional[List[AgentTask]] = None
    attributes: Optional[Dict[str, Any]] = None
    conditions: Optional[List[PropertyCondition]] = None
    legend: Optional[Dict[str, Any]] = None  # LegendConfig
    min: Optional[float] = None
    max: Optional[float] = None
    extra: Optional[bool] = None

    # Runtime calculated (not included in __init__)
    _unique: Optional[UniquePropertyValues] = field(
        default=None, init=False, repr=False
    )

    def __post_init__(self):
        """Initialize after dataclass construction with validation."""
        # Validate core fields
        if not self.key:
            raise ValueError("Property key is required")
        if not self.label:
            raise ValueError("Property label is required")

        # Set defaults
        if self.required is None:
            self.required = True
        if self.prio is None:
            self.prio = 4

        # Validate card_section
        if self.card_section and self.card_section not in (
            "header",
            "media",
            "content",
        ):
            raise ValueError("card_section must be 'header', 'media', or 'content'")


@dataclass
class FilterPreset:
    """Filter preset configuration."""

    id: str
    name: str
    filters: List[Any]  # IFluentOperation[]


@dataclass
class MetaSection:
    """Meta section configuration."""

    type: str
    name: Optional[str] = None
    properties: Optional[List[str]] = None
    component: Optional[str] = None
    title_template: Optional[str] = None
    template: Optional[str] = None


class MetaNodeProperties(ElementProperties):
    """Properties specific to MetaNode elements."""

    def __init__(self, **kwargs):
        """Initialize meta node properties with any keyword arguments."""
        super().__init__(**kwargs)

        # Set meta-specific attributes
        self.icon = kwargs.get("icon")
        self.type = kwargs.get("type")  # "node" | "edge"
        self.inherits_from = kwargs.get("inherits_from")
        self.target_source = kwargs.get("target_source")
        self.abstract = kwargs.get("abstract")
        self.readonly = kwargs.get("readonly")
        self.property_types = kwargs.get("property_types")
        self.sections = kwargs.get("sections")
        self.filter_presets = kwargs.get("filter_presets")
        self.storage = kwargs.get("storage")
        self.ttl_update = kwargs.get("ttl_update")
        self.ttl_creation = kwargs.get("ttl_creation")
        self.default_legend_property = kwargs.get("default_legend_property")


class MetaNodeDetails(ElementDetails):
    """Complete meta node data structure."""

    def __init__(self, **kwargs):
        """Initialize meta node details."""
        super().__init__(**kwargs)
        self.type = NodeTypes.META


@dataclass
class ValidationResult:
    """Result of schema validation."""

    valid: bool
    errors: Optional[List[Dict[str, Any]]] = None


def format_title(text: str) -> str:
    """Format text as title (capitalize first letter of each word)."""
    return " ".join(word.capitalize() for word in text.replace("_", " ").split())


def create_schema_with_validator(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Create schema with validator function."""

    # Simplified implementation - in real usage you'd use jsonschema
    def validate(data: Any) -> bool:
        # Basic validation logic here
        return True

    return {"schema": schema, "validate": validate}


def meta_node_to_json_schema(
    meta_node: "MetaNode", options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convert MetaNode to JSON Schema."""
    schema = {"type": "object", "properties": {}, "required": []}

    if not meta_node.properties.property_types:
        return schema

    max_prio = options.get("max_prio", 5) if options else 5

    for key, prop_type in meta_node.properties.property_types.items():
        if prop_type.prio and prop_type.prio > max_prio:
            continue

        prop_schema = {"type": "string"}  # Default type

        if prop_type.type == PropValueType.NUMBER:
            prop_schema["type"] = "number"
        elif prop_type.type == PropValueType.BOOLEAN:
            prop_schema["type"] = "boolean"
        elif prop_type.type == PropValueType.ELEMENT_ARRAY:
            prop_schema = {"type": "array", "items": {"type": "string"}}
        elif prop_type.type == PropValueType.JSON:
            prop_schema = prop_type.json_schema or {"type": "object"}

        if prop_type.description:
            prop_schema["description"] = prop_type.description

        schema["properties"][key] = prop_schema

        if prop_type.required:
            schema["required"].append(key)

    return schema


class MetaNode(BaseElement):
    """Extended MetaNode class for metadata definitions."""

    def __init__(
        self,
        data: Union[MetaNodeDetails, ElementDetails],
        store: Optional["ElementStore"] = None,
    ):
        """Initialize MetaNode."""
        super().__init__(data, store)

        # Override type to always be META
        self.type = NodeTypes.META

        # Private caches
        self._inherited_meta_nodes = None
        self._prop_types = None
        self._attributes = None
        self._inherited_properties = None

        # Setup inheritance
        self._setup_inheritance()

        # Initialize property types
        if (
            hasattr(self.properties, "property_types")
            and self.properties.property_types
        ):
            self._initialize_property_types()

        # Initialize attributes
        self._initialize_attributes()

    def _setup_inheritance(self) -> None:
        """Setup inheritance configuration."""
        # Ensure nodes inherit from 'node' type if needed
        properties_type = getattr(self.properties, "type", None)
        inherits_from = getattr(self.properties, "inherits_from", None)

        if properties_type == "node" and not inherits_from:
            if hasattr(self.properties, "inherits_from"):
                self.properties.inherits_from = ["node"]
            else:
                self.properties.inherits_from = ["node"]

    def _initialize_property_types(self) -> None:
        """Initialize property types with defaults."""
        property_types = getattr(self.properties, "property_types", None)
        if not property_types:
            return

        for key, pt in property_types.items():
            # Set defaults
            if not pt.key:
                pt.key = key
            if not pt.label:
                pt.label = format_title(key)
            if pt.required is None:
                pt.required = True
            if pt.prio is None:
                pt.prio = 4

            # Set elementType for element properties
            if pt.type == PropValueType.ELEMENT and not pt.element_type:
                pt.element_type = self.id

    def _initialize_attributes(self) -> None:
        """Initialize attributes with defaults."""
        if self.attributes is None:
            self.attributes = {}

        # Only apply defaults if no significant inheritance
        if not self._has_significant_inheritance():
            self._apply_default_card_attributes()

    def _has_significant_inheritance(self) -> bool:
        """Check if node has significant inheritance."""
        return bool(
            self.properties.inherits_from
            and len(self.properties.inherits_from) > 0
            and not (
                len(self.properties.inherits_from) == 1
                and self.properties.inherits_from[0] == "node"
            )
        )

    def _apply_default_card_attributes(self) -> None:
        """Apply default card attributes."""
        defaults = {
            "card:variant": "outlined",
            "card:density": "comfortable",
            "card:colorScheme": "primary",
            "card:sections": [
                {"type": "header", "properties": ["name"]},
                {"type": "content"},
            ],
        }

        for key, value in defaults.items():
            if key not in self.attributes:
                self.attributes[key] = value

    @property
    def all_attributes(self) -> Dict[str, Any]:
        """Get all attributes including inherited ones."""
        if self._attributes is None:
            self._attributes = self._gather_inherited_attributes()
        return self._attributes

    @property
    def all_prop_types(self) -> Dict[str, MetaPropertyType]:
        """Get all property types including inherited ones."""
        if self._prop_types is None:
            self._prop_types = self._gather_inherited_property_types()
        return self._prop_types

    @property
    def inherited_properties(self) -> MetaNodeProperties:
        """Get inherited properties from parent MetaNodes."""
        if self._inherited_properties is None:
            self._inherited_properties = self._gather_inherited_properties()
        return self._inherited_properties

    @property
    def default_legend_property(self) -> Optional[str]:
        """Get default legend property, respecting inheritance."""
        return self.inherited_properties.default_legend_property

    @property
    def color(self) -> Optional[str]:
        """Get color, respecting inheritance."""
        return self.inherited_properties.color

    @property
    def storage(self) -> Optional[str]:
        """Get storage setting, respecting inheritance."""
        return self.inherited_properties.storage

    @property
    def readonly(self) -> Optional[bool]:
        """Get readonly setting, respecting inheritance."""
        return self.inherited_properties.readonly

    @property
    def ttl_update(self) -> Optional[int]:
        """Get ttl_update setting, respecting inheritance."""
        return self.inherited_properties.ttl_update

    @property
    def ttl_creation(self) -> Optional[int]:
        """Get ttl_creation setting, respecting inheritance."""
        return self.inherited_properties.ttl_creation

    @property
    def default_properties(self) -> Dict[str, Any]:
        """Get properties that have default values defined."""
        defaults = {}
        prop_types = self.all_prop_types

        for key, prop_type in prop_types.items():
            if prop_type.default is not None:
                defaults[key] = prop_type.default

        return defaults

    @property
    def filterable_properties(self) -> List[MetaPropertyType]:
        """Get properties that can be used for filtering."""
        return [pt for pt in self.all_prop_types.values() if pt.prio and pt.prio < 2]

    @property
    def inherited_meta_nodes(self) -> List["MetaNode"]:
        """Get inherited meta nodes."""
        if self._inherited_meta_nodes is None:
            self._inherited_meta_nodes = self._calculate_inherited_meta_nodes()
        return self._inherited_meta_nodes

    def inherits_from(self, class_id: str) -> bool:
        """Check if this meta node inherits from given class_id."""
        return self.class_id == class_id or class_id in self.inherited_meta_nodes_names

    @property
    def inherited_meta_nodes_names(self) -> List[str]:
        """Get names of inherited meta nodes."""
        return [meta_node.id for meta_node in self.inherited_meta_nodes]

    @lru_cache(maxsize=64)
    def _calculate_inherited_meta_nodes(self) -> List["MetaNode"]:
        """Calculate inherited meta nodes recursively."""
        if not self.store:
            return []

        visited_nodes = set()
        inherited_meta_nodes = []

        def collect_inherited_nodes(node_ids: List[str]) -> None:
            for parent_id in node_ids:
                if parent_id in visited_nodes:
                    continue

                visited_nodes.add(parent_id)
                parent_meta_node = self.store.elements.get(parent_id)

                if parent_meta_node and isinstance(parent_meta_node, MetaNode):
                    inherited_meta_nodes.append(parent_meta_node)
                    if parent_meta_node.properties.inherits_from:
                        collect_inherited_nodes(
                            parent_meta_node.properties.inherits_from
                        )

        if self.properties.inherits_from:
            collect_inherited_nodes(self.properties.inherits_from)

        return inherited_meta_nodes

    def _gather_inherited_attributes(self) -> Dict[str, Any]:
        """Gather inherited attributes from parent nodes."""
        inherited_attributes = {}

        # Process inherited meta nodes and this node
        all_nodes = list(self.inherited_meta_nodes) + [self]

        for meta_node in all_nodes:
            if meta_node.attributes:
                for key, value in meta_node.attributes.items():
                    if key == "card:sections" and key in inherited_attributes and value:
                        # Merge card sections
                        sections_by_type = {}

                        # Add existing sections
                        for section in inherited_attributes[key]:
                            if isinstance(section, dict) and "type" in section:
                                sections_by_type[section["type"]] = section

                        # Process new sections
                        for section in value:
                            if isinstance(section, dict) and "type" in section:
                                section_type = section["type"]
                                if section_type in sections_by_type:
                                    # Merge sections of same type
                                    merged_section = {
                                        **sections_by_type[section_type],
                                        **section,
                                    }
                                    # Handle properties array specially
                                    if "properties" in section:
                                        existing_props = sections_by_type[
                                            section_type
                                        ].get("properties", [])
                                        merged_section["properties"] = list(
                                            set(existing_props + section["properties"])
                                        )
                                    sections_by_type[section_type] = merged_section
                                else:
                                    sections_by_type[section_type] = section

                        inherited_attributes[key] = list(sections_by_type.values())
                    else:
                        # Override other attributes
                        if (
                            key not in inherited_attributes
                            or inherited_attributes[key] != value
                        ):
                            inherited_attributes[key] = value

        return inherited_attributes

    @lru_cache(maxsize=128)
    def _gather_inherited_property_types(self) -> Dict[str, MetaPropertyType]:
        """Gather inherited property types from parent nodes."""
        all_nodes = list(self.inherited_meta_nodes) + [self]
        result = {}

        for meta_node in all_nodes:
            if meta_node.properties.property_types:
                result.update(meta_node.properties.property_types)

        return result

    @lru_cache(maxsize=64)
    def _gather_inherited_properties(self) -> MetaNodeProperties:
        """Gather inherited MetaNode properties from parent nodes."""
        all_nodes = list(self.inherited_meta_nodes) + [self]
        inheritable_props = [
            "icon",
            "description",
            "color",
            "storage",
            "readonly",
            "ttl_update",
            "ttl_creation",
            "default_legend_property",
        ]

        inherited_props = {}

        # Process nodes from most parent to most specific
        for meta_node in all_nodes:
            for prop in inheritable_props:
                value = getattr(meta_node.properties, prop, None)
                if value is not None:
                    inherited_props[prop] = value

        # Create new properties object with inherited values
        result_props = MetaNodeProperties(**vars(self.properties))
        for prop, value in inherited_props.items():
            setattr(result_props, prop, value)

        return result_props

    def set_default_properties(self, element: Optional[BaseElement] = None) -> None:
        """Set default properties for an element based on this MetaNode."""
        if not element:
            return

        props = self.all_prop_types
        for key, prop_type in props.items():
            if prop_type.default is not None and key not in element.properties:
                element.properties[key] = prop_type.default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper card attributes serialization."""
        result = super().to_dict()

        # Ensure card attributes are included
        if self.attributes:
            card_attributes = [
                "card:variant",
                "card:density",
                "card:colorScheme",
                "card:component",
                "card:sections",
            ]

            for attr in card_attributes:
                if attr in self.attributes:
                    if "attributes" not in result:
                        result["attributes"] = {}
                    result["attributes"][attr] = self.attributes[attr]

        return result

    def to_json_schema(
        self, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert MetaNode to JSON Schema."""
        return meta_node_to_json_schema(self, options)

    def validate(self, data: Any) -> ValidationResult:
        """Validate data against this MetaNode's JSON Schema."""
        # Use WeakKeyDictionary cache
        validator = schema_validator_cache.get(self)

        if validator is None:
            schema = self.to_json_schema()
            validator_result = create_schema_with_validator(schema)
            validator = validator_result["validate"]
            schema_validator_cache[self] = validator

        valid = validator(data)

        if not valid:
            # In real implementation, you'd get actual validation errors
            return ValidationResult(valid=False, errors=[])

        return ValidationResult(valid=True)

    def to_json_schema_with_validator(self) -> Dict[str, Any]:
        """Export MetaNode with JSON Schema validation functionality."""
        schema = self.to_json_schema()
        return create_schema_with_validator(schema)

    def reset_schema_validator(self) -> None:
        """Reset cached schema validator."""
        if self in schema_validator_cache:
            del schema_validator_cache[self]

    def reset_inheritance_caches(self) -> None:
        """Reset all cached inherited properties."""
        self._inherited_meta_nodes = None
        self._prop_types = None
        self._attributes = None
        self._inherited_properties = None
        self.reset_schema_validator()

    def calculate_unique_values(
        self, pt: Union[str, MetaPropertyType], force: bool = False
    ) -> None:
        """Calculate unique values for a property type."""
        if not self.store:
            return

        if isinstance(pt, str):
            if pt not in self.all_prop_types:
                return
            prop_type = self.all_prop_types[pt]
        else:
            prop_type = pt

        if not force and prop_type._unique is not None:
            return

        values = {}

        # Get all elements of this class
        elements = [el for el in self.store.elements.values() if el.class_id == self.id]

        # Count unique values
        for element in elements:
            if prop_type.key in element.properties:
                v = element.val(prop_type)
                if v is None:
                    continue

                if isinstance(v, str):
                    values[v] = values.get(v, 0) + 1
                elif isinstance(v, list):
                    for val in v:
                        if isinstance(val, str):
                            values[val] = values.get(val, 0) + 1

        prop_type._unique = values
