import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union

from .base_element import (
    KG,
    BaseElement,
    ElementDetails,
    ElementProperties,
    NodeTypes,
    PropertyValue,
    generate_guid,
)
from .edge import Edge, EdgeDetails, EdgeProperties
from .meta import MetaNode
from .node import Node

if TYPE_CHECKING:
    from .graph_query import GraphQuery

    """Type hint for element classes."""

    pass


@dataclass
class ISuggestion:
    """Interface for suggestions."""

    key: str


@dataclass
class IDataStorageConfig:
    """Configuration for data storage."""

    type: str = "memory"
    extra_config: Dict[str, Any] = field(default_factory=dict)


class IDataStorage(ABC):
    """Abstract interface for data storage operations."""

    def __init__(self):
        self.store_server: Optional[IDataStorageConfig] = None
        self.store: Optional[ElementStore] = None

    @abstractmethod
    async def init(self) -> None:
        """Initialize the data storage."""
        pass

    @abstractmethod
    async def load_data(self) -> Optional[Dict[str, BaseElement]]:
        """Load all data from storage."""
        pass

    @abstractmethod
    async def create_elements(self, elements: List[BaseElement]) -> None:
        """Create elements in storage."""
        pass

    @abstractmethod
    async def update_elements(self, elements: List[BaseElement]) -> None:
        """Update elements in storage."""
        pass

    @abstractmethod
    async def patch_elements(self, elements: List[BaseElement]) -> None:
        """Partially update elements in storage."""
        pass

    @abstractmethod
    async def delete_elements(self, elements: List[BaseElement]) -> None:
        """Delete elements from storage."""
        pass

    async def get_elements_by_class_id(self, class_id: str) -> Dict[str, BaseElement]:
        """
        Get elements by class ID from storage.

        Args:
            class_id: The class ID to filter by

        Returns:
            Dictionary of BaseElement objects keyed by ID that match the class
        """
        # Default implementation for storage backends that don't support native filtering
        data = await self.load_data()
        if not data:
            return {}

        return {
            element_id: element
            for element_id, element in data.items()
            if element.class_id == class_id
        }

    @abstractmethod
    async def reset(self) -> None:
        """Reset/clear all data in storage."""
        pass


def create_data_storage(config: IDataStorageConfig) -> IDataStorage:
    """
    Factory function to create the appropriate data storage based on config.

    Args:
        config: Storage configuration

    Returns:
        Configured data storage instance
    """
    storage_type = config.type.lower()

    if storage_type == "memory":
        return MemoryDataStorage()
    elif storage_type == "rest":
        # Import here to avoid circular imports
        from .rest_client import RestDataStorage, RestDataStorageConfig

        if isinstance(config, RestDataStorageConfig):
            return RestDataStorage(config.to_rest_config())
        else:
            # Create default REST config from extra_config
            rest_config = RestDataStorageConfig(**config.extra_config)
            return RestDataStorage(rest_config.to_rest_config())
    elif storage_type == "synchronized":
        # Import here to avoid circular imports
        from .rest_client import SynchronizedDataStorage, SynchronizedDataStorageConfig

        if isinstance(config, SynchronizedDataStorageConfig):
            storage = SynchronizedDataStorage(config.to_rest_config())
            if config.json_store_path:
                storage.set_json_store_path(config.json_store_path)
            return storage
        else:
            # Create default synchronized config from extra_config
            sync_config = SynchronizedDataStorageConfig(**config.extra_config)
            storage = SynchronizedDataStorage(sync_config.to_rest_config())
            if sync_config.json_store_path:
                storage.set_json_store_path(sync_config.json_store_path)
            return storage
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")


class MemoryDataStorage(IDataStorage):
    """Simple in-memory data storage implementation."""

    def __init__(self):
        super().__init__()
        self._data: Dict[str, BaseElement] = {}

    async def init(self) -> None:
        """Initialize memory storage."""
        pass

    async def load_data(self) -> Optional[Dict[str, BaseElement]]:
        """Load data from memory."""
        return self._data.copy() if self._data else None

    async def create_elements(self, elements: List[BaseElement]) -> None:
        """Store elements in memory."""
        for element in elements:
            self._data[element.id] = element

    async def update_elements(self, elements: List[BaseElement]) -> None:
        """Update elements in memory."""
        for element in elements:
            if element.id in self._data:
                self._data[element.id] = element

    async def delete_elements(self, elements: List[BaseElement]) -> None:
        """Delete elements from memory."""
        for element in elements:
            if element.id in self._data:
                del self._data[element.id]

    async def patch_elements(self, elements: List[BaseElement]) -> None:
        """Patch elements in memory."""
        for element in elements:
            if element.id in self._data:
                self._data[element.id] = element

    async def reset(self) -> None:
        """Clear all data from memory."""
        self._data.clear()


@dataclass
class QueryOptions:
    """Options for graph queries."""

    limit: Optional[int] = None
    offset: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


@dataclass
class ElementStoreConfig:
    """Configuration for ElementStore."""

    data_config: Optional[IDataStorageConfig] = None
    operation: Optional[IDataStorage] = None
    default_node: Optional[Type[Node]] = None
    default_edge: Optional[Type[Edge]] = None
    default_meta_node: Optional[Type[MetaNode]] = None


class ElementStore:
    """Store to manage CRUD operations for elements."""

    def __init__(self, config: Optional[ElementStoreConfig] = None):
        """Initialize ElementStore with configuration."""
        self.elements = KG()

        if config:
            if config.operation:
                self.data_operation = config.operation
            elif config.data_config:
                self.data_operation = create_data_storage(config.data_config)
            else:
                self.data_operation = MemoryDataStorage()

            if config.data_config:
                self.data_operation.store_server = config.data_config
            self.default_node = config.default_node or Node
            self.default_edge = config.default_edge or Edge
            self.default_meta_node = config.default_meta_node or MetaNode
        else:
            self.data_operation = MemoryDataStorage()
            self.default_node = Node
            self.default_edge = Edge
            self.default_meta_node = MetaNode

        self.data_operation.store = self
        self.element_types = {}
        self.suggestion_lists = {}

    async def load_elements(self) -> None:
        """Load elements from data storage."""
        try:
            await self.data_operation.init()
            data = await self.data_operation.load_data()

            if data:
                await self.add_elements(list(data.values()), skip_save=True)

            for element in self.elements.values():
                self.check_suggestions(element)

        except Exception as error:
            print(f"Error loading data: {error}")

    def get_element(self, element_id: str) -> Optional[BaseElement]:
        """Get element by ID."""
        return self.elements.elements.get(element_id)

    def get_all_elements(self) -> List[BaseElement]:
        """Get all elements in the store."""
        return list(self.elements.elements.values())

    def get_element_by_id(self, element_id: str) -> Optional[BaseElement]:
        """Get element by ID (alias for get_element)."""
        return self.get_element(element_id)

    def get_elements(self, ids: List[str]) -> List[BaseElement]:
        """Get multiple elements by IDs."""
        return [
            self.elements[element_id]
            for element_id in ids
            if element_id in self.elements
        ]

    def get_meta_node_by_id(self, element_id: str) -> Optional[MetaNode]:
        """Get MetaNode by ID."""
        element = self.elements.elements.get(element_id)
        if element and element.type == NodeTypes.META:
            return element
        return None

    async def get_elements_by_class_id(self, class_id: str) -> KG:
        """Get elements by their class ID, excluding meta nodes."""
        result_elements = {
            k: v
            for k, v in self.elements.items()
            if v.class_id == class_id and v.type != NodeTypes.META
        }
        result_kg = KG()
        # Populate KG using its dict-like interface
        for k, v in result_elements.items():
            result_kg[k] = v
        return result_kg

    async def get_elements_by_property(
        self, class_id: str, property_name: str, value: PropertyValue
    ) -> KG:
        """Get elements by property filter, excluding meta nodes."""
        result_elements = {
            k: v
            for k, v in self.elements.items()
            if (
                v.class_id == class_id
                and v.type != NodeTypes.META
                and hasattr(v, "properties")
                and v.properties.get(property_name) == value
            )
        }
        result_kg = KG()
        # Populate KG using its dict-like interface
        for k, v in result_elements.items():
            result_kg[k] = v
        return result_kg

    def query(
        self,
        elements: Optional[List[BaseElement]] = None,
        options: Optional[QueryOptions] = None,
    ) -> "GraphQuery":
        """Create a new graph query."""
        from .graph_query import GraphQuery

        query = GraphQuery(self)
        if elements:
            query.result = elements
        return query

    def create_instance(
        self, class_id: str, element_type: str, *args, **kwargs
    ) -> BaseElement:
        """Create instance of registered element type."""
        if class_id in self.element_types:
            return self.element_types[class_id](*args, **kwargs)
        else:
            raise ValueError(f"Type {class_id} is not registered.")

    async def add_edge(
        self,
        class_id: str,
        from_element: Union[ElementDetails, str],
        to_element: Union[ElementDetails, str],
        source: Optional[str] = None,
        properties: Optional[EdgeProperties] = None,
    ) -> Optional[Edge]:
        """Helper method to quickly create and add edge."""
        from_id = from_element if isinstance(from_element, str) else from_element.id
        to_id = to_element if isinstance(to_element, str) else to_element.id

        if from_id and to_id:
            edge_details = EdgeDetails(
                from_id=from_id,
                to_id=to_id,
                id=generate_guid(),
                class_id=class_id,
                type=NodeTypes.EDGE,
                properties=properties or EdgeProperties(),
                source=source,
            )

            edge = self.create_new_element(class_id, edge_details)
            await self.add_elements([edge])
            edge.reset_connections()
            return edge
        return None

    async def delete_edge(self, class_id: str, from_node: Node, to_node: Node) -> None:
        """Helper method to delete edge between nodes."""
        if not from_node.outgoing_edges or not to_node.id:
            return

        matches = [
            edge
            for edge in from_node.outgoing_edges
            if edge.to_id == to_node.id and edge.class_id == class_id
        ]

        if matches:
            await self.delete_elements(matches)

    def create_element(self, element_data: ElementDetails) -> BaseElement:
        """Create element instance but don't add to store."""
        if element_data.class_id in self.element_types:
            return self.element_types[element_data.class_id](element_data, self)
        else:
            # Handle inheritance and card attributes for nodes
            if (
                element_data.type == NodeTypes.NODE
                and element_data.class_id in self.elements
                and self.elements[element_data.class_id].type == NodeTypes.META
            ):

                metanode = self.elements[element_data.class_id]

                if not element_data.attributes:
                    element_data.attributes = {}

                # Copy card attributes from metanode
                if metanode.attributes:
                    for key, value in metanode.attributes.items():
                        if key.startswith("card:"):
                            element_data.attributes[key] = value

            # Create based on type
            if element_data.type == NodeTypes.NODE:
                return self.default_node(element_data, self)
            elif element_data.type == NodeTypes.EDGE:
                return self.default_edge(element_data, self)
            elif element_data.type == NodeTypes.META:
                return self.default_meta_node(element_data, self)
            else:
                return BaseElement(element_data, self)

    async def update_element_properties(
        self, element: BaseElement, properties: Dict[str, PropertyValue]
    ) -> None:
        """Update element properties."""
        element.update_properties(properties)
        await self.update_elements([element], lazy=True)

    def create_new_element(
        self,
        class_id: str,
        preset: Optional[Union[ElementDetails, ElementProperties]] = None,
    ) -> BaseElement:
        """Create new element with defaults."""
        meta_node = self.get_meta_node_by_id(class_id)

        # Handle preset data
        if preset and hasattr(preset, "properties"):
            base = preset
        else:
            base = ElementDetails(
                id="",
                class_id=class_id,
                type=NodeTypes.NODE,
                properties=preset if preset else ElementProperties(),
            )

        # Create element properties
        properties_dict = {}
        if hasattr(base, "properties") and base.properties:
            if hasattr(base.properties, "items"):
                properties_dict.update(dict(base.properties.items()))
            else:
                properties_dict.update(vars(base.properties))

        # Set default name if not provided
        if "name" not in properties_dict or not properties_dict["name"]:
            properties_dict["name"] = (
                f"New {meta_node.properties.name if meta_node else class_id}"
            )

        # Create element details
        details = ElementDetails(
            id=getattr(preset, "id", None) or str(uuid.uuid4()),
            class_id=class_id,
            to_id=getattr(preset, "to_id", None),
            from_id=getattr(preset, "from_id", None),
            type=(
                meta_node.properties.type
                if meta_node and meta_node.properties.type
                else getattr(preset, "type", NodeTypes.NODE)
            ),
            source=(
                getattr(preset, "source", None)
                or (meta_node.properties.get("target_source") if meta_node else None)
                or (meta_node.source if meta_node else None)
            ),
            temp=getattr(preset, "temp", False),
            flat=getattr(preset, "flat", {}),
            properties=ElementProperties(**properties_dict),
        )

        return self.create_element(details)

    def check_suggestions(self, element: BaseElement) -> None:
        """Check and update suggestion lists for element properties."""
        if not element.meta_node:
            return

        suggestion_properties = [
            pt
            for pt in element.meta_node.all_prop_types.values()
            if pt.suggestions_list
        ]

        for prop in suggestion_properties:
            prop_value = element.properties.get(prop.key)
            values = prop_value if isinstance(prop_value, list) else [prop_value]

            if values and values[0] is not None and prop.suggestions_list:
                if prop.suggestions_list not in self.suggestion_lists:
                    self.suggestion_lists[prop.suggestions_list] = {}

                for value in values:
                    if (
                        value
                        and value not in self.suggestion_lists[prop.suggestions_list]
                    ):
                        self.suggestion_lists[prop.suggestions_list][value] = (
                            ISuggestion(key=value)
                        )

    async def add_elements(
        self,
        new_elements: Union[
            BaseElement, ElementDetails, List[Union[BaseElement, ElementDetails]]
        ],
        skip_save: bool = False,
        notify: bool = True,
        lazy: bool = False,
        datasource: Optional[str] = None,
    ) -> List[BaseElement]:
        """Add elements to store and save to data storage."""
        added_elements = []

        async def push_element(element: Union[BaseElement, ElementDetails]) -> None:
            if isinstance(element, BaseElement):
                e = element
            else:
                e = self.create_element(element)

            if not skip_save:
                e.temp = False

            self.elements[e.id] = e

            if e.type == NodeTypes.EDGE and not skip_save:
                e.reset_connections()

            added_elements.append(e)

        # Handle single element or list
        elements_to_add = (
            new_elements if isinstance(new_elements, list) else [new_elements]
        )

        if elements_to_add:
            # Sort by type priority (meta, node, edge)
            type_order = {NodeTypes.META: 0, NodeTypes.NODE: 1, NodeTypes.EDGE: 2}
            elements_to_add.sort(
                key=lambda x: type_order.get(getattr(x, "type", NodeTypes.NODE), 1)
            )

            for element in elements_to_add:
                await push_element(element)
        else:
            return []

        # Save to storage
        if not skip_save:
            if lazy:
                await self.data_operation.create_elements(added_elements)
            else:
                await self.data_operation.create_elements(added_elements)

        return added_elements

    async def reset(self) -> None:
        """Reset store and data storage."""
        self.elements = KG()
        await self.data_operation.reset()

    async def patch_elements(
        self, updated_elements: List[BaseElement]
    ) -> List[BaseElement]:
        """Patch/update elements."""
        await self.data_operation.update_elements(updated_elements)
        return updated_elements

    async def update_elements(
        self, updated_elements: List[BaseElement], lazy: bool = False
    ) -> List[BaseElement]:
        """Update elements in storage."""
        if lazy:
            await self.data_operation.update_elements(updated_elements)
        else:
            await self.data_operation.update_elements(updated_elements)

        for element in updated_elements:
            self.check_suggestions(element)

        return updated_elements

    async def delete_elements(
        self, elements: List[Union[BaseElement, str]], lazy: bool = False
    ) -> None:
        """Delete elements from store and storage."""
        try:
            deletes = []
            for element in elements:
                e = self.get_element(element) if isinstance(element, str) else element
                if e:
                    deletes.append(e)
                    if hasattr(e, "reset_connections"):
                        e.reset_connections()
                    if e.id in self.elements:
                        del self.elements.elements[e.id]

            if self.data_operation and deletes:
                if lazy:
                    await self.data_operation.delete_elements(deletes)
                else:
                    await self.data_operation.delete_elements(deletes)

        except Exception as error:
            print(f"Error deleting elements: {error}")

    async def refresh_elements(
        self, class_ids: Optional[List[str]] = None
    ) -> List[BaseElement]:
        """Refresh elements from storage."""
        elements_data = await self.data_operation.load_data()
        if not elements_data:
            return []

        if not class_ids:
            return list(elements_data.values())

        new_elements = [
            element
            for element in elements_data.values()
            if element.class_id in class_ids
        ]

        await self.add_elements(new_elements, skip_save=True)
        return new_elements

    async def duplicate_element(self, element: BaseElement) -> BaseElement:
        """Duplicate an existing element."""
        new_element = self.create_new_element(element.class_id, element)
        await self.add_elements([new_element])
        return new_element

    async def addNodeAsync(self, class_id_or_node, props_or_kwargs=None, **kwargs):
        """Add a node to the store asynchronously.

        Usage:
        - store.addNodeAsync('person', props) - Create and add node from Props
        - store.addNodeAsync('person', name='John', age=30) - Create from kwargs
        - store.addNodeAsync(existing_node) - Add existing node

        Args:
            class_id_or_node: Either a string class_id or an existing Node object
            props_or_kwargs: Props object or can be None if using kwargs
            **kwargs: Individual property values (name='John', age=30)

        Returns:
            The node that was added to the store
        """
        if isinstance(class_id_or_node, str):
            # Create new node from class_id and props/kwargs
            if props_or_kwargs is None and kwargs:
                # Create Props from kwargs: addNode('person', name='John', age=30)
                from .base_element import Props

                props = Props(**kwargs)
            elif props_or_kwargs is not None:
                # Use provided Props: addNode('person', props)
                props = props_or_kwargs
            else:
                # No props provided
                from .base_element import Props

                props = Props()

            node = self.create_new_element(class_id_or_node, props)
            await self.add_elements([node])
            return node
        else:
            # Add existing node
            node = class_id_or_node
            await self.add_elements([node])
            return node

    def createNode(self, class_id, props=None):
        """Create a new node (alias for create_new_element).

        Usage:
        - store.createNode('person', props)

        Args:
            class_id: String class identifier for the node
            props: Props object with node properties

        Returns:
            The created node (not added to store yet)
        """
        if props is None:
            from .base_element import Props

            props = Props()
        return self.create_new_element(class_id, props)

    async def addEdgeAsync(
        self,
        class_id_or_edge,
        from_node_or_props=None,
        to_node=None,
        props_or_kwargs=None,
        **kwargs,
    ):
        """Add an edge to the store asynchronously.

        Usage:
        - store.addEdgeAsync('relationship', from_node, to_node, props)
        - store.addEdgeAsync('relationship', from_node, to_node, type='friend')
        - store.addEdgeAsync(existing_edge) - Add existing edge

        Args:
            class_id_or_edge: Either a string class_id or an existing Edge object
            from_node_or_props: Source node (for class_id) or Props (for existing edge)
            to_node: Target node (only used when first arg is class_id)
            props_or_kwargs: Props object or can be None if using kwargs
            **kwargs: Individual property values (type='friend', strength=0.8)

        Returns:
            The edge that was added to the store
        """
        if isinstance(class_id_or_edge, str):
            # Create new edge from class_id, from_node, to_node, and props/kwargs
            class_id = class_id_or_edge
            from_node = from_node_or_props

            if props_or_kwargs is None and kwargs:
                # Create Props from kwargs: addEdgeAsync('rel', from_node, to_node, type='friend')
                from .base_element import Props

                props = Props(**kwargs)
            elif props_or_kwargs is not None:
                # Use provided Props: addEdgeAsync('rel', from_node, to_node, props)
                props = props_or_kwargs
            else:
                # No props provided
                from .base_element import Props

                props = Props()

            # Use existing add_edge method
            from .edge import EdgeProperties

            edge_props = EdgeProperties(**dict(props))
            edge = await self.add_edge(
                class_id, from_node, to_node, properties=edge_props
            )
            return edge
        else:
            # Add existing edge
            edge = class_id_or_edge
            await self.add_elements([edge])
            return edge

    def addEdge(
        self,
        class_id_or_edge,
        from_node_or_props=None,
        to_node=None,
        props_or_kwargs=None,
        **kwargs,
    ):
        """Add an edge to the store synchronously (default behavior).

        Usage:
        - store.addEdge('relationship', from_node, to_node, type='friend')
        - store.addEdge('relationship', from_node, to_node, props)
        - store.addEdge(existing_edge) - Add existing edge

        Args:
            class_id_or_edge: Either a string class_id or an existing Edge object
            from_node_or_props: Source node (for class_id) or Props (for existing edge)
            to_node: Target node (only used when first arg is class_id)
            props_or_kwargs: Props object or can be None if using kwargs
            **kwargs: Individual property values (type='friend', strength=0.8)

        Returns:
            The edge that was added to the store
        """
        import asyncio

        return asyncio.run(
            self.addEdgeAsync(
                class_id_or_edge, from_node_or_props, to_node, props_or_kwargs, **kwargs
            )
        )

    def createEdge(self, class_id, from_node, to_node, props=None):
        """Create a new edge (without adding to store).

        Usage:
        - store.createEdge('relationship', from_node, to_node, props)

        Args:
            class_id: String class identifier for the edge
            from_node: Source node
            to_node: Target node
            props: Props object with edge properties

        Returns:
            The created edge (not added to store yet)
        """
        if props is None:
            from .base_element import Props

            props = Props()

        from .base_element import NodeTypes, generate_guid
        from .edge import EdgeDetails, EdgeProperties

        from_id = from_node.id if hasattr(from_node, "id") else str(from_node)
        to_id = to_node.id if hasattr(to_node, "id") else str(to_node)

        edge_details = EdgeDetails(
            from_id=from_id,
            to_id=to_id,
            id=generate_guid(),
            class_id=class_id,
            type=NodeTypes.EDGE,
            properties=EdgeProperties(**dict(props)),
            source=None,
        )

        return self.create_element(edge_details)

    def addNode(self, class_id_or_node, props_or_kwargs=None, **kwargs):
        """Add a node to the store synchronously (default behavior).

        Usage:
        - store.addNode('person', name='John', age=30) - Create from kwargs
        - store.addNode('person', props) - Create and add node from Props
        - store.addNode(existing_node) - Add existing node

        Args:
            class_id_or_node: Either a string class_id or an existing Node object
            props_or_kwargs: Props object or can be None if using kwargs
            **kwargs: Individual property values (name='John', age=30)

        Returns:
            The node that was added to the store
        """
        import asyncio

        return asyncio.run(
            self.addNodeAsync(class_id_or_node, props_or_kwargs, **kwargs)
        )
