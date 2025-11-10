"""
REST API Client for Graph API

This module provides a client interface to communicate with the TypeScript Bun/Hono/OpenAPI
graph service running on http://localhost:9800/reference

Features:
- Full CRUD operations for Elements, Schema, and Query endpoints
- Proper error handling with HTTP status code mapping
- Automatic serialization/deserialization of Python objects
- Configurable endpoint and timeout settings
- Comprehensive logging and debugging support
"""

import asyncio
import base64
import json
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, Field

from .base_element import BaseElement
from .element_store import IDataStorage, IDataStorageConfig

# Configure logging
logger = logging.getLogger(__name__)


class GraphApiError(Exception):
    """Base exception for Graph API errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class ValidationError(GraphApiError):
    """Validation error from the API."""

    pass


class ElementNotFoundError(GraphApiError):
    """Element not found error."""

    pass


class QueryError(GraphApiError):
    """Query execution error."""

    pass


class InternalServerError(GraphApiError):
    """Internal server error."""

    pass


class HttpError(GraphApiError):
    """HTTP-level error."""

    pass


@dataclass
class RestClientConfig:
    """Configuration for REST API client."""

    base_url: str = "http://localhost:9800"
    timeout: float = 30.0
    max_retries: int = 3
    verify_ssl: bool = True
    headers: Optional[Dict[str, str]] = None


class ApiResponse(BaseModel):
    """Standard API response format."""

    status: str = Field(..., pattern="^(success|error)$")
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class RestGraphApiClient:
    """
    REST client for communicating with the TypeScript Graph API.

    This client provides methods to interact with Elements, Schema, and Query endpoints
    of the graph API service.
    """

    def __init__(self, config: Optional[RestClientConfig] = None):
        """
        Initialize the REST client.

        Args:
            config: Configuration for the client. Uses defaults if not provided.
        """
        self.config = config or RestClientConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            verify=self.config.verify_ssl,
            headers=self.config.headers,
        )
        # Generate unique client ID for SSE diagnostics
        self.client_id = str(uuid.uuid4())

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _handle_error_response(self, response: ApiResponse) -> None:
        """
        Handle error responses from the API.

        Args:
            response: The API response object

        Raises:
            Appropriate exception based on error code
        """
        if response.status != "error" or not response.error:
            return

        error_code = response.error.get("code", "UNKNOWN_ERROR")
        error_message = response.error.get("message", "Unknown error occurred")
        error_details = response.error.get("details", {})

        # Map error codes to specific exceptions
        if error_code == "VALIDATION_ERROR":
            raise ValidationError(error_message, error_code, error_details)
        elif error_code == "ELEMENT_NOT_FOUND" or error_code == "CLASS_NOT_FOUND":
            raise ElementNotFoundError(error_message, error_code, error_details)
        elif error_code == "QUERY_ERROR":
            raise QueryError(error_message, error_code, error_details)
        elif error_code == "INTERNAL_ERROR":
            raise InternalServerError(error_message, error_code, error_details)
        elif error_code == "HTTP_ERROR":
            raise HttpError(error_message, error_code, error_details)
        else:
            raise GraphApiError(error_message, error_code, error_details)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], List[Any]]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> ApiResponse:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            data: Request body data (can be dict or list)
            params: URL query parameters

        Returns:
            Parsed API response

        Raises:
            GraphApiError: For various API errors
            HttpError: For HTTP-level errors
        """
        try:
            # Make request with correct parameter names
            if data is not None:
                response = await self.client.request(
                    method, endpoint, json=data, params=params
                )
            else:
                response = await self.client.request(method, endpoint, params=params)

            # Handle HTTP errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    api_response = ApiResponse(**error_data)
                    self._handle_error_response(api_response)
                except (json.JSONDecodeError, ValueError):
                    # Fallback for non-JSON error responses
                    raise HttpError(
                        f"HTTP {response.status_code}: {response.text}",
                        "HTTP_ERROR",
                        {
                            "status_code": response.status_code,
                            "response": response.text,
                        },
                    )

            # Parse successful response
            response_data = response.json()
            logger.debug(f"Response: {json.dumps(response_data, indent=2)}")

            api_response = ApiResponse(**response_data)
            self._handle_error_response(api_response)  # Check for API-level errors

            return api_response

        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HttpError(
                f"Request failed: {str(e)}", "HTTP_ERROR", {"original_error": str(e)}
            )

    # ============================================================================
    # ELEMENTS API METHODS
    # ============================================================================

    async def get_all_elements(self) -> Dict[str, Any]:
        """
        Get all elements from the API.

        Returns:
            Dictionary of all elements keyed by their IDs
        """
        response = await self._make_request("GET", "/graph/elements")
        return response.data or {}

    async def get_element_by_id(self, element_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single element by its ID.

        Args:
            element_id: The ID of the element to retrieve

        Returns:
            Element data or None if not found

        Raises:
            ElementNotFoundError: If element doesn't exist
        """
        response = await self._make_request("GET", f"/graph/elements/{element_id}")
        return response.data

    async def get_elements_by_class_id(self, class_id: str) -> Dict[str, Any]:
        """
        Get all elements of a specific class ID.

        Args:
            class_id: The class ID to filter by

        Returns:
            Dictionary containing:
                - data: List of elements matching the class
                - count: Number of elements found
                - status: Success status
        """
        response = await self._make_request(
            "GET", f"/graph/elements/classId/{class_id}"
        )
        return {
            "data": response.data or [],
            "count": len(response.data) if response.data else 0,
            "status": response.status,
        }

    async def get_elements_by_class(self, class_id: str) -> List[Dict[str, Any]]:
        """
        Get all elements of a specific class (legacy method - use get_elements_by_class_id for full response).

        Args:
            class_id: The class ID to filter by

        Returns:
            List of elements matching the class
        """
        result = await self.get_elements_by_class_id(class_id)
        return result.get("data", [])

    async def create_elements(
        self, elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create or update elements in the API.

        Args:
            elements: List of element data to create/update

        Returns:
            List of created/updated elements
        """
        response = await self._make_request("POST", "/graph/elements", data=elements)
        return response.data or []

    async def patch_elements(
        self, elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Partially update elements in the API.

        Args:
            elements: List of element data to patch

        Returns:
            List of patched elements
        """
        response = await self._make_request("PATCH", "/graph/elements", data=elements)
        return response.data or []

    async def delete_elements(self, element_ids: List[str]) -> List[str]:
        """
        Delete elements by their IDs.

        Args:
            element_ids: List of element IDs to delete

        Returns:
            List of deleted element IDs
        """
        response = await self._make_request(
            "DELETE", "/graph/elements", data=element_ids
        )
        return response.data.get("deleted", []) if response.data else []

    async def query_elements(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a query against elements.

        Args:
            query: Query object to execute

        Returns:
            Dictionary of matching elements
        """
        response = await self._make_request("POST", "/graph/elements/query", data=query)
        return response.data or {}

    # ============================================================================
    # SCHEMA API METHODS
    # ============================================================================

    async def get_all_schemas(self, schema_type: str = "default") -> Dict[str, Any]:
        """
        Get all schema definitions.

        Args:
            schema_type: Type of schema format ('default' or 'jsonschema')

        Returns:
            Dictionary of all schemas
        """
        params = {"type": schema_type} if schema_type != "default" else None
        # Schema endpoint returns direct data, not ApiResponse wrapper
        response = await self.client.request("GET", "/graph/schema", params=params)
        if response.status_code >= 400:
            try:
                error_data = response.json()
                raise GraphApiError(
                    f"Schema request failed: {error_data}", "HTTP_ERROR"
                )
            except json.JSONDecodeError:
                raise HttpError(
                    f"HTTP {response.status_code}: {response.text}", "HTTP_ERROR"
                )
        response_data = response.json()
        return response_data.get("schema", {})

    async def get_schema_by_id(
        self, schema_id: str, schema_type: str = "default"
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single schema by its ID.

        Args:
            schema_id: The ID of the schema to retrieve
            schema_type: Type of schema format ('default' or 'jsonschema')

        Returns:
            Schema data or None if not found
        """
        params = {"type": schema_type} if schema_type != "default" else None
        response = await self.client.request(
            "GET", f"/graph/schema/{schema_id}", params=params
        )
        if response.status_code == 404:
            return None
        if response.status_code >= 400:
            try:
                error_data = response.json()
                raise GraphApiError(
                    f"Schema request failed: {error_data}", "HTTP_ERROR"
                )
            except json.JSONDecodeError:
                raise HttpError(
                    f"HTTP {response.status_code}: {response.text}", "HTTP_ERROR"
                )
        response_data = response.json()
        return response_data.get("schema")

    # ============================================================================
    # QUERY API METHODS
    # ============================================================================

    async def execute_complex_query(
        self, operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute a complex fluent query.

        Args:
            operations: List of fluent operations to execute

        Returns:
            Dictionary of matching elements
        """
        response = await self._make_request("POST", "/graph/query", data=operations)
        return response.data or {}

    # ============================================================================
    # SSE (Server-Sent Events) API METHODS
    # ============================================================================

    async def _stream_sse_events(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream SSE events from the specified endpoint.

        Args:
            endpoint: SSE endpoint path
            params: URL query parameters

        Yields:
            Parsed event data as dictionaries with 'type' and 'data' keys

        Raises:
            HttpError: For connection or parsing errors
        """
        try:
            async with self.client.stream("GET", endpoint, params=params) as response:
                if response.status_code >= 400:
                    # For streaming responses, we need to read the error content
                    content = await response.aread()
                    try:
                        error_data = json.loads(content.decode("utf-8"))
                        raise GraphApiError(
                            f"SSE request failed: {error_data}", "HTTP_ERROR"
                        )
                    except json.JSONDecodeError:
                        raise HttpError(
                            f"HTTP {response.status_code}: {content.decode('utf-8')}",
                            "HTTP_ERROR",
                        )

                event_type = None
                data_buffer = ""

                async for line in response.aiter_lines():
                    line = line.strip()

                    # Parse event type (e.g., "event: CREATE")
                    if line.startswith("event: "):
                        event_type = line[7:]  # Remove "event: " prefix
                        logger.debug(f"SSE event type: {event_type}")
                        continue

                    # Parse data line (e.g., "data: {...json...}")
                    if line.startswith("data: "):
                        data_line = line[6:]  # Remove "data: " prefix
                        data_buffer += data_line
                        continue

                    # Empty line signals end of event
                    if line == "" and data_buffer.strip():
                        try:
                            event_data = json.loads(data_buffer.strip())

                            # The server sends events in two formats:
                            # 1. Named SSE events: event: CREATE, data: {...} -> wrap with event type
                            # 2. Inline events: data: {"type":"CREATE", ...} -> already has type

                            # Check if the event_data already contains a 'type' field
                            if isinstance(event_data, dict) and "type" in event_data:
                                # Event already has type, use it directly
                                yield event_data
                            elif event_type:
                                # Wrap the data with the event type
                                yield {"type": event_type, "data": event_data}
                            else:
                                # Fallback: just yield the data as-is
                                yield event_data

                            # Reset for next event
                            event_type = None
                            data_buffer = ""
                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"Failed to parse SSE event data: {data_buffer} - {e}"
                            )
                            event_type = None
                            data_buffer = ""
                            continue

        except httpx.RequestError as e:
            logger.warning(f"SSE stream connection error: {e}")
            # For SSE streaming, we don't want to raise an error that stops the stream
            # Instead, let the caller handle reconnection
            return

    async def stream_elements(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream all elements as they change in real-time.

        Yields:
            Element data dictionaries as they are created, updated, or deleted
        """
        # Add diagnostic parameters like cs-base client does
        params = {
            "ts": str(int(time.time() * 1000)),  # Current timestamp in milliseconds
            "cid": self.client_id,  # Client ID for server diagnostics
        }
        async for event in self._stream_sse_events("/graph/sse/stream", params=params):
            yield event

    async def stream_element_by_id(
        self, element_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream changes for a specific element in real-time.

        Args:
            element_id: The ID of the element to monitor

        Yields:
            Element data dictionaries when the specified element changes
        """
        # Use filters to target specific element
        filters = [{"where": {"id": element_id}}]
        params = {"filters": base64.b64encode(json.dumps(filters).encode()).decode()}
        async for event in self._stream_sse_events("/graph/sse/stream", params=params):
            yield event

    async def stream_elements_by_class_id(
        self, class_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream elements of a specific class as they change in real-time.

        Args:
            class_id: The class ID to filter by

        Yields:
            Element data dictionaries for elements matching the class ID
        """
        # Use filters to target specific class
        filters = [{"classId": class_id}]
        params = {"filters": base64.b64encode(json.dumps(filters).encode()).decode()}
        async for event in self._stream_sse_events("/graph/sse/stream", params=params):
            yield event

    async def stream_schema(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream schema changes in real-time.

        Yields:
            Schema change events as dictionaries
        """
        # Schema changes are not directly supported by the current SSE implementation
        # This would need to be implemented on the server side
        raise NotImplementedError(
            "Schema streaming is not currently supported by the SSE API"
        )

    async def stream_query(
        self, query: Dict[str, Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream results of a continuous query in real-time.

        Args:
            query: Query object to execute continuously

        Yields:
            Query result events as they occur
        """
        # Query streaming is not directly supported by the current SSE implementation
        # This would need to be implemented on the server side
        raise NotImplementedError(
            "Query streaming is not currently supported by the SSE API"
        )

    async def stream_health(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream health status updates in real-time.

        Yields:
            Health status events as dictionaries
        """
        # Health streaming is not directly supported by the current SSE implementation
        # This would need to be implemented on the server side
        raise NotImplementedError(
            "Health streaming is not currently supported by the SSE API"
        )

    async def stream_events(self) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream all graph events in real-time.

        Yields:
            All graph event data as dictionaries
        """
        async for event in self._stream_sse_events("/graph/sse/stream"):
            yield event


class RestDataStorage(IDataStorage):
    """
    REST-based data storage implementation that communicates with the TypeScript Graph API.

    This class implements the IDataStorage interface to provide seamless integration
    with the existing ElementStore while communicating with a remote API.
    """

    def __init__(self, config: Optional[RestClientConfig] = None):
        """
        Initialize REST data storage.

        Args:
            config: Configuration for the REST client
        """
        super().__init__()
        self.config = config or RestClientConfig()
        self.client: Optional[RestGraphApiClient] = None

    async def init(self) -> None:
        """Initialize the REST client."""
        self.client = RestGraphApiClient(self.config)
        logger.info(
            f"Initialized REST data storage with base URL: {self.config.base_url}"
        )

    async def close(self) -> None:
        """Close the REST client."""
        if self.client:
            await self.client.close()
            self.client = None

    async def load_data(self) -> Optional[Dict[str, BaseElement]]:
        """
        Load all data from the remote API.

        Returns:
            Dictionary of BaseElement objects keyed by ID
        """
        if not self.client:
            raise RuntimeError("RestDataStorage not initialized. Call init() first.")

        try:
            # Get all elements from API
            elements_data = await self.client.get_all_elements()

            if not elements_data:
                logger.info("No elements found in remote storage")
                return {}

            # Convert API data to BaseElement objects
            elements = {}
            for element_id, element_data in elements_data.items():
                try:
                    # Create appropriate element type based on data
                    element = self._create_element_from_data(element_data)
                    elements[element_id] = element
                except Exception as e:
                    logger.warning(f"Failed to create element {element_id}: {e}")
                    continue

            logger.info(f"Loaded {len(elements)} elements from remote storage")
            return elements

        except Exception as e:
            logger.error(f"Failed to load data from remote storage: {e}")
            raise

    async def create_elements(self, elements: List[BaseElement]) -> None:
        """
        Create elements in the remote storage.

        Args:
            elements: List of BaseElement objects to create
        """
        if not self.client:
            raise RuntimeError("RestDataStorage not initialized. Call init() first.")

        # Convert BaseElement objects to API format
        elements_data = [self._serialize_element(element) for element in elements]

        try:
            await self.client.create_elements(elements_data)
            logger.info(f"Created {len(elements)} elements in remote storage")
        except Exception as e:
            logger.error(f"Failed to create elements in remote storage: {e}")
            raise

    async def update_elements(self, elements: List[BaseElement]) -> None:
        """
        Update elements in the remote storage.

        Args:
            elements: List of BaseElement objects to update
        """
        if not self.client:
            raise RuntimeError("RestDataStorage not initialized. Call init() first.")

        # Convert BaseElement objects to API format
        elements_data = [self._serialize_element(element) for element in elements]

        try:
            await self.client.create_elements(
                elements_data
            )  # POST handles both create and update
            logger.info(f"Updated {len(elements)} elements in remote storage")
        except Exception as e:
            logger.error(f"Failed to update elements in remote storage: {e}")
            raise

    async def patch_elements(self, elements: List[BaseElement]) -> None:
        """
        Partially update elements in the remote storage.

        Args:
            elements: List of BaseElement objects to patch
        """
        if not self.client:
            raise RuntimeError("RestDataStorage not initialized. Call init() first.")

        # Convert BaseElement objects to API format
        elements_data = [self._serialize_element(element) for element in elements]

        try:
            await self.client.patch_elements(elements_data)
            logger.info(f"Patched {len(elements)} elements in remote storage")
        except Exception as e:
            logger.error(f"Failed to patch elements in remote storage: {e}")
            raise

    async def delete_elements(self, elements: List[BaseElement]) -> None:
        """
        Delete elements from the remote storage.

        Args:
            elements: List of BaseElement objects to delete
        """
        if not self.client:
            raise RuntimeError("RestDataStorage not initialized. Call init() first.")

        # Extract element IDs
        element_ids = [element.id for element in elements]

        try:
            await self.client.delete_elements(element_ids)
            logger.info(f"Deleted {len(elements)} elements from remote storage")
        except Exception as e:
            logger.error(f"Failed to delete elements from remote storage: {e}")
            raise

    async def get_elements_by_class_id(self, class_id: str) -> Dict[str, BaseElement]:
        """
        Get elements by class ID from the remote storage.

        Args:
            class_id: The class ID to filter by

        Returns:
            Dictionary of BaseElement objects keyed by ID that match the class
        """
        if not self.client:
            raise RuntimeError("RestDataStorage not initialized. Call init() first.")

        try:
            # Get elements by class ID from API
            result = await self.client.get_elements_by_class_id(class_id)
            elements_data = result.get("data", [])

            if not elements_data:
                logger.info(f"No elements found for class ID: {class_id}")
                return {}

            # Convert API data to BaseElement objects
            elements = {}
            for element_data in elements_data:
                try:
                    element_id = element_data.get("id")
                    if element_id:
                        element = self._create_element_from_data(element_data)
                        elements[element_id] = element
                except Exception as e:
                    logger.warning(f"Failed to create element from data: {e}")
                    continue

            logger.info(
                f"Found {len(elements)} elements for class ID '{class_id}' from remote storage"
            )
            return elements

        except Exception as e:
            logger.error(f"Failed to get elements by class ID from remote storage: {e}")
            raise

    async def reset(self) -> None:
        """
        Reset/clear all data in the remote storage.

        Note: This implementation loads all elements and deletes them individually
        as the API doesn't provide a bulk reset endpoint.
        """
        if not self.client:
            raise RuntimeError("RestDataStorage not initialized. Call init() first.")

        try:
            # Get all elements
            elements_data = await self.client.get_all_elements()

            if elements_data:
                # Delete all elements
                element_ids = list(elements_data.keys())
                await self.client.delete_elements(element_ids)
                logger.info(
                    f"Reset remote storage by deleting {len(element_ids)} elements"
                )
            else:
                logger.info("Remote storage is already empty")

        except Exception as e:
            logger.error(f"Failed to reset remote storage: {e}")
            raise

    def _serialize_element(self, element: BaseElement) -> Dict[str, Any]:
        """
        Convert a BaseElement to API-compatible format.

        Args:
            element: BaseElement to serialize

        Returns:
            Dictionary representation suitable for API
        """
        # Get properties dictionary
        properties_dict = {}
        if hasattr(element, "properties") and element.properties:
            # Handle both Pydantic and dict-like properties
            try:
                # Try Pydantic model_dump if available - use getattr to avoid type checker issues
                model_dump_method = getattr(element.properties, "model_dump", None)
                if model_dump_method and callable(model_dump_method):
                    properties_dict = model_dump_method()
                elif hasattr(element.properties, "__dict__"):
                    properties_dict = {
                        k: v
                        for k, v in element.properties.__dict__.items()
                        if not k.startswith("_")
                    }
                else:
                    # Fallback to dict-like access
                    properties_dict = dict(element.properties)
            except Exception as e:
                logger.warning(f"Failed to serialize properties: {e}")
                # Last resort: try to convert to dict
                try:
                    properties_dict = dict(element.properties)
                except Exception:
                    properties_dict = {}

        # Ensure required fields are present - use Python naming convention
        serialized = {
            "id": element.id,
            "type": str(element.type),  # Convert enum to string
            "classId": element.class_id,  # Map Python snake_case to API camelCase
            "properties": properties_dict,
            "source": getattr(element, "source", None),
        }

        # Add optional fields if present - use Python naming convention
        if hasattr(element, "to_id") and element.to_id:
            serialized["toId"] = element.to_id
        if hasattr(element, "from_id") and element.from_id:
            serialized["fromId"] = element.from_id
        if hasattr(element, "attributes") and element.attributes:
            serialized["attributes"] = element.attributes
        if hasattr(element, "temp") and element.temp is not None:
            serialized["_temp"] = element.temp
        if hasattr(element, "flat") and element.flat:
            serialized["_flat"] = element.flat

        return serialized

    def _create_element_from_data(self, data: Dict[str, Any]) -> BaseElement:
        """
        Create a BaseElement from API data.

        Args:
            data: Element data from API

        Returns:
            BaseElement instance
        """
        from .base_element import ElementDetails, NodeTypes, Props
        from .edge import Edge
        from .meta import MetaNode, MetaNodeProperties
        from .node import Node

        # Extract properties
        properties_data = data.get("properties", {})

        # Create appropriate properties object based on element type
        element_type = data.get("type", "node")
        if element_type == "meta":
            properties = MetaNodeProperties(**properties_data)
        else:
            properties = Props(**properties_data)

        # Create ElementDetails
        details = ElementDetails(
            id=data["id"],
            class_id=data["classId"],
            type=NodeTypes(data["type"]),
            properties=properties,
            to_id=data.get("toId"),
            from_id=data.get("fromId"),
            source=data.get("source"),
            temp=data.get("temp"),
            attributes=data.get("attributes"),
            flat=data.get("flat"),
        )

        # Create element
        if element_type == "edge":
            return Edge(details)
        elif element_type == "meta":
            return MetaNode(details)
        else:
            return Node(details)


# Configuration class for RestDataStorage
@dataclass
class RestDataStorageConfig(IDataStorageConfig):
    """Configuration for REST data storage."""

    type: str = "rest"
    base_url: str = "http://localhost:9800"
    timeout: float = 30.0
    max_retries: int = 3
    verify_ssl: bool = True
    headers: Optional[Dict[str, str]] = None

    def to_rest_config(self) -> RestClientConfig:
        """Convert to RestClientConfig."""
        return RestClientConfig(
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            verify_ssl=self.verify_ssl,
            headers=self.headers,
        )


class SynchronizedDataStorage(RestDataStorage):
    """
    Synchronized data storage that combines REST API calls with SSE streaming for real-time sync.

    This class extends RestDataStorage to add:
    - Real-time SSE event streaming for automatic server updates
    - Local in-memory cache for immediate operations
    - Server-wins conflict resolution
    - Bidirectional sync (local changes sync to server, server changes sync to local)
    - JSON store preparation for future offline mode
    """

    def __init__(self, config: Optional[RestClientConfig] = None):
        """
        Initialize synchronized data storage.

        Args:
            config: Configuration for the REST client
        """
        super().__init__(config)
        self._local_cache: Dict[str, BaseElement] = {}
        self._sse_task: Optional[asyncio.Task] = None
        self._sync_lock = asyncio.Lock()
        self._is_syncing = False
        self._json_store_path: Optional[str] = None  # For future offline mode

    async def init(self) -> None:
        """Initialize the synchronized storage with SSE streaming."""
        await super().init()

        # Load initial data from server
        initial_data = await self.load_data()
        if initial_data:
            self._local_cache = initial_data.copy()

        # Start SSE streaming for real-time updates
        self._sse_task = asyncio.create_task(self._start_sse_streaming())
        logger.info("Initialized synchronized data storage with SSE streaming")

    async def close(self) -> None:
        """Close the synchronized storage and stop SSE streaming."""
        if self._sse_task and not self._sse_task.done():
            self._sse_task.cancel()
            try:
                await self._sse_task
            except asyncio.CancelledError:
                pass

        await super().close()

    async def _start_sse_streaming(self) -> None:
        """Start SSE streaming for real-time updates."""
        if not self.client:
            logger.error("Cannot start SSE streaming: client not initialized")
            return

        while True:  # Keep trying to reconnect
            try:
                logger.info("Starting SSE streaming for real-time updates")
                async for event in self.client.stream_elements():
                    await self._handle_sse_event(event)
            except Exception as e:
                logger.warning(f"SSE streaming error: {e}. Will retry in 5 seconds...")
                await asyncio.sleep(5)  # Wait before retrying
                continue

    async def _handle_sse_event(self, event: Dict[str, Any]) -> None:
        """
        Handle incoming SSE events and update local cache with server-wins resolution.

        Args:
            event: SSE event data
        """
        async with self._sync_lock:
            event_type = event.get("type")
            event_data = event.get("data", {})

            logger.debug(f"Handling SSE event: {event_type}")

            if event_type == "INITIAL_DATA":
                # Full data sync - replace local cache only if it's empty (initial load)
                elements_data = event_data.get("elements", {})
                if not self._local_cache:  # Only replace if cache is empty
                    self._local_cache = {}
                    for element_id, element_data in elements_data.items():
                        try:
                            element = self._create_element_from_data(element_data)
                            self._local_cache[element_id] = element
                        except Exception as e:
                            logger.warning(
                                f"Failed to create element {element_id} from SSE data: {e}"
                            )
                    logger.info(
                        f"Synchronized {len(self._local_cache)} elements from INITIAL_DATA event"
                    )
                else:
                    logger.debug(
                        f"Ignoring INITIAL_DATA event - cache already has {len(self._local_cache)} elements"
                    )

            elif event_type == "BATCH":
                # Batch of element updates
                elements_data = event_data.get("elements", [])
                for element_data in elements_data:
                    try:
                        element = self._create_element_from_data(element_data)
                        self._local_cache[element.id] = (
                            element  # Server-wins: always update
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to create element from BATCH SSE data: {e}"
                        )
                logger.debug(
                    f"Applied {len(elements_data)} element updates from BATCH event"
                )

            elif event_type == "DELETE":
                # Element deletions
                element_ids = event_data.get("elementIds", [])
                for element_id in element_ids:
                    if element_id in self._local_cache:
                        del self._local_cache[element_id]
                logger.debug(f"Deleted {len(element_ids)} elements from DELETE event")

            else:
                logger.warning(f"Unknown SSE event type: {event_type}")

    async def load_data(self) -> Optional[Dict[str, BaseElement]]:
        """
        Load data from server and update local cache.

        Returns:
            Dictionary of BaseElement objects keyed by ID
        """
        # Use REST API to load data
        server_data = await super().load_data()

        # Update local cache with server data (server-wins)
        async with self._sync_lock:
            if server_data:
                self._local_cache = server_data.copy()
            else:
                self._local_cache = {}

        return self._local_cache.copy()

    async def create_elements(self, elements: List[BaseElement]) -> None:
        """
        Create elements locally and sync to server.

        Args:
            elements: List of BaseElement objects to create
        """
        # Update local cache immediately
        async with self._sync_lock:
            for element in elements:
                self._local_cache[element.id] = element

        # Sync to server (server-wins resolution will handle conflicts)
        try:
            await super().create_elements(elements)
        except Exception as e:
            logger.warning(f"Failed to sync element creation to server: {e}")
            # Local cache remains updated - could implement retry logic here

    async def update_elements(self, elements: List[BaseElement]) -> None:
        """
        Update elements locally and sync to server.

        Args:
            elements: List of BaseElement objects to update
        """
        # Update local cache immediately
        async with self._sync_lock:
            for element in elements:
                self._local_cache[element.id] = element

        # Sync to server
        try:
            await super().update_elements(elements)
        except Exception as e:
            logger.error(f"Failed to sync element updates to server: {e}")
            raise

    async def patch_elements(self, elements: List[BaseElement]) -> None:
        """
        Patch elements locally and sync to server.

        Args:
            elements: List of BaseElement objects to patch
        """
        # Update local cache immediately
        async with self._sync_lock:
            for element in elements:
                self._local_cache[element.id] = element

        # Sync to server
        try:
            await super().patch_elements(elements)
        except Exception as e:
            logger.error(f"Failed to sync element patches to server: {e}")
            raise

    async def delete_elements(self, elements: List[BaseElement]) -> None:
        """
        Delete elements locally and sync to server.

        Args:
            elements: List of BaseElement objects to delete
        """
        # Remove from local cache immediately
        async with self._sync_lock:
            for element in elements:
                if element.id in self._local_cache:
                    del self._local_cache[element.id]

        # Sync to server
        try:
            await super().delete_elements(elements)
        except Exception as e:
            logger.error(f"Failed to sync element deletions to server: {e}")
            raise

    async def get_elements_by_class_id(self, class_id: str) -> Dict[str, BaseElement]:
        """
        Get elements by class ID from local cache.

        Args:
            class_id: The class ID to filter by

        Returns:
            Dictionary of BaseElement objects keyed by ID that match the class
        """
        async with self._sync_lock:
            return {
                element_id: element
                for element_id, element in self._local_cache.items()
                if element.class_id == class_id
            }

    async def reset(self) -> None:
        """
        Reset local cache and server data.
        """
        async with self._sync_lock:
            self._local_cache.clear()

        await super().reset()

    def get_local_cache_snapshot(self) -> Dict[str, BaseElement]:
        """
        Get a snapshot of the current local cache for debugging/inspection.

        Returns:
            Copy of the local cache
        """
        return self._local_cache.copy()

    def set_json_store_path(self, path: str) -> None:
        """
        Set the path for JSON store (for future offline mode).

        Args:
            path: File path for JSON storage
        """
        self._json_store_path = path
        logger.info(f"Set JSON store path: {path}")

    async def save_to_json_store(self) -> None:
        """
        Save current local cache to JSON store (for future offline mode).
        """
        if not self._json_store_path:
            logger.warning("JSON store path not set")
            return

        try:
            # Convert elements to serializable format
            serializable_data = {}
            for element_id, element in self._local_cache.items():
                serializable_data[element_id] = self._serialize_element(element)

            # Save to JSON file
            import json

            with open(self._json_store_path, "w") as f:
                json.dump(serializable_data, f, indent=2, default=str)

            logger.info(f"Saved {len(serializable_data)} elements to JSON store")
        except Exception as e:
            logger.error(f"Failed to save to JSON store: {e}")
            raise

    async def load_from_json_store(self) -> None:
        """
        Load data from JSON store into local cache (for future offline mode).
        """
        if not self._json_store_path:
            logger.warning("JSON store path not set")
            return

        try:
            import json

            with open(self._json_store_path) as f:
                data = json.load(f)

            # Convert back to BaseElement objects
            loaded_elements = {}
            for element_id, element_data in data.items():
                try:
                    element = self._create_element_from_data(element_data)
                    loaded_elements[element_id] = element
                except Exception as e:
                    logger.warning(
                        f"Failed to load element {element_id} from JSON store: {e}"
                    )

            async with self._sync_lock:
                self._local_cache = loaded_elements

            logger.info(f"Loaded {len(loaded_elements)} elements from JSON store")
        except FileNotFoundError:
            logger.info("JSON store file not found, starting with empty cache")
        except Exception as e:
            logger.error(f"Failed to load from JSON store: {e}")
            raise


# Configuration class for SynchronizedDataStorage
@dataclass
class SynchronizedDataStorageConfig(IDataStorageConfig):
    """Configuration for synchronized data storage."""

    type: str = "synchronized"
    base_url: str = "http://localhost:9800"
    timeout: float = 30.0
    max_retries: int = 3
    verify_ssl: bool = True
    headers: Optional[Dict[str, str]] = None
    json_store_path: Optional[str] = None

    def to_rest_config(self) -> RestClientConfig:
        """Convert to RestClientConfig."""
        return RestClientConfig(
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
            verify_ssl=self.verify_ssl,
            headers=self.headers,
        )
