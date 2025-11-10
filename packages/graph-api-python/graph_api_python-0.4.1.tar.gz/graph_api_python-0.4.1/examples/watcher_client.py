#!/usr/bin/env python3
"""
Graph API Watcher Client

A real-time watcher client that connects to the Graph API server via SSE (Server-Sent Events)
and displays user-friendly messages for all graph changes.

Usage:
    uv run python examples/watcher_client.py

This client will:
- Connect to the SSE stream at /graph/sse/stream
- Display formatted messages for all graph events
- Show property changes in a readable format
- Handle create, update, and delete operations
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from graph_api.rest_client import RestClientConfig, RestGraphApiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GraphWatcherClient:
    """
    Real-time graph watcher client that displays user-friendly messages for graph events.
    """

    def __init__(self, base_url: str = "http://localhost:9800", timeout: float = 30.0):
        """
        Initialize the watcher client.

        Args:
            base_url: Base URL of the Graph API server
            timeout: Request timeout in seconds
        """
        self.config = RestClientConfig(base_url=base_url, timeout=timeout)
        self.client: Optional[RestGraphApiClient] = None
        self.is_running = False

    async def start(self) -> None:
        """Start the watcher client."""
        self.client = RestGraphApiClient(self.config)
        self.is_running = True

        logger.info("🚀 Starting Graph Watcher Client")
        logger.info(f"📡 Connecting to: {self.config.base_url}")

        # Load and display store statistics
        await self._display_store_statistics()

        logger.info("📝 Watching for graph events... (Press Ctrl+C to stop)")
        print()

        try:
            await self._watch_events()
        except KeyboardInterrupt:
            logger.info("🛑 Watcher client stopped by user")
        except Exception as e:
            logger.error(f"❌ Watcher client error: {e}")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the watcher client."""
        self.is_running = False
        if self.client:
            await self.client.close()
            self.client = None

    async def _display_store_statistics(self) -> None:
        """Load and display store statistics."""
        if not self.client:
            raise RuntimeError("Client not initialized")

        try:
            # Load all elements
            all_elements = await self.client.get_all_elements()

            # Calculate statistics
            nodes = sum(1 for e in all_elements.values() if e.get("type") == "node")
            edges = sum(1 for e in all_elements.values() if e.get("type") == "edge")
            meta_nodes = sum(
                1 for e in all_elements.values() if e.get("type") == "meta"
            )

            # Count unique classes
            classes = {
                e.get("classId") for e in all_elements.values() if e.get("classId")
            }

            # Display statistics
            logger.info("📊 Store Statistics:")
            logger.info(f"   Total Elements: {len(all_elements)}")
            logger.info(f"   Nodes: {nodes}")
            logger.info(f"   Edges: {edges}")
            logger.info(f"   Meta Nodes: {meta_nodes}")
            logger.info(f"   Unique Classes: {len(classes)}")
            if classes:
                logger.info(f"   Classes: {', '.join(sorted(classes))}")

        except Exception as e:
            logger.warning(f"⚠️  Failed to load store statistics: {e}")

    async def _watch_events(self) -> None:
        """Watch for SSE events and display formatted messages."""
        if not self.client:
            raise RuntimeError("Client not initialized")

        async for event in self.client.stream_elements():
            try:
                await self._handle_event(event)
            except Exception as e:
                import traceback

                logger.error(f"Error handling event: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.debug(f"Event was: {event}")
                continue

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        """
        Handle an incoming SSE event and display user-friendly messages.

        Args:
            event: The SSE event data (contains 'type' and other event-specific fields)
        """
        try:
            event_type = event.get("type")
            timestamp = datetime.now().strftime("%H:%M:%S")
            if event_type == "INITIAL_DATA":
                # INITIAL_DATA: has 'elements' array and 'count'
                elements = event.get("elements", [])
                count = event.get("count", 0)
                await self._handle_initial_data(
                    {"elements": elements, "count": count}, timestamp
                )

            elif event_type == "BATCH":
                # BATCH: has 'elements' array
                elements = event.get("elements", [])
                await self._handle_batch_update({"elements": elements}, timestamp)

            elif event_type and event_type.upper() == "DELETE":
                # DELETE: has 'elementIds' array or 'elements' array or single 'elementId' or 'id'
                await self._handle_delete(event, timestamp)

            elif event_type == "CREATE":
                # CREATE: the event itself is the element data
                element_data = {k: v for k, v in event.items() if k != "type"}
                if element_data:
                    await self._display_element_change(
                        element_data, timestamp, "created"
                    )

            elif event_type == "UPDATE":
                # UPDATE: the event itself is the element data
                element_data = {k: v for k, v in event.items() if k != "type"}
                if element_data:
                    await self._display_element_change(
                        element_data, timestamp, "updated"
                    )

            else:
                print(f"DEBUG: Unknown event type: {event_type}, full event: {event}")
        except Exception as e:
            logger.error(f"Error in _handle_event: {e}, event: {event}")
            raise

    async def _handle_initial_data(self, data: Any, timestamp: str) -> None:
        """
        Handle initial data load event.

        Args:
            data: Event data containing elements (can be dict or array)
            timestamp: Formatted timestamp
        """
        # Handle both dict and array formats
        if isinstance(data, dict):
            elements = data.get("elements", {})
            if isinstance(elements, dict):
                count = len(elements)
                if count > 0:
                    print(f"📦 {timestamp} | Initial data loaded: {count} elements")
                    # Show a sample of the loaded elements
                    sample_ids = list(elements.keys())[:3]  # Show first 3
                    for element_id in sample_ids:
                        element = elements[element_id]
                        class_id = element.get("classId", "unknown")
                        print(f"   • Node {element_id} of type {class_id}")

                    if count > 3:
                        print(f"   ... and {count - 3} more elements")
                else:
                    print(f"📦 {timestamp} | Initial data loaded: empty graph")
            else:
                # elements might be a list
                logger.debug(
                    f"INITIAL_DATA elements field is list, not dict: {type(elements)}"
                )
        elif isinstance(data, list):
            # INITIAL_DATA might be an array directly
            count = len(data)
            if count > 0:
                print(f"📦 {timestamp} | Initial data loaded: {count} elements")
                # Show a sample
                for element in data[:3]:
                    if isinstance(element, dict):
                        element_id = element.get("id", "unknown")
                        class_id = element.get("classId", "unknown")
                        print(f"   • Node {element_id} of type {class_id}")

                if count > 3:
                    print(f"   ... and {count - 3} more elements")
            else:
                print(f"📦 {timestamp} | Initial data loaded: empty graph")
        else:
            logger.debug(f"Unexpected INITIAL_DATA format: {type(data)}")

    async def _handle_batch_update(self, data: Dict[str, Any], timestamp: str) -> None:
        """
        Handle batch element update event.

        Args:
            data: Event data containing elements array
            timestamp: Formatted timestamp
        """
        elements = data.get("elements", [])

        for element_data in elements:
            await self._display_element_change(element_data, timestamp, "updated")

    async def _handle_delete(self, data: Dict[str, Any], timestamp: str) -> None:
        """
        Handle element deletion event.

        Args:
            data: Event data containing element IDs or elements array
            timestamp: Formatted timestamp
        """
        # Check for elements array (with full data)
        elements = data.get("elements", [])
        if not elements:
            # Check in 'data' subdict
            data_sub = data.get("data", {})
            if isinstance(data_sub, dict):
                elements = data_sub.get("elements", [])

        if elements:
            for element in elements:
                if isinstance(element, dict):
                    element_id = element.get("id", "unknown")
                    class_id = element.get("classId", "unknown")
                    properties = element.get("properties", {})
                    name = (
                        properties.get("name") or properties.get("title") or element_id
                    )
                    print(
                        f"🗑️  {timestamp} | Node '{name}' (ID: {element_id}, Type: {class_id}) was deleted"
                    )
        else:
            # Fallback to elementIds array
            element_ids = data.get("elementIds", [])
            if not element_ids:
                # Check in 'data'
                data_sub = data.get("data", {})
                if isinstance(data_sub, dict):
                    element_ids = data_sub.get("elementIds", [])
                # Check for single
                if not element_ids:
                    single_id = data.get("elementId") or data.get("id")
                    if single_id:
                        element_ids = [single_id]
                    elif isinstance(data_sub, dict):
                        single_id = data_sub.get("elementId") or data_sub.get("id")
                        if single_id:
                            element_ids = [single_id]
            for element_id in element_ids:
                print(f"🗑️  {timestamp} | Node {element_id} was deleted")

    async def _display_element_change(
        self, element_data: Dict[str, Any], timestamp: str, action: str
    ) -> None:
        """
        Display a user-friendly message for an element change.

        Args:
            element_data: The element data from the event
            timestamp: Formatted timestamp
            action: The action performed (created, updated, etc.)
        """
        element_id = element_data.get("id", "unknown")
        class_id = element_data.get("classId", "unknown")
        properties = element_data.get("properties", {})

        # Format the main message
        if action == "updated":
            prop_str = self._format_properties_for_line(properties)
            print(
                f"🔄 {timestamp} | Node {element_id} of type {class_id} updated: {prop_str}"
            )
        elif action == "created":
            print(f"✨ {timestamp} | Node {element_id} of type {class_id} was created")
            # Show property details for created elements
            if properties:
                await self._display_property_changes(
                    properties, element_id, class_id, timestamp
                )
        else:
            print(f"📝 {timestamp} | Node {element_id} of type {class_id} was {action}")
            # Show property details for other actions
            if properties:
                await self._display_property_changes(
                    properties, element_id, class_id, timestamp
                )

    async def _display_property_changes(
        self, properties: Dict[str, Any], element_id: str, class_id: str, timestamp: str
    ) -> None:
        """
        Display detailed property changes in a user-friendly format.

        Args:
            properties: Element properties
            element_id: Element ID
            class_id: Element class
            timestamp: Formatted timestamp
        """
        # Show key properties in a readable format
        important_props = [
            "name",
            "title",
            "description",
            "status",
            "role",
            "age",
            "email",
        ]

        shown_props = []
        for prop_name in important_props:
            if prop_name in properties:
                value = properties[prop_name]
                # Format the value nicely
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                elif isinstance(value, (int, float)):
                    value = str(value)
                elif isinstance(value, bool):
                    value = "true" if value else "false"
                elif value is None:
                    value = "null"

                shown_props.append(f"{prop_name}={value}")

        if shown_props:
            print(f"   Properties: {', '.join(shown_props)}")

        # Count total properties
        total_props = len(properties)
        if total_props > len(shown_props):
            extra_count = total_props - len(shown_props)
            print(f"   + {extra_count} additional properties")

        # Special handling for common property changes
        if "name" in properties:
            print(f"   📛 Name: {properties['name']}")
        if "status" in properties:
            print(f"   📊 Status: {properties['status']}")
        if "role" in properties:
            print(f"   👤 Role: {properties['role']}")
        if "age" in properties and isinstance(properties["age"], (int, float)):
            print(f"   🎂 Age: {properties['age']}")

    def _format_properties_for_line(self, properties: Dict[str, Any]) -> str:
        """
        Format properties into a condensed single-line string for update messages.

        Args:
            properties: Element properties

        Returns:
            Formatted string like "name='New Name', status='active'"
        """
        if not properties:
            return "no properties"

        # Properties to ignore in the log
        ignore_props = {"created_time", "updated_time"}

        formatted_props = []
        for key, value in properties.items():
            if key in ignore_props:
                continue

            # Format the value
            if isinstance(value, str):
                if len(value) > 30:
                    value = value[:27] + "..."
                formatted_value = f"'{value}'"
            elif isinstance(value, bool):
                formatted_value = "true" if value else "false"
            elif isinstance(value, (int, float)):
                formatted_value = str(value)
            elif value is None:
                formatted_value = "null"
            else:
                formatted_value = str(value)
                if len(formatted_value) > 30:
                    formatted_value = formatted_value[:27] + "..."

            formatted_props.append(f"{key}={formatted_value}")

        if not formatted_props:
            return "no properties"

        return ", ".join(formatted_props)


async def main():
    """Main function to run the watcher client."""
    import argparse

    parser = argparse.ArgumentParser(description="Graph API Watcher Client")
    parser.add_argument(
        "--url",
        default="http://localhost:9800",
        help="Graph API server URL (default: http://localhost:9800)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )

    args = parser.parse_args()

    watcher = GraphWatcherClient(base_url=args.url, timeout=args.timeout)

    try:
        await watcher.start()
    except Exception as e:
        logger.error(f"Failed to start watcher: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
