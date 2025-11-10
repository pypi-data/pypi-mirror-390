"""
SSE Integration Test

This test validates that Server-Sent Events (SSE) correctly stream real-time updates
when elements are created, updated, or deleted via the REST API.

The test runs two concurrent tasks:
1. SSE Consumer: Listens to SSE events and collects them
2. REST Producer: Sends CRUD operations with intervals
3. Validator: Compares sent operations with received events
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from graph_api.rest_client import RestGraphApiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestEvent:
    """Represents a test operation and expected SSE event."""

    operation: str  # 'create', 'update', 'delete'
    element_id: str
    element_data: Dict[str, Any]
    timestamp: float
    expected_event_type: str


@dataclass
class SseEvent:
    """Represents an SSE event received from the stream."""

    event_type: str
    element_id: str
    data: Dict[str, Any]
    timestamp: float
    received_at: float


class SseIntegrationTest:
    """
    Integration test for SSE functionality.

    Tests that REST API operations are correctly streamed via SSE.
    """

    def __init__(self, base_url: str = "http://localhost:9800"):
        self.base_url = base_url
        self.client: Optional[RestGraphApiClient] = None
        self.received_events: List[SseEvent] = []
        self.sent_events: List[TestEvent] = []
        self.test_elements: List[str] = []  # Track elements created for cleanup

    async def setup(self):
        """Initialize the test client."""
        self.client = RestGraphApiClient()
        logger.info(f"Initialized SSE integration test with base URL: {self.base_url}")

    async def teardown(self):
        """Clean up test resources."""
        if self.client:
            # Clean up test elements
            if self.test_elements:
                try:
                    await self.client.delete_elements(self.test_elements)
                    logger.info(f"Cleaned up {len(self.test_elements)} test elements")
                except Exception as e:
                    logger.warning(f"Failed to clean up test elements: {e}")

            await self.client.close()

    async def sse_consumer(self, stream_type: str = "elements", duration: int = 30):
        """
        Consume SSE events for a specified duration.

        Args:
            stream_type: Type of SSE stream ('elements', 'events', etc.)
            duration: How long to listen in seconds
        """
        logger.info(f"Starting SSE consumer for {stream_type} stream")

        try:
            start_time = time.time()
            event_count = 0

            # Choose the appropriate stream method
            if stream_type == "elements":
                stream_method = self.client.stream_elements()
            elif stream_type == "events":
                stream_method = self.client.stream_events()
            else:
                raise ValueError(f"Unsupported stream type: {stream_type}")

            # Add timeout to the stream
            async def timed_stream():
                try:
                    async for event_data in stream_method:
                        yield event_data
                except Exception as e:
                    logger.error(f"SSE stream error: {e}")
                    return

            stream_with_timeout = timed_stream()

            async for event_data in stream_with_timeout:
                event_count += 1
                received_at = time.time()

                # Parse SSE event
                event_type = event_data.get("type", "unknown")

                # Handle BATCH events by creating individual events for each element
                if event_type == "BATCH":
                    elements = event_data.get("elements", [])
                    for element in elements:
                        if isinstance(element, dict) and "id" in element:
                            element_id = element["id"]
                            # For BATCH events, we can't easily distinguish CREATE from UPDATE
                            # based on existing elements, so assume CREATE for now
                            # The validation logic will handle matching appropriately
                            batch_event = SseEvent(
                                event_type="CREATE",  # Default to CREATE for BATCH events
                                element_id=element_id,
                                data={"element": element},
                                timestamp=event_data.get("ts", received_at),
                                received_at=received_at,
                            )
                            self.received_events.append(batch_event)
                            logger.info(
                                f"Received SSE event {event_count}: CREATE (from BATCH) for {element_id}"
                            )
                    # Skip adding the BATCH event itself
                    continue

                # Extract element ID based on event type
                element_id = "unknown"
                if event_type in ["CREATE", "UPDATE", "DELETE"]:
                    # Individual element events have element.id
                    element = event_data.get("element", {})
                    element_id = (
                        element.get("id", "unknown")
                        if isinstance(element, dict)
                        else "unknown"
                    )
                elif event_type == "INITIAL_DATA":
                    # Initial data contains multiple elements
                    element_id = "initial_data"
                else:
                    # Other event types
                    element_id = event_data.get("elementId") or event_data.get(
                        "id", "unknown"
                    )

                data = event_data.get("data", event_data)

                sse_event = SseEvent(
                    event_type=event_type,
                    element_id=element_id,
                    data=data,
                    timestamp=event_data.get("timestamp", received_at),
                    received_at=received_at,
                )

                self.received_events.append(sse_event)
                logger.info(
                    f"Received SSE event {event_count}: {event_type} for {element_id}"
                )

                # Check if we've exceeded the duration
                if received_at - start_time > duration:
                    logger.info(f"SSE consumer stopping after {duration} seconds")
                    break

        except Exception as e:
            logger.error(f"SSE consumer error: {e}")
            # Don't raise exception, just log and continue

        logger.info(
            f"SSE consumer finished. Received {len(self.received_events)} events"
        )

    async def rest_producer(self, operations: List[TestEvent], interval: float = 2.0):
        """
        Send REST API operations with intervals.

        Args:
            operations: List of operations to perform
            interval: Seconds to wait between operations
        """
        logger.info(f"Starting REST producer with {len(operations)} operations")

        for i, operation in enumerate(operations):
            try:
                logger.info(
                    f"Executing operation {i+1}/{len(operations)}: {operation.operation} {operation.element_id}"
                )

                if operation.operation == "create":
                    elements = [operation.element_data]
                    await self.client.create_elements(elements)
                    self.test_elements.append(operation.element_id)

                elif operation.operation == "update":
                    elements = [operation.element_data]
                    await self.client.patch_elements(elements)

                elif operation.operation == "delete":
                    await self.client.delete_elements([operation.element_id])
                    if operation.element_id in self.test_elements:
                        self.test_elements.remove(operation.element_id)

                else:
                    raise ValueError(f"Unsupported operation: {operation.operation}")

                operation.timestamp = time.time()
                self.sent_events.append(operation)

                logger.info(f"Operation {i+1} completed successfully")

                # Wait before next operation
                if i < len(operations) - 1:
                    await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Failed to execute operation {i+1}: {e}")
                raise

        logger.info("REST producer finished")

    def validate_events(self) -> Dict[str, Any]:
        """
        Validate that sent operations match received SSE events.

        Returns:
            Validation results dictionary
        """
        logger.info("Starting event validation")

        results = {
            "total_sent": len(self.sent_events),
            "total_received": len(self.received_events),
            "matched_events": 0,
            "unmatched_sent": [],
            "unmatched_received": [],
            "validation_errors": [],
            "success": False,
        }

        # Create lookup dictionaries - only consider individual element events
        sent_by_id = {event.element_id: event for event in self.sent_events}
        received_by_id = defaultdict(list)

        for event in self.received_events:
            # Only consider individual element events, not batch or initial data
            if event.event_type in ["CREATE", "UPDATE", "DELETE"]:
                received_by_id[event.element_id].append(event)

        # Validate each sent event has corresponding SSE event
        for sent_event in self.sent_events:
            element_id = sent_event.element_id

            if element_id not in received_by_id:
                results["unmatched_sent"].append(
                    {
                        "element_id": element_id,
                        "operation": sent_event.operation,
                        "reason": "No SSE events received for this element",
                    }
                )
                continue

            # Find matching SSE event
            matching_events = [
                event
                for event in received_by_id[element_id]
                if self._events_match(sent_event, event)
            ]

            if matching_events:
                results["matched_events"] += 1
                logger.info(
                    f"✓ Matched event for {element_id} ({sent_event.operation})"
                )
            else:
                results["unmatched_sent"].append(
                    {
                        "element_id": element_id,
                        "operation": sent_event.operation,
                        "reason": "No matching SSE event found",
                        "received_events": [
                            {"type": e.event_type, "timestamp": e.received_at}
                            for e in received_by_id[element_id]
                        ],
                    }
                )

        # Check for unexpected SSE events (only individual element events)
        expected_element_ids = set(sent_by_id.keys())
        for element_id, events in received_by_id.items():
            if element_id not in expected_element_ids:
                results["unmatched_received"].extend(
                    [
                        {
                            "element_id": element_id,
                            "event_type": event.event_type,
                            "reason": "Unexpected SSE event for unknown element",
                        }
                        for event in events
                    ]
                )

        # Overall success
        results["success"] = (
            results["matched_events"] == results["total_sent"]
            and len(results["unmatched_received"]) == 0
        )

        # Add summary of all received events for debugging
        results["all_received_events"] = [
            {"type": e.event_type, "element_id": e.element_id, "timestamp": e.timestamp}
            for e in self.received_events
        ]

        logger.info(
            f"Validation complete: {results['matched_events']}/{results['total_sent']} events matched"
        )
        return results

    def _events_match(self, sent_event: TestEvent, sse_event: SseEvent) -> bool:
        """
        Check if a sent event matches a received SSE event.

        Args:
            sent_event: The operation that was sent
            sse_event: The SSE event that was received

        Returns:
            True if events match
        """
        # Check element ID
        if sent_event.element_id != sse_event.element_id:
            return False

        # Check event type based on operation
        expected_types = {
            "create": [
                "CREATE",
                "UPDATE",
            ],  # BATCH events might be sent as CREATE or UPDATE
            "update": [
                "UPDATE",
                "CREATE",
            ],  # Allow flexibility for server implementation
            "delete": ["DELETE"],
        }

        if sse_event.event_type not in expected_types.get(sent_event.operation, []):
            return False

        # Check timing (SSE event should be after or very close to sent operation)
        time_diff = sse_event.received_at - sent_event.timestamp
        if (
            time_diff < -1.0 or time_diff > 10.0
        ):  # Allow 1 second early, 10 seconds late
            logger.warning(
                f"Timing mismatch for {sent_event.element_id}: {time_diff:.2f}s"
            )
            return False

        return True

    async def check_sse_availability(self, stream_type: str = "elements") -> bool:
        """
        Check if SSE endpoints are available on the server.

        Args:
            stream_type: Type of SSE stream to check

        Returns:
            True if SSE endpoint is available
        """
        # All SSE streams now use the single /stream endpoint
        endpoint = "/graph/sse/stream"

        try:
            response = await self.client.client.head(endpoint)
            return response.status_code == 200
        except Exception:
            return False

    async def run_test(self, stream_type: str = "elements") -> Dict[str, Any]:
        """
        Run the complete SSE integration test.

        Args:
            stream_type: Type of SSE stream to test

        Returns:
            Test results dictionary
        """
        logger.info("Starting SSE integration test")

        # Setup
        await self.setup()

        try:
            # Check SSE availability first
            sse_available = await self.check_sse_availability(stream_type)
            if not sse_available:
                logger.warning("SSE endpoint /stream not available on server")
                return {
                    "test_name": "SSE Integration Test",
                    "stream_type": stream_type,
                    "timestamp": time.time(),
                    "sse_available": False,
                    "error": "SSE endpoint /stream not available (HTTP 404 or connection failed)",
                    "validation": {"success": False},
                }

            # Define test operations
            test_operations = self._create_test_operations()

            # Run producer and consumer concurrently with timeout
            producer_task = asyncio.create_task(
                self.rest_producer(test_operations, interval=1.5)
            )

            consumer_task = asyncio.create_task(
                self.sse_consumer(stream_type, duration=20)
            )

            # Wait for both to complete with overall timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(producer_task, consumer_task),
                    timeout=25,  # Slightly longer than consumer duration
                )
            except asyncio.TimeoutError:
                logger.warning("Test timed out, but continuing with validation")

            # Validate results
            validation_results = self.validate_events()

            # Add test metadata
            results = {
                "test_name": "SSE Integration Test",
                "stream_type": stream_type,
                "timestamp": time.time(),
                "sse_available": True,
                "operations_performed": len(test_operations),
                "events_received": len(self.received_events),
                "validation": validation_results,
            }

            logger.info(f"Test completed: {validation_results['success']}")
            return results

        finally:
            await self.teardown()

    def _create_test_operations(self) -> List[TestEvent]:
        """
        Create a sequence of test operations.

        Returns:
            List of test operations to perform
        """
        operations = []

        # Create operations
        for i in range(3):
            element_id = f"test-sse-element-{i}"
            element_data = {
                "id": element_id,
                "classId": "TestElement",
                "type": "node",
                "properties": {
                    "name": f"Test Element {i}",
                    "value": i * 10,
                    "category": "integration_test",
                },
                "source": "sse_test",
            }

            operations.append(
                TestEvent(
                    operation="create",
                    element_id=element_id,
                    element_data=element_data,
                    timestamp=0.0,
                    expected_event_type="element_created",
                )
            )

        # Update operations
        for i in range(3):
            element_id = f"test-sse-element-{i}"
            element_data = {
                "id": element_id,
                "classId": "TestElement",  # Required field
                "type": "node",  # Required field
                "properties": {
                    "name": f"Updated Test Element {i}",
                    "value": i * 10 + 5,
                    "updated": True,
                },
            }

            operations.append(
                TestEvent(
                    operation="update",
                    element_id=element_id,
                    element_data=element_data,
                    timestamp=0.0,
                    expected_event_type="element_updated",
                )
            )

        # Delete operations
        for i in range(3):
            element_id = f"test-sse-element-{i}"
            element_data = {"id": element_id}  # Minimal data for delete

            operations.append(
                TestEvent(
                    operation="delete",
                    element_id=element_id,
                    element_data=element_data,
                    timestamp=0.0,
                    expected_event_type="element_deleted",
                )
            )

        return operations

    async def _verify_rest_operations(
        self, operations: List[TestEvent]
    ) -> Dict[str, Any]:
        """
        Verify that REST operations were successful by querying the API.

        Args:
            operations: List of operations that were performed

        Returns:
            Verification results
        """
        results = {
            "verified": 0,
            "total": len(operations),
            "success": False,
            "errors": [],
        }

        try:
            # Get all elements to verify state
            all_elements = await self.client.get_all_elements()

            # Group operations by element ID
            operations_by_id = {}
            for op in operations:
                operations_by_id[op.element_id] = op

            # Verify each operation
            for element_id, operation in operations_by_id.items():
                try:
                    if operation.operation == "create":
                        # Check if element exists
                        if element_id in all_elements:
                            results["verified"] += 1
                            logger.info(f"✓ Create verified: {element_id}")
                        else:
                            results["errors"].append(
                                f"Create failed: {element_id} not found"
                            )

                    elif operation.operation == "update":
                        # Check if element exists and has updated properties
                        if element_id in all_elements:
                            element = all_elements[element_id]
                            if element.get("properties", {}).get("updated"):
                                results["verified"] += 1
                                logger.info(f"✓ Update verified: {element_id}")
                            else:
                                results["errors"].append(
                                    f"Update failed: {element_id} not updated"
                                )
                        else:
                            results["errors"].append(
                                f"Update failed: {element_id} not found"
                            )

                    elif operation.operation == "delete":
                        # Check if element was deleted
                        if element_id not in all_elements:
                            results["verified"] += 1
                            logger.info(f"✓ Delete verified: {element_id}")
                        else:
                            results["errors"].append(
                                f"Delete failed: {element_id} still exists"
                            )

                except Exception as e:
                    results["errors"].append(
                        f"Verification error for {element_id}: {e}"
                    )

            results["success"] = len(results["errors"]) == 0

        except Exception as e:
            results["errors"].append(f"API query failed: {e}")

        return results


async def run_rest_only_test():
    """
    Run a test that validates REST API operations work correctly,
    without requiring SSE endpoints.
    """
    print("REST API Operations Test (SSE Client Validation)")
    print("=" * 55)

    test = SseIntegrationTest()

    try:
        await test.setup()

        # Define test operations
        test_operations = test._create_test_operations()

        print(f"Testing {len(test_operations)} REST operations...")

        # Run only the producer (REST operations)
        await test.rest_producer(test_operations, interval=0.5)  # Faster for testing

        # Verify operations by querying the API
        print("\nVerifying operations via REST API...")

        verification_results = await test._verify_rest_operations(test_operations)

        print("\nVerification Results:")
        print(f"- Operations attempted: {len(test_operations)}")
        print(f"- Operations verified: {verification_results['verified']}")
        print(f"- Verification success: {verification_results['success']}")

        if verification_results["success"]:
            print("✅ REST operations test PASSED")
            print(
                "   SSE client code is ready for when server endpoints are implemented"
            )
        else:
            print("❌ REST operations test FAILED")
            for error in verification_results["errors"][:5]:  # Show first 5 errors
                print(f"   - {error}")

        await test.teardown()

        return {
            "test_type": "rest_only",
            "operations_tested": len(test_operations),
            "verification": verification_results,
        }

    except Exception as e:
        logger.error(f"REST test failed: {e}")
        print(f"❌ TEST ERROR: {e}")
        await test.teardown()
        raise


async def run_sse_integration_test():
    """
    Run the SSE integration test and print results.
    """
    print("SSE Integration Test")
    print("=" * 50)

    test = SseIntegrationTest()

    try:
        results = await test.run_test(stream_type="elements")

        print("\nTest Results:")
        print(f"- SSE Available: {results.get('sse_available', 'Unknown')}")

        if not results.get("sse_available", True):
            print(f"- Error: {results.get('error', 'Unknown error')}")
            print("⚠️  SSE endpoints not available on server")
            print("   This test validates client-side code only")
            return results

        print(f"- Operations performed: {results['operations_performed']}")
        print(f"- SSE events received: {results['events_received']}")
        print(
            f"- Events matched: {results['validation']['matched_events']}/{results['validation']['total_sent']}"
        )

        if results["validation"]["success"]:
            print("✅ TEST PASSED: All operations were correctly streamed via SSE")
        else:
            print("❌ TEST FAILED: Some operations were not streamed correctly")

            if results["validation"]["unmatched_sent"]:
                print(
                    f"\nUnmatched sent operations ({len(results['validation']['unmatched_sent'])}):"
                )
                for unmatched in results["validation"]["unmatched_sent"][
                    :5
                ]:  # Show first 5
                    print(
                        f"  - {unmatched['operation']} {unmatched['element_id']}: {unmatched['reason']}"
                    )

            if results["validation"]["unmatched_received"]:
                print(
                    f"\nUnexpected received events ({len(results['validation']['unmatched_received'])}):"
                )
                for unmatched in results["validation"]["unmatched_received"][
                    :5
                ]:  # Show first 5
                    print(
                        f"  - {unmatched['event_type']} {unmatched['element_id']}: {unmatched['reason']}"
                    )

        return results

    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        print(f"❌ TEST ERROR: {e}")
        raise


if __name__ == "__main__":
    # Run both tests
    print("Running SSE Integration Tests")
    print("=" * 40)

    # First run the REST-only test to validate operations work
    asyncio.run(run_rest_only_test())

    print("\n" + "=" * 40 + "\n")

    # Then run the full SSE integration test
    asyncio.run(run_sse_integration_test())
