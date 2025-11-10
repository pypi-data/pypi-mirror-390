#!/usr/bin/env python3
"""
SynchronizedDataStorage Example

This example demonstrates how to use the SynchronizedDataStorage for real-time
bidirectional synchronization between a local graph store and a remote server.

Features demonstrated:
- Creating a synchronized store with SSE streaming
- Immediate local operations with automatic server sync
- Real-time updates from server changes
- Local cache management
- JSON store preparation for offline mode

Usage:
    uv run python examples/synchronized_storage_example.py
"""

import asyncio
import logging
import tempfile
from pathlib import Path

from graph_api.element_store import ElementStore, ElementStoreConfig
from graph_api.rest_client import SynchronizedDataStorageConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main example showing synchronized storage usage."""

    print("SynchronizedDataStorage Example")
    print("=" * 40)

    # Configure synchronized storage
    sync_config = SynchronizedDataStorageConfig(
        base_url="http://localhost:9800",
        json_store_path=str(
            Path(tempfile.gettempdir()) / "sync_example_cache.json"
        ),  # For future offline mode
        timeout=10.0,
    )

    # Create ElementStore with synchronized storage
    store_config = ElementStoreConfig(data_config=sync_config)
    store = ElementStore(config=store_config)

    try:
        print("\n1. Initializing synchronized storage...")
        print("   - Loading initial data from server")
        print("   - Starting SSE streaming for real-time updates")

        await store.load_elements()

        print("   ✓ Storage initialized and SSE streaming started")

        print("\n2. Checking local cache...")
        cache_snapshot = store.data_operation.get_local_cache_snapshot()
        print(f"   Cache contains {len(cache_snapshot)} elements from server")

        print("\n3. Creating a test element (immediate local operation)...")
        # Create a test person
        test_props = {
            "name": "Sync Test User",
            "description": "Created with SynchronizedDataStorage",
            "tags": ["synchronized", "example"],
        }
        person = store.create_new_element("person", test_props)
        person.source = "sync-example"  # Required for server validation

        print(f"   Created person with ID: {person.id}")

        print("\n4. Adding element to store (immediate + sync to server)...")
        await store.add_elements([person])
        print("   ✓ Element added to local cache immediately")
        print("   ✓ Server sync attempted (may fail if server validation issues)")

        print("\n5. Verifying element in local cache...")
        # Check that element is immediately available
        cache_after = store.data_operation.get_local_cache_snapshot()
        if person.id in cache_after:
            cached_element = cache_after[person.id]
            print(
                f"   ✓ Element found in cache: {cached_element.properties.get('name')}"
            )
        else:
            print("   ✗ Element not found in cache")
            return

        print("\n6. Testing element retrieval by class...")
        # Test filtering by class ID
        person_elements = await store.data_operation.get_elements_by_class_id("person")
        person_count = len(
            [e for e in person_elements.values() if e.class_id == "person"]
        )
        print(f"   Found {person_count} person elements in cache")

        print("\n7. Demonstrating real-time sync...")
        print("   The store is now listening for SSE events from the server.")
        print(
            "   Any changes made on the server will automatically update the local cache."
        )
        print("   Local changes are immediately available and synced to server.")

        # Wait a bit to demonstrate SSE streaming is active
        print("\n8. SSE streaming status...")
        print("   SSE task is running in background for real-time updates")
        print("   Server-wins conflict resolution ensures consistency")

        print("\n9. JSON store preparation...")
        print("   Path configured for future offline mode:")
        print(f"   {store.data_operation._json_store_path}")

        # Optional: Save current state to JSON (for future offline use)
        try:
            await store.data_operation.save_to_json_store()
            print("   ✓ Current cache saved to JSON store")
        except Exception as e:
            print(f"   ! JSON store save failed (expected if path doesn't exist): {e}")

        print("\n10. Cleanup...")
        # Remove test element
        await store.delete_elements([person])
        print("   ✓ Test element removed from store")

        print("\n✅ SynchronizedDataStorage example completed successfully!")
        print("\nKey Benefits Demonstrated:")
        print("• Immediate local operations (no server round-trip required)")
        print("• Automatic server synchronization")
        print("• Real-time updates via SSE streaming")
        print("• Local cache for fast access")
        print("• Server-wins conflict resolution")
        print("• JSON store hooks for offline mode")
        print("• Backward compatibility with existing ElementStore API")

    except Exception as e:
        logger.error(f"Example failed: {e}")
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        try:
            await store.data_operation.close()
            print("\n✓ Storage closed and SSE streaming stopped")
        except Exception as e:
            logger.warning(f"Error closing storage: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
