"""
Comprehensive tests for graph_api.base_element module.
Tests KG, ElementProperties, ElementDetails, BaseElement classes and utility functions.
"""

from collections.abc import MutableMapping
from unittest.mock import Mock

import pytest

from graph_api.base_element import (
    KG,
    BaseElement,
    BaseElementEventEmitter,
    ElementDetails,
    ElementProperties,
    NodeTypes,
    Props,
    generate_guid,
)
from graph_api.element_store import ElementStore


class TestKG:
    """Test KG (Knowledge Graph) container class."""

    def test_kg_initialization(self):
        """Test KG creates empty container."""
        kg = KG()
        assert len(kg) == 0
        assert isinstance(kg, MutableMapping)
        assert hasattr(kg, "_elements")

    def test_kg_setitem_getitem(self):
        """Test setting and getting elements."""
        kg = KG()
        mock_element = Mock()
        mock_element.id = "test_id"

        kg["test_id"] = mock_element
        assert kg["test_id"] == mock_element
        assert len(kg) == 1

    def test_kg_delitem(self):
        """Test deleting elements."""
        kg = KG()
        mock_element = Mock()
        kg["test_id"] = mock_element

        del kg["test_id"]
        assert len(kg) == 0

        with pytest.raises(KeyError):
            _ = kg["test_id"]

    def test_kg_contains(self):
        """Test 'in' operator."""
        kg = KG()
        mock_element = Mock()
        kg["test_id"] = mock_element

        assert "test_id" in kg
        assert "nonexistent" not in kg

    def test_kg_iteration(self):
        """Test iterating over KG."""
        kg = KG()
        elements = {"id1": Mock(), "id2": Mock(), "id3": Mock()}

        for key, element in elements.items():
            kg[key] = element

        assert set(kg.keys()) == set(elements.keys())
        assert list(kg.values()) == list(elements.values())
        assert set(kg) == set(elements.keys())

    def test_kg_repr(self):
        """Test string representation."""
        kg = KG()
        kg["test"] = Mock()
        repr_str = repr(kg)
        assert "KG" in repr_str
        assert "1 elements" in repr_str


class TestElementProperties:
    """Test ElementProperties class with MutableMapping interface."""

    def test_properties_initialization_empty(self):
        """Test creating empty properties."""
        props = ElementProperties()
        assert len(props) == 0
        assert hasattr(props, "_KNOWN_ATTRS")
        assert hasattr(props, "extra_properties")

    def test_properties_initialization_with_kwargs(self):
        """Test creating properties with keyword arguments."""
        props = ElementProperties(name="Test", age=25, city="NYC", active=True)

        assert props["name"] == "Test"
        assert props["age"] == 25
        assert props["city"] == "NYC"
        assert props["active"] is True
        assert len(props) == 4

    def test_properties_known_attributes(self):
        """Test known attributes are handled correctly."""
        props = ElementProperties(
            name="Alice",
            description="Test person",
            tags=["tag1", "tag2"],
            created_time=1234567890,
        )

        # Known attributes should be set directly
        assert props.name == "Alice"
        assert props.description == "Test person"
        assert props.tags == ["tag1", "tag2"]
        assert props.created_time == 1234567890

        # Should be accessible via dict interface
        assert props["name"] == "Alice"
        assert props["description"] == "Test person"

    def test_properties_extra_attributes(self):
        """Test extra attributes go to extra_properties."""
        props = ElementProperties(
            name="Alice",  # Known attribute
            custom_field="custom_value",  # Extra attribute
        )

        assert props.name == "Alice"
        assert props["custom_field"] == "custom_value"
        assert "custom_field" in props.extra_properties
        assert props.extra_properties["custom_field"] == "custom_value"

    def test_properties_setitem_getitem(self):
        """Test dict-like access."""
        props = ElementProperties()

        # Set known attribute
        props["name"] = "Bob"
        assert props["name"] == "Bob"
        assert props.name == "Bob"

        # Set extra attribute
        props["custom"] = "value"
        assert props["custom"] == "value"
        assert "custom" in props.extra_properties

    def test_properties_delitem(self):
        """Test deleting properties."""
        props = ElementProperties(name="Alice", custom="value")

        # Delete known attribute
        del props["name"]
        assert props.name is None
        assert "name" not in props

        # Delete extra attribute
        del props["custom"]
        assert "custom" not in props
        assert "custom" not in props.extra_properties

    def test_properties_iteration(self):
        """Test iterating over properties."""
        props = ElementProperties(name="Alice", age=30, custom1="val1", custom2="val2")

        keys = list(props.keys())
        assert "name" in keys
        assert "age" in keys
        assert "custom1" in keys
        assert "custom2" in keys

        # Test values and items
        values = list(props.values())
        assert "Alice" in values
        assert 30 in values
        assert "val1" in values

        items = dict(props.items())
        assert items["name"] == "Alice"
        assert items["custom1"] == "val1"

    def test_properties_contains(self):
        """Test 'in' operator."""
        props = ElementProperties(name="Alice", custom="value")

        assert "name" in props
        assert "custom" in props
        assert "nonexistent" not in props

        # Test with None values - known attributes with None don't count as contained
        props = ElementProperties(name="Alice", description=None)
        assert "name" in props
        assert "description" not in props  # Known attribute with None value

        # But extra properties with None do count
        props["extra_none"] = None
        assert "extra_none" in props

    def test_properties_get_method(self):
        """Test get method with defaults."""
        props = ElementProperties(name="Alice")

        assert props.get("name") == "Alice"
        assert props.get("nonexistent") is None
        assert props.get("nonexistent", "default") == "default"


class TestElementDetails:
    """Test ElementDetails dataclass."""

    def test_element_details_creation(self):
        """Test creating ElementDetails."""
        props = ElementProperties(name="Test")
        details = ElementDetails(
            id="test_id", class_id="test_class", type=NodeTypes.NODE, properties=props
        )

        assert details.id == "test_id"
        assert details.class_id == "test_class"
        assert details.type == NodeTypes.NODE
        assert details.properties == props
        assert details.to_id is None
        assert details.from_id is None

    def test_element_details_with_optional_fields(self):
        """Test ElementDetails with all fields."""
        props = ElementProperties(name="Test")
        details = ElementDetails(
            id="test_id",
            class_id="test_class",
            type=NodeTypes.EDGE,
            properties=props,
            to_id="target",
            from_id="source",
            source="manual",
            temp=True,
            attributes={"key": "value"},
            flat={"flat_key": "flat_value"},
        )

        assert details.to_id == "target"
        assert details.from_id == "source"
        assert details.source == "manual"
        assert details.temp is True
        assert details.attributes == {"key": "value"}
        assert details.flat == {"flat_key": "flat_value"}


class TestBaseElementEventEmitter:
    """Test BaseElementEventEmitter class."""

    def test_event_emitter_initialization(self):
        """Test event emitter creates empty listeners."""
        emitter = BaseElementEventEmitter()
        assert hasattr(emitter, "_listeners")
        assert isinstance(emitter._listeners, dict)
        assert len(emitter._listeners) == 0

    def test_event_listener_registration(self):
        """Test adding event listeners."""
        emitter = BaseElementEventEmitter()
        mock_listener = Mock()

        emitter.on("test_event", mock_listener)
        assert "test_event" in emitter._listeners
        assert mock_listener in emitter._listeners["test_event"]

    def test_event_emission(self):
        """Test emitting events."""
        emitter = BaseElementEventEmitter()
        mock_listener1 = Mock()
        mock_listener2 = Mock()

        emitter.on("test_event", mock_listener1)
        emitter.on("test_event", mock_listener2)

        emitter.emit("test_event", "arg1", "arg2", kwarg1="value1")

        mock_listener1.assert_called_once_with("arg1", "arg2", kwarg1="value1")
        mock_listener2.assert_called_once_with("arg1", "arg2", kwarg1="value1")

    def test_event_listener_removal(self):
        """Test removing event listeners."""
        emitter = BaseElementEventEmitter()
        mock_listener = Mock()

        emitter.on("test_event", mock_listener)
        emitter.off("test_event", mock_listener)

        assert mock_listener not in emitter._listeners.get("test_event", [])

    def test_emit_nonexistent_event(self):
        """Test emitting event with no listeners."""
        emitter = BaseElementEventEmitter()
        # Should not raise exception
        emitter.emit("nonexistent_event", "arg")


class TestBaseElement:
    """Test BaseElement class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_store = Mock(spec=ElementStore)
        self.properties = ElementProperties(name="Test Element")
        self.details = ElementDetails(
            id="test_id",
            class_id="test_class",
            type=NodeTypes.NODE,
            properties=self.properties,
        )

    def test_base_element_initialization(self):
        """Test BaseElement initialization."""
        element = BaseElement(self.details, self.mock_store)

        assert element.id == "test_id"
        assert element.class_id == "test_class"
        assert element.type == NodeTypes.NODE
        assert element.store == self.mock_store
        assert element.properties == self.properties
        assert element.attributes == {}
        assert element.flat == {}

    def test_base_element_validation(self):
        """Test BaseElement validation."""
        # Test missing ID
        bad_details = ElementDetails(
            id="",  # Empty ID
            class_id="test_class",
            type=NodeTypes.NODE,
            properties=self.properties,
        )

        with pytest.raises(ValueError, match="Element ID is required"):
            BaseElement(bad_details, self.mock_store)

        # Test missing class_id
        bad_details2 = ElementDetails(
            id="test_id",
            class_id="",  # Empty class_id
            type=NodeTypes.NODE,
            properties=self.properties,
        )

        with pytest.raises(ValueError, match="Element class_id is required"):
            BaseElement(bad_details2, self.mock_store)

    def test_base_element_properties_initialization(self):
        """Test properties are properly initialized."""
        element = BaseElement(self.details, self.mock_store)

        # Test _init_properties method indirectly
        assert isinstance(element.properties, ElementProperties)
        assert element.properties["name"] == "Test Element"

    def test_base_element_optional_fields(self):
        """Test BaseElement with optional fields."""
        details = ElementDetails(
            id="test_id",
            class_id="test_class",
            type=NodeTypes.EDGE,
            properties=self.properties,
            to_id="target_id",
            from_id="source_id",
            source="test_source",
            temp=True,
            attributes={"attr1": "value1"},
            flat={"flat1": "value1"},
        )

        element = BaseElement(details, self.mock_store)

        assert element.to_id == "target_id"
        assert element.from_id == "source_id"
        assert element.source == "test_source"
        assert element.temp is True
        assert element.attributes == {"attr1": "value1"}
        assert element.flat == {"flat1": "value1"}

    def test_base_element_inheritance(self):
        """Test BaseElement inherits from BaseElementEventEmitter."""
        element = BaseElement(self.details, self.mock_store)

        # Should have event emitter capabilities
        assert hasattr(element, "on")
        assert hasattr(element, "emit")
        assert hasattr(element, "off")
        assert hasattr(element, "_listeners")

        # Test event functionality
        mock_listener = Mock()
        element.on("test", mock_listener)
        element.emit("test", "data")
        mock_listener.assert_called_once_with("data")


class TestUtilityFunctions:
    """Test utility functions."""

    def test_generate_guid(self):
        """Test GUID generation."""
        guid1 = generate_guid()
        guid2 = generate_guid()

        # Should be strings
        assert isinstance(guid1, str)
        assert isinstance(guid2, str)

        # Should be different
        assert guid1 != guid2

        # Should have reasonable length (UUID-like)
        assert len(guid1) > 10
        assert len(guid2) > 10

        # Test multiple generations
        guids = [generate_guid() for _ in range(10)]
        assert len(set(guids)) == 10  # All unique


class TestIntegration:
    """Integration tests for base_element components."""

    def test_kg_with_base_elements(self):
        """Test KG storing BaseElement instances."""
        kg = KG()
        mock_store = Mock(spec=ElementStore)

        # Create multiple elements
        for i in range(3):
            props = ElementProperties(name=f"Element {i}")
            details = ElementDetails(
                id=f"id_{i}",
                class_id="test_class",
                type=NodeTypes.NODE,
                properties=props,
            )
            element = BaseElement(details, mock_store)
            kg[f"id_{i}"] = element

        assert len(kg) == 3
        assert kg["id_1"].properties["name"] == "Element 1"

        # Test iteration
        element_names = [kg[key].properties["name"] for key in kg]
        assert "Element 0" in element_names
        assert "Element 2" in element_names

    def test_properties_with_various_types(self):
        """Test ElementProperties with different data types."""
        props = ElementProperties(
            name="test",  # Known attribute
            string_val="test",  # Extra attribute
            int_val=42,
            float_val=3.14,
            bool_val=True,
            list_val=[1, 2, 3],
            dict_val={"nested": "value"},
            none_val=None,
        )

        assert props["name"] == "test"
        assert props["string_val"] == "test"
        assert props["int_val"] == 42
        assert props["float_val"] == 3.14
        assert props["bool_val"] is True
        assert props["list_val"] == [1, 2, 3]
        assert props["dict_val"] == {"nested": "value"}

        # None values in extra properties are included
        assert "none_val" in props
        assert props["none_val"] is None
        assert len(props) == 8  # All properties including None


class TestPropsRename:
    """Test Props class (renamed from ElementProperties)."""

    def test_props_is_elementproperties(self):
        """Test that Props is the same as ElementProperties."""
        # Props should be an alias for ElementProperties
        assert Props is ElementProperties

        # Creating instances should be equivalent
        props1 = Props(name="test", value=42)
        props2 = ElementProperties(name="test", value=42)

        assert type(props1) == type(props2)
        assert props1["name"] == props2["name"]
        assert props1["value"] == props2["value"]

    def test_props_creation(self):
        """Test creating Props instances."""
        # Empty Props
        props = Props()
        assert len(props) == 0
        assert isinstance(props, MutableMapping)

        # Props with data
        props = Props(name="John", age=30, active=True)
        assert props["name"] == "John"
        assert props["age"] == 30
        assert props["active"] is True
        assert len(props) == 3

    def test_props_mutable_mapping_behavior(self):
        """Test Props behaves as MutableMapping."""
        props = Props(initial="value")

        # Getting/setting
        assert props["initial"] == "value"
        props["new_key"] = "new_value"
        assert props["new_key"] == "new_value"

        # Contains
        assert "initial" in props
        assert "new_key" in props
        assert "missing" not in props

        # Deletion
        del props["initial"]
        assert "initial" not in props
        assert len(props) == 1

        # Iteration
        keys = list(props.keys())
        values = list(props.values())
        items = list(props.items())

        assert "new_key" in keys
        assert "new_value" in values
        assert ("new_key", "new_value") in items

    def test_props_validation(self):
        """Test Props validation via Pydantic."""
        # Should allow extra fields (extra='allow')
        props = Props(name="test", unexpected_field="allowed")
        assert props["unexpected_field"] == "allowed"

        # Should handle various data types
        props = Props(
            string_val="text",
            int_val=42,
            float_val=3.14,
            bool_val=True,
            list_val=[1, 2, 3],
            dict_val={"nested": "data"},
            none_val=None,
        )

        assert all(
            key in props
            for key in [
                "string_val",
                "int_val",
                "float_val",
                "bool_val",
                "list_val",
                "dict_val",
                "none_val",
            ]
        )

    def test_props_backward_compatibility(self):
        """Test backward compatibility works correctly."""
        # Old code using ElementProperties should still work
        old_props = ElementProperties(name="old_style", version=1)

        # New code using Props should work identically
        new_props = Props(name="new_style", version=2)

        # Both should have the same interface
        assert hasattr(old_props, "__getitem__")
        assert hasattr(new_props, "__getitem__")
        assert hasattr(old_props, "__setitem__")
        assert hasattr(new_props, "__setitem__")

        # Both should be MutableMapping
        assert isinstance(old_props, MutableMapping)
        assert isinstance(new_props, MutableMapping)

        # Both should support the same operations
        old_props["dynamic"] = "added"
        new_props["dynamic"] = "added"

        assert old_props["dynamic"] == "added"
        assert new_props["dynamic"] == "added"


if __name__ == "__main__":
    pytest.main([__file__])
