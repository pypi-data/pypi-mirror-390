"""
SSE (Server-Sent Events) Examples for Graph API REST Client

This module demonstrates how to use the Server-Sent Events functionality
of the Graph API client for real-time streaming of graph data.

Features demonstrated:
- Streaming all elements
- Streaming specific elements by ID
- Streaming elements by class ID
- Streaming schema changes
- Streaming query results
- Streaming health status
- Streaming all graph events
"""

import asyncio
import logging

from graph_api.rest_client import RestGraphApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def stream_elements_example():
    """
    Example: Stream all elements in real-time.

    This will continuously monitor all graph elements and print changes
    as they occur.
    """
    print("=== Streaming All Elements ===")

    async with RestGraphApiClient() as client:
        try:
            count = 0
            async for event in client.stream_elements():
                count += 1
                print(f"Event {count}: {event}")

                # Limit output for demo
                if count >= 5:
                    print("Stopping after 5 events...")
                    break

        except Exception as e:
            logger.error(f"Error streaming elements: {e}")


async def stream_element_by_id_example(element_id: str = "example-element-1"):
    """
    Example: Stream changes for a specific element.

    Args:
        element_id: ID of the element to monitor
    """
    print(f"=== Streaming Element: {element_id} ===")

    async with RestGraphApiClient() as client:
        try:
            count = 0
            async for event in client.stream_element_by_id(element_id):
                count += 1
                print(f"Event {count}: {event}")

                # Limit output for demo
                if count >= 3:
                    print("Stopping after 3 events...")
                    break

        except Exception as e:
            logger.error(f"Error streaming element {element_id}: {e}")


async def stream_elements_by_class_id_example(class_id: str = "Person"):
    """
    Example: Stream elements of a specific class.

    Args:
        class_id: Class ID to filter by
    """
    print(f"=== Streaming Elements by Class: {class_id} ===")

    async with RestGraphApiClient() as client:
        try:
            count = 0
            async for event in client.stream_elements_by_class_id(class_id):
                count += 1
                print(f"Event {count}: {event}")

                # Limit output for demo
                if count >= 3:
                    print("Stopping after 3 events...")
                    break

        except Exception as e:
            logger.error(f"Error streaming elements by class {class_id}: {e}")


async def stream_schema_example():
    """
    Example: Stream schema changes in real-time.

    This monitors changes to the graph schema definitions.
    """
    print("=== Streaming Schema Changes ===")

    async with RestGraphApiClient() as client:
        try:
            count = 0
            async for event in client.stream_schema():
                count += 1
                print(f"Schema Event {count}: {event}")

                # Limit output for demo
                if count >= 2:
                    print("Stopping after 2 events...")
                    break

        except Exception as e:
            logger.error(f"Error streaming schema: {e}")


async def stream_query_example():
    """
    Example: Stream results of a continuous query.

    This demonstrates streaming query results as data changes.
    """
    print("=== Streaming Query Results ===")

    # Example query: Find all nodes with a specific property
    query = {
        "operations": [
            {"type": "match", "classId": "Person", "where": {"name": {"$exists": True}}}
        ]
    }

    async with RestGraphApiClient() as client:
        try:
            count = 0
            async for event in client.stream_query(query):
                count += 1
                print(f"Query Event {count}: {event}")

                # Limit output for demo
                if count >= 3:
                    print("Stopping after 3 events...")
                    break

        except Exception as e:
            logger.error(f"Error streaming query: {e}")


async def stream_health_example():
    """
    Example: Stream health status updates.

    This monitors the health of the graph service.
    """
    print("=== Streaming Health Status ===")

    async with RestGraphApiClient() as client:
        try:
            count = 0
            async for event in client.stream_health():
                count += 1
                print(f"Health Event {count}: {event}")

                # Limit output for demo
                if count >= 2:
                    print("Stopping after 2 events...")
                    break

        except Exception as e:
            logger.error(f"Error streaming health: {e}")


async def stream_events_example():
    """
    Example: Stream all graph events.

    This captures all types of events happening in the graph.
    """
    print("=== Streaming All Graph Events ===")

    async with RestGraphApiClient() as client:
        try:
            count = 0
            async for event in client.stream_events():
                count += 1
                print(f"Graph Event {count}: {event}")

                # Limit output for demo
                if count >= 5:
                    print("Stopping after 5 events...")
                    break

        except Exception as e:
            logger.error(f"Error streaming events: {e}")


async def concurrent_streaming_example():
    """
    Example: Run multiple streams concurrently.

    This demonstrates how to monitor different aspects of the graph
    simultaneously using asyncio tasks.
    """
    print("=== Concurrent Streaming Example ===")

    async def monitor_stream(name: str, stream_func):
        """Helper to monitor a stream and print events."""
        try:
            count = 0
            async for event in stream_func():
                count += 1
                print(f"{name} Event {count}: {event}")
                if count >= 2:  # Limit per stream
                    break
        except Exception as e:
            logger.error(f"Error in {name}: {e}")

    async with RestGraphApiClient() as client:
        # Create tasks for different streams
        tasks = [
            asyncio.create_task(monitor_stream("Health", client.stream_health)),
            asyncio.create_task(monitor_stream("Schema", client.stream_schema)),
        ]

        # Run tasks concurrently with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks), timeout=10.0
            )  # Reduced timeout
        except asyncio.TimeoutError:
            print("Concurrent streaming demo completed (timeout)")
        except Exception as e:
            logger.error(f"Concurrent streaming failed: {e}")


async def sse_connectivity_test():
    """
    Test SSE endpoint connectivity without streaming.

    This checks if SSE endpoints are accessible and return proper responses.
    """
    print("=== SSE Connectivity Test ===")

    async with RestGraphApiClient() as client:
        endpoints = [
            "/graph/sse/health",
            "/graph/sse/elements",
            "/graph/sse/schema",
            "/graph/sse/events",
        ]

        for endpoint in endpoints:
            try:
                # Test basic connectivity by making a HEAD request or checking response headers
                response = await client.client.head(endpoint)
                print(f"{endpoint}: HTTP {response.status_code}")
                if response.status_code == 200:
                    content_type = response.headers.get("content-type", "")
                    if "text/event-stream" in content_type:
                        print(
                            f"  ✓ SSE endpoint confirmed (content-type: {content_type})"
                        )
                    else:
                        print(f"  ? Unexpected content-type: {content_type}")
                elif response.status_code == 404:
                    print(
                        "  ✗ Endpoint not found (server may not implement this SSE endpoint)"
                    )
            except Exception as e:
                print(f"{endpoint}: Error - {e}")


async def main():
    """
    Main function to run SSE examples.

    Uncomment the examples you want to run.
    """
    print("Graph API SSE Examples")
    print("======================")

    # First test connectivity
    await sse_connectivity_test()

    # Basic streaming examples (commented out to avoid hanging)
    # await stream_elements_example()
    # await stream_element_by_id_example()
    # await stream_elements_by_class_id_example()
    # await stream_schema_example()
    # await stream_query_example()
    # await stream_health_example()
    # await stream_events_example()

    # Advanced example
    # await concurrent_streaming_example()

    print("\nSSE examples completed!")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
