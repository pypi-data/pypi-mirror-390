"""
Comprehensive tests for graph_api.edge module.
Tests EdgeProperties, EdgeDetails, and Edge classes.
"""

from unittest.mock import Mock

import pytest

from graph_api.base_element import ElementProperties, NodeTypes
from graph_api.edge import Edge, EdgeDetails, EdgeProperties
from graph_api.element_store import ElementStore


class TestEdgeProperties:
    """Test EdgeProperties class."""

    def test_edge_properties_inheritance(self):
        """Test EdgeProperties inherits from ElementProperties."""
        props = EdgeProperties()
        assert isinstance(props, ElementProperties)
        assert hasattr(props, "extra_properties")
        assert hasattr(props, "_KNOWN_ATTRS")

    def test_edge_properties_with_kwargs(self):
        """Test EdgeProperties accepts arbitrary kwargs."""
        props = EdgeProperties(
            name="Connection", weight=5.0, type="friendship", created_at="2023-01-01"
        )

        assert props["name"] == "Connection"
        assert props["weight"] == 5.0
        assert props["type"] == "friendship"
        assert props["created_at"] == "2023-01-01"
        assert len(props) == 4

    def test_edge_properties_empty(self):
        """Test empty EdgeProperties."""
        props = EdgeProperties()
        assert len(props) == 0


class TestEdgeDetails:
    """Test EdgeDetails dataclass."""

    def test_edge_details_required_fields(self):
        """Test EdgeDetails with required fields."""
        props = EdgeProperties(name="Test Edge")
        details = EdgeDetails(
            id="edge_1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=props,
            from_id="source_node",
            to_id="target_node",
        )

        assert details.id == "edge_1"
        assert details.class_id == "connection"
        assert details.type == NodeTypes.EDGE
        assert details.properties == props
        assert details.from_id == "source_node"
        assert details.to_id == "target_node"

    def test_edge_details_with_optional_fields(self):
        """Test EdgeDetails with all fields."""
        props = EdgeProperties(weight=1.0)
        details = EdgeDetails(
            id="edge_1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=props,
            from_id="source_node",
            to_id="target_node",
            source="manual",
            temp=True,
            attributes={"attr1": "value1"},
            flat={"flat1": "value1"},
        )

        assert details.source == "manual"
        assert details.temp is True
        assert details.attributes == {"attr1": "value1"}
        assert details.flat == {"flat1": "value1"}

    def test_edge_details_post_init_validation(self):
        """Test EdgeDetails post-init validation."""
        props = EdgeProperties()

        # Test missing from_id
        with pytest.raises(ValueError, match="Edge from_id is required"):
            EdgeDetails(
                id="edge_1",
                class_id="connection",
                type=NodeTypes.EDGE,
                properties=props,
                from_id="",  # Empty from_id
                to_id="target_node",
            )

        # Test missing to_id
        with pytest.raises(ValueError, match="Edge to_id is required"):
            EdgeDetails(
                id="edge_1",
                class_id="connection",
                type=NodeTypes.EDGE,
                properties=props,
                from_id="source_node",
                to_id="",  # Empty to_id
            )

    def test_edge_details_type_assignment(self):
        """Test EdgeDetails automatically sets type to EDGE."""
        props = EdgeProperties()
        details = EdgeDetails(
            id="edge_1",
            class_id="connection",
            type=NodeTypes.NODE,  # This will be overridden
            properties=props,
            from_id="source_node",
            to_id="target_node",
        )

        # Should be overridden to EDGE in post_init
        assert details.type == NodeTypes.EDGE


class TestEdge:
    """Test Edge class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_store = Mock(spec=ElementStore)
        self.mock_store.elements = {}

        self.properties = EdgeProperties(name="Test Edge", weight=1.0)
        self.details = EdgeDetails(
            id="edge_1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=self.properties,
            from_id="source_node",
            to_id="target_node",
        )

    def test_edge_initialization(self):
        """Test Edge initialization."""
        edge = Edge(self.details, self.mock_store)

        assert edge.id == "edge_1"
        assert edge.class_id == "connection"
        assert edge.type == NodeTypes.EDGE
        assert edge.from_id == "source_node"
        assert edge.to_id == "target_node"
        assert edge.properties == self.properties
        assert edge.store == self.mock_store

        # Test slots
        assert hasattr(edge, "_incoming_node")
        assert hasattr(edge, "_outgoing_node")
        assert hasattr(edge, "_nodes_cache_valid")

    def test_edge_initialization_validation(self):
        """Test Edge initialization validation."""
        mock_store = Mock(spec=ElementStore)

        # Test missing required fields - from_id
        with pytest.raises(ValueError, match="Edge from_id is required"):
            bad_details = EdgeDetails(
                id="edge1",
                class_id="connection",
                type=NodeTypes.EDGE,
                properties=EdgeProperties(),
                from_id=None,  # Invalid: missing from_id
                to_id="node2",
            )
            Edge(bad_details, mock_store)

        # Test missing to_id
        with pytest.raises(ValueError, match="Edge to_id is required"):
            bad_details = EdgeDetails(
                id="edge2",
                class_id="connection",
                type=NodeTypes.EDGE,
                properties=EdgeProperties(),
                from_id="node1",
                to_id=None,  # Invalid: missing to_id
            )
            Edge(bad_details, mock_store)

    def test_edge_inheritance(self):
        """Test Edge inherits from BaseElement."""
        from graph_api.base_element import BaseElement

        edge = Edge(self.details, self.mock_store)

        assert isinstance(edge, BaseElement)
        assert hasattr(edge, "emit")
        assert hasattr(edge, "on")
        assert hasattr(edge, "store")

    def test_edge_incoming_node_property(self):
        """Test incoming_node property with caching."""
        from graph_api.node import Node

        # Create mock node
        mock_node = Mock(spec=Node)
        mock_node.id = "source_node"

        # Mock store.get_element method
        self.mock_store.get_element = Mock(return_value=mock_node)

        edge = Edge(self.details, self.mock_store)

        # First access should cache the node
        incoming_node = edge.incoming_node
        assert incoming_node == mock_node
        assert edge._incoming_node == mock_node

        # Verify get_element was called
        self.mock_store.get_element.assert_called_with("source_node")

        # Second access should use cache (no additional calls)
        self.mock_store.get_element.reset_mock()
        incoming_node2 = edge.incoming_node
        assert incoming_node2 == mock_node
        self.mock_store.get_element.assert_not_called()

    def test_edge_outgoing_node_property(self):
        """Test outgoing_node property with caching."""
        from graph_api.node import Node

        # Create mock node
        mock_node = Mock(spec=Node)
        mock_node.id = "target_node"

        # Mock store.get_element method
        self.mock_store.get_element = Mock(return_value=mock_node)

        edge = Edge(self.details, self.mock_store)

        # First access should cache the node
        outgoing_node = edge.outgoing_node
        assert outgoing_node == mock_node
        assert edge._outgoing_node == mock_node

        # Verify get_element was called
        self.mock_store.get_element.assert_called_with("target_node")

    def test_edge_node_properties_missing_nodes(self):
        """Test incoming_node and outgoing_node when nodes don't exist."""
        # Mock store returns None for missing nodes
        self.mock_store.get_element = Mock(return_value=None)

        edge = Edge(self.details, self.mock_store)

        # Should return None for missing nodes
        assert edge.incoming_node is None
        assert edge.outgoing_node is None

    def test_edge_cache_invalidation(self):
        """Test cache invalidation when _nodes_cache_valid is False."""
        from graph_api.node import Node

        mock_node1 = Mock(spec=Node)
        mock_node1.id = "source_node"
        mock_node2 = Mock(spec=Node)
        mock_node2.id = "source_node"

        # Mock store returns different nodes on different calls
        self.mock_store.get_element = Mock(side_effect=[mock_node1, mock_node2])

        edge = Edge(self.details, self.mock_store)

        # First access caches
        incoming_node1 = edge.incoming_node
        assert incoming_node1 == mock_node1

        # Invalidate cache
        edge._nodes_cache_valid = False

        # Should fetch fresh node
        incoming_node2 = edge.incoming_node
        assert incoming_node2 == mock_node2
        assert edge._incoming_node == mock_node2

    def test_edge_reset_connections(self):
        """Test reset_connections method."""
        from graph_api.node import Node

        # Setup mock nodes that have reset methods
        mock_incoming_node = Mock(spec=Node)
        mock_outgoing_node = Mock(spec=Node)
        mock_incoming_node.reset_outgoing_edges = Mock()
        mock_outgoing_node.reset_incoming_edges = Mock()

        # Mock get_element to return our mock nodes
        self.mock_store.get_element = Mock()
        self.mock_store.get_element.side_effect = lambda node_id: {
            "source_node": mock_incoming_node,
            "target_node": mock_outgoing_node,
        }.get(node_id)

        edge = Edge(self.details, self.mock_store)

        # Call reset_connections
        edge.reset_connections()

        # Should call reset methods on connected nodes
        mock_outgoing_node.reset_incoming_edges.assert_called_once()
        mock_incoming_node.reset_outgoing_edges.assert_called_once()

    def test_edge_reset_node_caches_method(self):
        """Test _reset_node_caches method."""
        edge = Edge(self.details, self.mock_store)

        # Set some cached values
        edge._incoming_node = Mock()
        edge._outgoing_node = Mock()
        edge._nodes_cache_valid = True

        # Call reset
        edge._reset_node_caches()

        # Should clear caches
        assert edge._incoming_node is None
        assert edge._outgoing_node is None
        assert edge._nodes_cache_valid is False

    def test_edge_reset_individual_caches(self):
        """Test individual cache reset methods."""
        from graph_api.node import Node

        edge = Edge(self.details, self.mock_store)

        # Set cached values
        edge._incoming_node = Mock(spec=Node)
        edge._outgoing_node = Mock(spec=Node)
        edge._nodes_cache_valid = True

        # Reset incoming node
        edge.reset_incoming_node()
        assert edge._incoming_node is None
        assert edge._nodes_cache_valid is False

        # Reset state and test outgoing
        edge._outgoing_node = Mock(spec=Node)
        edge._nodes_cache_valid = True

        edge.reset_outgoing_node()
        assert edge._outgoing_node is None
        assert edge._nodes_cache_valid is False

    def test_edge_reset_connections_missing_nodes(self):
        """Test reset_connections with missing nodes."""
        # Empty store
        self.mock_store.elements = {}

        edge = Edge(self.details, self.mock_store)

        # Should not raise exception
        edge.reset_connections()

    def test_edge_reset_node_caches(self):
        """Test _reset_connected_nodes_caches method."""
        from graph_api.node import Node

        # Setup nodes with reset methods
        mock_incoming_node = Mock(spec=Node)
        mock_outgoing_node = Mock(spec=Node)
        mock_incoming_node.reset_outgoing_edges = Mock()
        mock_outgoing_node.reset_incoming_edges = Mock()

        edge = Edge(self.details, self.mock_store)

        # Test with both nodes available
        self.mock_store.get_element = Mock()
        self.mock_store.get_element.side_effect = lambda node_id: {
            "source_node": mock_incoming_node,
            "target_node": mock_outgoing_node,
        }.get(node_id)

        edge._reset_connected_nodes_caches()
        mock_incoming_node.reset_outgoing_edges.assert_called_once()
        mock_outgoing_node.reset_incoming_edges.assert_called_once()

    def test_edge_add_node_methods(self):
        """Test edge add_incoming_node and add_outgoing_node methods."""
        mock_store = Mock(spec=ElementStore)

        props = EdgeProperties(name="Test Edge")
        details = EdgeDetails(
            id="edge1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=props,
            from_id="node1",
            to_id="node2",
        )

        edge = Edge(details, mock_store)

        # Mock the node objects
        mock_node = Mock()
        mock_node.id = "node3"

        # Test that methods exist and can be called
        # These methods don't change from_id/to_id, they just emit events
        try:
            edge.add_incoming_node(mock_node)
            edge.add_outgoing_node(mock_node)
            # If we get here, the methods worked
            methods_callable = True
        except Exception:
            methods_callable = False

        assert (
            methods_callable
        ), "add_incoming_node and add_outgoing_node should be callable"

        # The from_id and to_id should remain unchanged
        assert edge.from_id == "node1"
        assert edge.to_id == "node2"

    def test_edge_reverse_edge(self):
        """Test edge reversal functionality."""
        mock_store = Mock(spec=ElementStore)

        props = EdgeProperties(name="Directional Edge")
        details = EdgeDetails(
            id="edge1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=props,
            from_id="node1",
            to_id="node2",
        )

        edge = Edge(details, mock_store)

        # Store original values
        original_from = edge.from_id
        original_to = edge.to_id

        # Test reversal
        edge.reverse_edge()

        # Check that from/to are swapped
        assert edge.from_id == original_to
        assert edge.to_id == original_from
        assert edge.from_id == "node2"
        assert edge.to_id == "node1"


class TestEdgeIntegration:
    """Integration tests for Edge with other components."""

    def test_edge_with_real_store(self):
        """Test Edge with actual ElementStore."""
        from graph_api.base_element import NodeTypes
        from graph_api.element_store import ElementStore

        # Create real store
        store = ElementStore()
        store.get_element = Mock()  # Mock the get_element method

        # Create edge
        edge_props = EdgeProperties(name="Connection", weight=1.0)
        edge_details = EdgeDetails(
            id="edge1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=edge_props,
            from_id="node1",
            to_id="node2",
        )

        edge = Edge(edge_details, store)

        # Test edge properties
        assert edge.from_id == "node1"
        assert edge.to_id == "node2"
        assert edge.properties["weight"] == 1.0
        assert edge.properties["name"] == "Connection"

    def test_edge_bidirectional_operations(self):
        """Test edge direction operations."""
        mock_store = Mock(spec=ElementStore)

        props = EdgeProperties(name="Bidirectional")
        details = EdgeDetails(
            id="edge1",
            class_id="friendship",
            type=NodeTypes.EDGE,
            properties=props,
            from_id="alice",
            to_id="bob",
        )

        edge = Edge(details, mock_store)

        # Test directional properties
        assert edge.from_id == "alice"
        assert edge.to_id == "bob"

        # Test edge reversal
        edge.reverse_edge()

        # After reversal
        assert edge.from_id == "bob"
        assert edge.to_id == "alice"

    def test_edge_property_updates(self):
        """Test edge property updates."""
        mock_store = Mock(spec=ElementStore)
        props = EdgeProperties(weight=1.0, active=True)
        details = EdgeDetails(
            id="edge1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=props,
            from_id="node1",
            to_id="node2",
        )

        edge = Edge(details, mock_store)

        # Update properties
        edge.properties["weight"] = 2.0
        edge.properties["new_prop"] = "new_value"

        assert edge.properties["weight"] == 2.0
        assert edge.properties["new_prop"] == "new_value"
        assert edge.properties["active"] is True

    def test_edge_with_node_caching(self):
        """Test edge node caching behavior."""
        from graph_api.node import Node

        mock_store = Mock(spec=ElementStore)
        mock_incoming = Mock(spec=Node)
        mock_outgoing = Mock(spec=Node)

        # Configure store to return nodes
        mock_store.get_element.side_effect = lambda node_id: {
            "source_node": mock_incoming,
            "target_node": mock_outgoing,
        }.get(node_id)

        props = EdgeProperties(name="Cached Edge")
        details = EdgeDetails(
            id="edge1",
            class_id="connection",
            type=NodeTypes.EDGE,
            properties=props,
            from_id="source_node",
            to_id="target_node",
        )

        edge = Edge(details, mock_store)

        # First access should call get_element
        incoming1 = edge.incoming_node
        assert incoming1 == mock_incoming
        assert mock_store.get_element.call_count == 1

        # Second access should use cache
        mock_store.get_element.reset_mock()
        incoming2 = edge.incoming_node
        assert incoming2 == mock_incoming
        assert mock_store.get_element.call_count == 0  # No additional calls

        # Cache invalidation should cause fresh fetch
        edge._nodes_cache_valid = False
        incoming3 = edge.incoming_node
        assert incoming3 == mock_incoming
        assert mock_store.get_element.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__])
