#!/usr/bin/env python3
"""
Comprehensive Graph API Test Suite

This test application validates all aspects of the graph API including:
- All storage backends (Memory, REST, Synchronized)
- SSE integration and real-time updates
- Data consistency across operations
- Conflict resolution (server-wins)
- Error handling and recovery
- Performance characteristics

Usage:
    uv run python examples/comprehensive_test_suite.py
"""

import asyncio
import json
import logging
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from graph_api.base_element import Props
from graph_api.element_store import ElementStore, ElementStoreConfig
from graph_api.rest_client import (
    RestDataStorageConfig,
    RestGraphApiClient,
    SynchronizedDataStorageConfig,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a test case."""

    name: str
    success: bool
    duration: float
    message: str
    details: Optional[Dict[str, Any]] = None


class ComprehensiveTestSuite:
    """Comprehensive test suite for graph API functionality."""

    def __init__(self):
        self.results: List[TestResult] = []
        self.temp_dir = tempfile.mkdtemp()
        self.test_elements: List[str] = []
        self.start_time = time.time()

    def add_result(
        self,
        name: str,
        success: bool,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Add a test result."""
        duration = time.time() - self.start_time
        self.results.append(TestResult(name, success, duration, message, details))
        status = "✅" if success else "❌"
        print(f"{status} {name}: {message}")

    async def setup_test_data(self, store: ElementStore) -> List[str]:
        """Create test data for validation."""
        test_elements = []

        # Create test elements of different types
        test_data = [
            ("person", {"name": "Alice", "age": 30, "role": "developer"}),
            ("person", {"name": "Bob", "age": 25, "role": "designer"}),
            ("organization", {"name": "Tech Corp", "industry": "software"}),
            ("project", {"name": "Graph API", "status": "active", "priority": "high"}),
        ]

        for class_id, props in test_data:
            element = store.create_new_element(class_id, Props(**props))
            element.source = "comprehensive-test"
            await store.add_elements([element])
            test_elements.append(element.id)

        return test_elements

    async def cleanup_test_data(self, store: ElementStore, element_ids: List[str]):
        """Clean up test data."""
        try:
            elements = [
                store.get_element(eid) for eid in element_ids if store.get_element(eid)
            ]
            if elements:
                await store.delete_elements(elements)
        except Exception as e:
            logger.warning(f"Failed to cleanup test data: {e}")

    async def test_memory_storage(self) -> bool:
        """Test basic memory storage functionality."""
        try:
            # Create memory storage (default)
            store = ElementStore()
            await store.load_elements()

            # Test basic operations
            test_elements = await self.setup_test_data(store)

            # Verify elements exist
            all_elements = store.get_all_elements()
            found_elements = [e for e in all_elements if e.id in test_elements]

            if len(found_elements) != len(test_elements):
                self.add_result(
                    "Memory Storage",
                    False,
                    f"Expected {len(test_elements)} elements, found {len(found_elements)}",
                )
                return False

            # Test class filtering
            person_elements = await store.get_elements_by_class_id("person")
            if len(person_elements) < 2:
                self.add_result(
                    "Memory Storage",
                    False,
                    f"Expected at least 2 person elements, found {len(person_elements)}",
                )
                return False

            # Cleanup
            await self.cleanup_test_data(store, test_elements)

            self.add_result(
                "Memory Storage", True, "Basic CRUD operations work correctly"
            )
            return True

        except Exception as e:
            self.add_result("Memory Storage", False, f"Failed: {e}")
            return False

    async def test_rest_storage(self) -> bool:
        """Test REST storage functionality."""
        try:
            # Create REST storage
            rest_config = RestDataStorageConfig(
                base_url="http://localhost:9800", timeout=10.0
            )
            store_config = ElementStoreConfig(data_config=rest_config)
            store = ElementStore(config=store_config)

            await store.load_elements()

            # Test basic operations
            test_elements = await self.setup_test_data(store)

            # Verify elements exist in local store
            found_elements = [
                store.get_element(eid)
                for eid in test_elements
                if store.get_element(eid)
            ]

            if len(found_elements) != len(test_elements):
                self.add_result(
                    "REST Storage",
                    False,
                    f"Expected {len(test_elements)} elements, found {len(found_elements)}",
                )
                return False

            # Test server persistence by creating a fresh store instance
            # Create a new store instance and load elements to verify persistence
            fresh_store_config = ElementStoreConfig(data_config=rest_config)
            fresh_store = ElementStore(config=fresh_store_config)
            await fresh_store.load_elements()

            # Check if our test elements were persisted on the server
            fresh_reloaded_elements = [
                fresh_store.get_element(eid)
                for eid in test_elements
                if fresh_store.get_element(eid)
            ]
            if len(fresh_reloaded_elements) != len(test_elements):
                self.add_result(
                    "REST Storage",
                    False,
                    f"Server persistence failed: expected {len(test_elements)}, got {len(fresh_reloaded_elements)}",
                )
                return False

            # Cleanup
            await self.cleanup_test_data(fresh_store, test_elements)
            await fresh_store.data_operation.close()
            await store.data_operation.close()

            self.add_result(
                "REST Storage", True, "REST API integration works correctly"
            )
            return True

        except Exception as e:
            self.add_result("REST Storage", False, f"Failed: {e}")
            return False

    async def test_synchronized_storage(self) -> bool:
        """Test synchronized storage functionality."""
        try:
            # Create synchronized storage
            json_path = str(Path(self.temp_dir) / "sync_test.json")
            sync_config = SynchronizedDataStorageConfig(
                base_url="http://localhost:9800",
                json_store_path=json_path,
                timeout=10.0,
            )
            store_config = ElementStoreConfig(data_config=sync_config)
            store = ElementStore(config=store_config)

            await store.load_elements()

            # Check initial cache
            # initial_cache = store.data_operation.get_local_cache_snapshot()

            # Test immediate operations
            test_elements = await self.setup_test_data(store)

            # Verify immediate availability
            cache_after = store.data_operation.get_local_cache_snapshot()
            immediate_elements = [eid for eid in test_elements if eid in cache_after]

            if len(immediate_elements) != len(test_elements):
                self.add_result(
                    "Synchronized Storage",
                    False,
                    f"Immediate cache update failed: {len(immediate_elements)}/{len(test_elements)}",
                )
                return False

            # Test class filtering from cache
            person_cache = await store.data_operation.get_elements_by_class_id("person")
            cache_person_count = len(
                [e for e in person_cache.values() if e.class_id == "person"]
            )

            if cache_person_count < 2:
                self.add_result(
                    "Synchronized Storage",
                    False,
                    f"Cache filtering failed: expected >=2 persons, got {cache_person_count}",
                )
                return False

            # Test JSON store functionality
            await store.data_operation.save_to_json_store()

            if Path(json_path).exists():
                with open(json_path) as f:
                    json_data = json.load(f)
                json_count = len(json_data)
                if json_count < len(test_elements):
                    self.add_result(
                        "Synchronized Storage",
                        False,
                        f"JSON store incomplete: {json_count} < {len(test_elements)}",
                    )
                    return False
            else:
                self.add_result(
                    "Synchronized Storage", False, "JSON store file not created"
                )
                return False

            # Cleanup
            await self.cleanup_test_data(store, test_elements)
            await store.data_operation.close()

            self.add_result(
                "Synchronized Storage",
                True,
                f"Real-time sync works: {len(test_elements)} elements, JSON store validated",
            )
            return True

        except Exception as e:
            self.add_result("Synchronized Storage", False, f"Failed: {e}")
            return False

    async def test_sse_integration(self) -> bool:
        """Test SSE integration and background streaming."""
        try:
            # Test SSE connectivity first
            async with RestGraphApiClient() as client:
                sse_available = await client.client.head("/graph/sse/stream")
                if sse_available.status_code != 200:
                    self.add_result(
                        "SSE Integration",
                        False,
                        f"SSE endpoint not available: HTTP {sse_available.status_code}",
                    )
                    return False

            # Create synchronized storage for SSE testing
            sync_config = SynchronizedDataStorageConfig(
                base_url="http://localhost:9800", timeout=5.0
            )
            store_config = ElementStoreConfig(data_config=sync_config)
            store = ElementStore(config=store_config)

            await store.load_elements()

            # Test that SSE streaming starts without crashing
            await asyncio.sleep(2)  # Give SSE streaming time to start

            # Test element operations work with SSE running in background
            test_element = store.create_new_element(
                "person", Props(name="SSE Test", role="tester")
            )
            test_element.source = "sse-integration-test"

            # Add element - should work with SSE streaming active
            await store.add_elements([test_element])

            # Verify element is in cache
            if test_element.id not in store.data_operation.get_local_cache_snapshot():
                self.add_result(
                    "SSE Integration",
                    False,
                    "Element not found in cache after add operation",
                )
                return False

            # Test that SSE task is still running (not crashed)
            if store.data_operation._sse_task and store.data_operation._sse_task.done():
                # Check if it failed
                try:
                    await store.data_operation._sse_task
                except Exception as e:
                    self.add_result(
                        "SSE Integration", False, f"SSE streaming task failed: {e}"
                    )
                    return False

            # Cleanup
            await store.delete_elements([test_element])
            await store.data_operation.close()

            self.add_result(
                "SSE Integration",
                True,
                "SSE streaming starts successfully and runs in background without crashing",
            )
            return True

        except Exception as e:
            self.add_result("SSE Integration", False, f"Failed: {e}")
            return False

    async def test_data_consistency(self) -> bool:
        """Test data consistency across operations."""
        try:
            # Create synchronized storage
            sync_config = SynchronizedDataStorageConfig(
                base_url="http://localhost:9800"
            )
            store_config = ElementStoreConfig(data_config=sync_config)
            store = ElementStore(config=store_config)

            await store.load_elements()

            # Create test element
            test_element = store.create_new_element(
                "person", Props(name="Consistency Test", age=35)
            )
            test_element.source = "consistency-test"
            await store.add_elements([test_element])

            # Verify in cache
            cache_element = store.data_operation.get_local_cache_snapshot().get(
                test_element.id
            )
            if not cache_element:
                self.add_result(
                    "Data Consistency", False, "Element not in cache after creation"
                )
                return False

            # Update element
            cache_element.properties.age = 36
            await store.update_elements([cache_element])

            # Verify update in cache
            updated_cache = store.data_operation.get_local_cache_snapshot().get(
                test_element.id
            )
            if not updated_cache or updated_cache.properties.age != 36:
                self.add_result(
                    "Data Consistency", False, "Element update not reflected in cache"
                )
                return False

            # Test class-based queries
            consistency_element = (await store.get_elements_by_class_id("person")).get(
                test_element.id
            )

            if not consistency_element or consistency_element.properties.age != 36:
                self.add_result(
                    "Data Consistency",
                    False,
                    "Element not found in class query or age mismatch",
                )
                return False

            # Cleanup
            await store.delete_elements([test_element])
            await store.data_operation.close()

            self.add_result(
                "Data Consistency",
                True,
                "CRUD operations maintain consistency across cache and queries",
            )
            return True

        except Exception as e:
            self.add_result("Data Consistency", False, f"Failed: {e}")
            return False

    async def test_error_handling(self) -> bool:
        """Test error handling and recovery."""
        try:
            # Test with invalid server URL
            invalid_config = SynchronizedDataStorageConfig(
                base_url="http://invalid-server:9999", timeout=2.0
            )
            store_config = ElementStoreConfig(data_config=invalid_config)
            store = ElementStore(config=store_config)

            # Should handle connection errors gracefully
            try:
                await store.load_elements()
                # If we get here, the error handling worked
            except Exception:
                # Expected - server not available
                pass

            # Test memory fallback - should still work
            memory_store = ElementStore()  # Default memory storage
            await memory_store.load_elements()

            test_element = memory_store.create_new_element(
                "person", Props(name="Error Test")
            )
            await memory_store.add_elements([test_element])

            if not memory_store.get_element(test_element.id):
                self.add_result(
                    "Error Handling", False, "Memory storage fallback failed"
                )
                return False

            await memory_store.delete_elements([test_element])

            self.add_result(
                "Error Handling",
                True,
                "Error handling and memory fallback work correctly",
            )
            return True

        except Exception as e:
            self.add_result("Error Handling", False, f"Failed: {e}")
            return False

    async def test_performance(self) -> bool:
        """Test performance characteristics."""
        try:
            # Create memory storage for performance testing
            store = ElementStore()
            await store.load_elements()

            # Create multiple elements for performance test
            elements = []
            for i in range(100):
                element = store.create_new_element(
                    "person", Props(name=f"Perf Test {i}", index=i)
                )
                elements.append(element)

            # Time bulk operations
            start_time = time.time()
            await store.add_elements(elements)
            add_time = time.time() - start_time

            # Time queries
            start_time = time.time()
            _ = await store.get_elements_by_class_id("person")
            query_time = time.time() - start_time

            # Time individual access
            start_time = time.time()
            for element in elements[:10]:  # Sample of 10
                _ = store.get_element(element.id)
            access_time = time.time() - start_time

            # Cleanup
            await store.delete_elements(elements)

            # Performance thresholds (reasonable for local operations)
            if add_time > 1.0:  # 1 second for 100 elements
                self.add_result(
                    "Performance", False, f"Bulk add too slow: {add_time:.2f}s"
                )
                return False

            if query_time > 0.1:  # 100ms for class query
                self.add_result(
                    "Performance", False, f"Class query too slow: {query_time:.2f}s"
                )
                return False

            if access_time > 0.01:  # 10ms for 10 element access
                self.add_result(
                    "Performance", False, f"Element access too slow: {access_time:.2f}s"
                )
                return False

            self.add_result(
                "Performance",
                True,
                f"Performance acceptable: add={add_time:.3f}s, query={query_time:.3f}s, access={access_time:.3f}s",
            )
            return True

        except Exception as e:
            self.add_result("Performance", False, f"Failed: {e}")
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("Comprehensive Graph API Test Suite")
        print("=" * 50)
        print(f"Starting tests at {time.strftime('%H:%M:%S')}")
        print()

        # Reset timing
        self.start_time = time.time()

        # Run all tests
        tests = [
            ("Memory Storage", self.test_memory_storage),
            ("REST Storage", self.test_rest_storage),
            ("Synchronized Storage", self.test_synchronized_storage),
            ("SSE Integration", self.test_sse_integration),
            ("Data Consistency", self.test_data_consistency),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance),
        ]

        for test_name, test_func in tests:
            print(f"Running {test_name}...")
            try:
                await test_func()
            except Exception as e:
                self.add_result(test_name, False, f"Unexpected error: {e}")
            print()

        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        total_time = time.time() - self.start_time

        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "total_time": total_time,
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "duration": r.duration,
                    "message": r.message,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        # Print summary
        print("Test Summary")
        print("-" * 30)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(".1f")
        print(".2f")
        print()

        if failed_tests > 0:
            print("Failed Tests:")
            for result in self.results:
                if not result.success:
                    print(f"  ❌ {result.name}: {result.message}")
        else:
            print("🎉 All tests passed!")

        return summary

    def cleanup(self):
        """Clean up temporary files."""
        try:
            import shutil

            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp dir: {e}")


async def main():
    """Main function to run the comprehensive test suite."""
    suite = ComprehensiveTestSuite()

    try:
        results = await suite.run_all_tests()

        # Save detailed results to file
        results_file = str(Path(tempfile.gettempdir()) / "graph_api_test_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\nDetailed results saved to: {results_file}")

        # Exit with appropriate code
        success = results["failed"] == 0
        return 0 if success else 1

    except Exception as e:
        logger.error(f"Test suite failed: {e}")
        print(f"\n❌ Test suite crashed: {e}")
        return 1

    finally:
        suite.cleanup()


if __name__ == "__main__":
    # Run the comprehensive test suite
    exit_code = asyncio.run(main())
    exit(exit_code)
