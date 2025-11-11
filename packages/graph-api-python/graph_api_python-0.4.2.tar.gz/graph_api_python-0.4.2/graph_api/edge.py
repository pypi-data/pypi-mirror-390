from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Union

from .base_element import BaseElement, ElementDetails, ElementProperties, NodeTypes

if TYPE_CHECKING:
    from .element_store import ElementStore
    from .node import Node


class EdgeProperties(ElementProperties):
    """Properties specific to Edge elements using inheritance."""

    # Add edge-specific properties here if needed
    pass


@dataclass(slots=True)
class EdgeDetails(ElementDetails):
    """Complete edge data structure with required from_id and to_id."""

    from_id: str
    to_id: str

    def __post_init__(self):
        """Ensure type is always EDGE and validate required fields."""
        if not self.from_id:
            raise ValueError("Edge from_id is required")
        if not self.to_id:
            raise ValueError("Edge to_id is required")
        self.type = NodeTypes.EDGE


class Edge(BaseElement):
    """Extended Edge class for graph edges with optimized node caching."""

    __slots__ = ("_incoming_node", "_outgoing_node", "_nodes_cache_valid")

    def __init__(
        self,
        data: Union[EdgeDetails, ElementDetails],
        store: Optional["ElementStore"] = None,
    ) -> None:
        """Initialize edge with proper validation and cache management."""
        # Validate edge data
        if not data.from_id or not data.to_id:
            raise ValueError("Edge must have both from_id and to_id")

        super().__init__(data, store)

        # Node caches - None means not cached
        self._incoming_node: Optional[Node] = None
        self._outgoing_node: Optional[Node] = None
        self._nodes_cache_valid: bool = True

    @property
    def incoming_node(self) -> Optional["Node"]:
        """Get the incoming node (source of the edge) with efficient caching."""
        if (
            self._incoming_node is None or not self._nodes_cache_valid
        ) and self.from_id:
            if not self.store:
                self._incoming_node = None
            else:
                from .node import Node

                element = self.store.get_element(self.from_id)
                if isinstance(element, Node):
                    self._incoming_node = element
                else:
                    self._incoming_node = (
                        None  # Explicitly set to None for invalid references
                    )
            self._nodes_cache_valid = True
        return self._incoming_node

    @property
    def outgoing_node(self) -> Optional["Node"]:
        """Get the outgoing node (target of the edge) with efficient caching."""
        if (self._outgoing_node is None or not self._nodes_cache_valid) and self.to_id:
            if not self.store:
                self._outgoing_node = None
            else:
                from .node import Node

                element = self.store.get_element(self.to_id)
                if isinstance(element, Node):
                    self._outgoing_node = element
                else:
                    self._outgoing_node = (
                        None  # Explicitly set to None for invalid references
                    )
            self._nodes_cache_valid = True
        return self._outgoing_node

    def _reset_node_caches(self) -> None:
        """Reset node caches and mark them as invalid."""
        self._incoming_node = None
        self._outgoing_node = None
        self._nodes_cache_valid = False

    def reset_incoming_node(self) -> None:
        """Reset incoming node cache."""
        self._incoming_node = None
        self._nodes_cache_valid = False

    def reset_outgoing_node(self) -> None:
        """Reset outgoing node cache."""
        self._outgoing_node = None
        self._nodes_cache_valid = False

    def reset_connections(self) -> None:
        """Reset all connection caches."""
        self._reset_connected_nodes_caches()
        self._reset_node_caches()

    def _reset_connected_nodes_caches(self) -> None:
        """Reset edge caches on connected nodes."""
        # Reset caches on connected nodes if they exist
        outgoing = self.outgoing_node
        if outgoing and hasattr(outgoing, "reset_incoming_edges"):
            outgoing.reset_incoming_edges()

        incoming = self.incoming_node
        if incoming and hasattr(incoming, "reset_outgoing_edges"):
            incoming.reset_outgoing_edges()

    def add_incoming_node(self, node: "Node") -> None:
        """Add an incoming node reference."""
        self.emit("incoming_node_added", node)

    def add_outgoing_node(self, node: "Node") -> None:
        """Add an outgoing node reference."""
        self.emit("outgoing_node_added", node)

    def reverse_edge(self) -> None:
        """Reverse the direction of the edge with proper cache management."""
        # Clear caches before swapping
        self._reset_node_caches()
        self._reset_connected_nodes_caches()

        # Swap from_id and to_id
        self.from_id, self.to_id = self.to_id, self.from_id

        # Mark as updated and emit event
        self.mark_updated()
        self.emit("edge_reversed")
