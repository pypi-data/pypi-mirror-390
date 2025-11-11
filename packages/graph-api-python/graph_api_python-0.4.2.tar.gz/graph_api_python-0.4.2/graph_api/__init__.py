"""
Graph Elements Library

A Python library for graph-based data structures and queries, providing TypeScript-equivalent
functionality for BaseElement, Node, Edge, MetaNode, and ElementStore classes with a fluent
GraphQuery API.
"""

from .base_element import ElementProperties  # Backward compatibility alias
from .base_element import (
    KG,
    BaseElement,
    DataContext,
    ElementDetails,
    NodeTypes,
    PropertyValue,
    Props,
    generate_guid,
    generate_hash,
)
from .edge import (
    Edge,
    EdgeDetails,
    EdgeProperties,
)
from .element_store import (
    ElementStore,
    ElementStoreConfig,
    IDataStorage,
    IDataStorageConfig,
    ISuggestion,
    MemoryDataStorage,
    QueryOptions,
)
from .fluent_query import (
    FluentQuery,
)
from .graph_query import (
    ElementFilter,
    ElementFilters,
    FilterOperator,
    GraphQuery,
    IFluentOperation,
    IFluentOptions,
    QueryOperations,
)
from .meta import (
    AgentTask,
    FilterPreset,
    ListItem,
    MetaNode,
    MetaNodeDetails,
    MetaNodeProperties,
    MetaPropertyType,
    MetaSection,
    MonitorConfig,
    PropertyCondition,
    PropertyRelation,
    PropValueType,
    ValidationResult,
)
from .node import (
    Node,
    NodeDetails,
    NodeProperties,
)
from .rest_client import (
    ApiResponse,
    ElementNotFoundError,
    GraphApiError,
    HttpError,
    InternalServerError,
    QueryError,
    RestClientConfig,
    RestDataStorage,
    RestDataStorageConfig,
    RestGraphApiClient,
    ValidationError,
)

__all__ = [
    # Base classes
    "BaseElement",
    "ElementDetails",
    "Props",
    "ElementProperties",  # Backward compatibility alias
    "DataContext",
    "NodeTypes",
    "PropertyValue",
    "KG",
    "generate_guid",
    "generate_hash",
    # Node classes
    "Node",
    "NodeDetails",
    "NodeProperties",
    # Edge classes
    "Edge",
    "EdgeDetails",
    "EdgeProperties",
    # Meta classes
    "MetaNode",
    "MetaNodeDetails",
    "MetaNodeProperties",
    "MetaPropertyType",
    "PropValueType",
    "PropertyCondition",
    "AgentTask",
    "ListItem",
    "PropertyRelation",
    "MonitorConfig",
    "FilterPreset",
    "MetaSection",
    "ValidationResult",
    # Store classes
    "ElementStore",
    "ElementStoreConfig",
    "IDataStorage",
    "IDataStorageConfig",
    "MemoryDataStorage",
    "QueryOptions",
    "ISuggestion",
    # Query classes
    "GraphQuery",
    "FilterOperator",
    "QueryOperations",
    "ElementFilters",
    "IFluentOptions",
    "IFluentOperation",
    "ElementFilter",
    "FluentQuery",
    # REST client classes
    "RestGraphApiClient",
    "RestDataStorage",
    "RestDataStorageConfig",
    "RestClientConfig",
    "ApiResponse",
    "GraphApiError",
    "ValidationError",
    "ElementNotFoundError",
    "QueryError",
    "InternalServerError",
    "HttpError",
]

__version__ = "1.0.0"
