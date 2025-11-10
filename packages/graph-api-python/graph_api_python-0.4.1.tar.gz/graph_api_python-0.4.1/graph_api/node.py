from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING, List, Optional, Union

from .base_element import BaseElement, ElementDetails, ElementProperties, NodeTypes

if TYPE_CHECKING:
    from .edge import Edge
    from .element_store import ElementStore
    from .meta import MetaPropertyType


class NodeProperties(ElementProperties):
    """Properties specific to Node elements using inheritance."""

    # Add node-specific properties here if needed
    pass


@dataclass(slots=True)
class NodeDetails(ElementDetails):
    """Complete node data structure with automatic type assignment."""

    def __post_init__(self):
        """Ensure type is always NODE."""
        self.type = NodeTypes.NODE


class Node(BaseElement):
    """Extended Node class for graph nodes with optimized edge caching."""

    __slots__ = ("_incoming_edges", "_outgoing_edges", "_edges_cache_valid")

    def __init__(
        self,
        data: Union[NodeDetails, ElementDetails],
        store: Optional["ElementStore"] = None,
    ) -> None:
        """Initialize node with proper cache management."""
        super().__init__(data, store)

        # Edge caches - None means not cached, empty list means cached but empty
        self._incoming_edges: Optional[List[Edge]] = None
        self._outgoing_edges: Optional[List[Edge]] = None
        self._edges_cache_valid: bool = True

    @property
    def incoming_edges(self) -> List["Edge"]:
        """Get incoming edges to this node with efficient caching."""
        if self._incoming_edges is None or not self._edges_cache_valid:
            if not self.store:
                self._incoming_edges = []
            else:
                from .edge import Edge

                self._incoming_edges = [
                    el
                    for el in self.store.elements.values()
                    if (
                        isinstance(el, Edge)
                        and el.type == NodeTypes.EDGE
                        and el.to_id == self.id
                    )
                ]
            self._edges_cache_valid = True
        return self._incoming_edges

    def incoming_elements(
        self,
        property_filter: Union[str, "MetaPropertyType"],
        class_id: Optional[Union[str, List[str]]] = None,
    ) -> List[BaseElement]:
        """Get elements that reference this node through a property with optimized filtering."""
        if not self.store:
            return []

        # Extract property key efficiently
        prop_key = (
            property_filter
            if isinstance(property_filter, str)
            else getattr(property_filter, "key", str(property_filter))
        )

        # Pre-filter by class_id if provided (more efficient)
        if class_id:
            class_ids = {class_id} if isinstance(class_id, str) else set(class_id)
            candidate_elements = (
                el for el in self.store.elements.values() if el.class_id in class_ids
            )
        else:
            candidate_elements = self.store.elements.values()

        # Filter by property match
        return [
            element
            for element in candidate_elements
            if element.properties.get(prop_key) == self.id
        ]

    @property
    def outgoing_edges(self) -> List["Edge"]:
        """Get outgoing edges from this node with efficient caching."""
        if self._outgoing_edges is None or not self._edges_cache_valid:
            if not self.store:
                self._outgoing_edges = []
            else:
                from .edge import Edge

                self._outgoing_edges = [
                    el
                    for el in self.store.elements.values()
                    if (
                        isinstance(el, Edge)
                        and el.type == NodeTypes.EDGE
                        and el.from_id == self.id
                    )
                ]
            self._edges_cache_valid = True
        return self._outgoing_edges

    @cached_property
    def edges(self) -> List["Edge"]:
        """Get all edges connected to this node (cached property)."""
        return self.incoming_edges + self.outgoing_edges

    def get_outgoing_by_property(
        self, property_filter: Union[str, "MetaPropertyType"]
    ) -> Optional[List["Edge"]]:
        """Get outgoing edges filtered by property/relation type."""
        if isinstance(property_filter, str):
            return [
                edge for edge in self.outgoing_edges if edge.class_id == property_filter
            ]
        else:
            # Handle MetaPropertyType with relation
            if hasattr(property_filter, "relation") and property_filter.relation:
                relation_type = getattr(property_filter.relation, "type", None)
                if relation_type:
                    return [
                        edge
                        for edge in self.outgoing_edges
                        if edge.class_id == relation_type
                    ]
        return None

    def get_incoming_by_property(
        self, property_filter: Union[str, "MetaPropertyType"]
    ) -> Optional[List["Edge"]]:
        """Get incoming edges filtered by property/relation type."""
        if isinstance(property_filter, str):
            return [
                edge for edge in self.incoming_edges if edge.class_id == property_filter
            ]
        else:
            # Handle MetaPropertyType with relation
            if hasattr(property_filter, "relation") and property_filter.relation:
                relation_type = getattr(property_filter.relation, "type", None)
                if relation_type:
                    return [
                        edge
                        for edge in self.incoming_edges
                        if edge.class_id == relation_type
                    ]
        return None

    def reset_connections(self) -> None:
        """Reset all connection caches and clear cached_property."""
        self._reset_edge_caches()
        # Clear cached_property if it exists
        self.__dict__.pop("edges", None)

    def _reset_edge_caches(self) -> None:
        """Reset edge caches and mark them as invalid."""
        self._incoming_edges = None
        self._outgoing_edges = None
        self._edges_cache_valid = False

    def reset_incoming_edges(self) -> None:
        """Reset incoming edges cache."""
        self._incoming_edges = None
        self._edges_cache_valid = False

    def reset_outgoing_edges(self) -> None:
        """Reset outgoing edges cache."""
        self._outgoing_edges = None
        self._edges_cache_valid = False

    def add_incoming_node(self, edge: "Edge") -> None:
        """Add an incoming edge to cache."""
        if self._incoming_edges is not None:
            self._incoming_edges.append(edge)
        self.emit("incoming_edge_added")

    def add_outgoing_node(self, edge: "Edge") -> None:
        """Add an outgoing edge to cache."""
        if self._outgoing_edges is not None:
            self._outgoing_edges.append(edge)
        self.emit("outgoing_edge_added")
