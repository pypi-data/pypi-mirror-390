#!/usr/bin/env python3
"""
Example: Get Elements by Class ID

This example demonstrates how to use the new get_elements_by_class_id functionality
in the Python Graph API client to fetch all elements of a specific class.

Requirements:
- TypeScript Graph API server running on http://localhost:9800
- Some elements with different classId values in the database
"""

import asyncio
import json

from graph_api.rest_client import RestClientConfig, RestGraphApiClient


async def main():
    """Main function to demonstrate getting elements by class ID."""

    # Initialize the REST client
    config = RestClientConfig(base_url="http://localhost:9800", timeout=30.0)

    async with RestGraphApiClient(config) as client:
        try:
            # Example 1: Get elements by class ID using the new detailed method
            print("=== Example 1: Get elements by class ID (detailed response) ===")
            class_id = "Person"  # Replace with actual class ID from your data

            result = await client.get_elements_by_class_id(class_id)
            print(f"Status: {result['status']}")
            print(f"Count: {result['count']}")
            print(f"Elements found: {len(result['data'])}")

            # Print first element as example
            if result["data"]:
                print("\nFirst element:")
                print(json.dumps(result["data"][0], indent=2))
            else:
                print(f"No elements found for class ID: {class_id}")

            print("\n" + "=" * 60 + "\n")

            # Example 2: Get elements by class ID using the legacy method (just returns list)
            print("=== Example 2: Get elements by class ID (legacy method) ===")

            elements = await client.get_elements_by_class(class_id)
            print(f"Elements found: {len(elements)}")

            if elements:
                print("\nClass IDs of found elements:")
                for element in elements[:5]:  # Show first 5
                    print(
                        f"  - ID: {element.get('id')}, Class: {element.get('classId')}"
                    )

            print("\n" + "=" * 60 + "\n")

            # Example 3: Try different class IDs
            print("=== Example 3: Try different class IDs ===")

            # Get all elements first to see what class IDs are available
            all_elements = await client.get_all_elements()

            # Extract unique class IDs
            class_ids = set()
            for element in all_elements.values():
                if element.get("classId"):
                    class_ids.add(element["classId"])

            print(f"Available class IDs: {sorted(class_ids)}")

            # Try each class ID
            for cid in sorted(class_ids)[:3]:  # Show first 3 class IDs
                result = await client.get_elements_by_class_id(cid)
                print(f"  - Class '{cid}': {result['count']} elements")

        except Exception as e:
            print(f"Error occurred: {e}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, "details"):
                print(f"Error details: {e.details}")


async def example_with_element_store():
    """Example using the ElementStore with REST backend."""

    print("\n" + "=" * 60)
    print("=== Example: Using ElementStore with REST Backend ===")

    from graph_api.element_store import ElementStore, ElementStoreConfig
    from graph_api.rest_client import RestDataStorage, RestDataStorageConfig

    # Configure REST data storage
    rest_config = RestDataStorageConfig(base_url="http://localhost:9800", timeout=30.0)

    # Create REST data storage
    rest_storage = RestDataStorage(rest_config.to_rest_config())

    # Configure ElementStore with REST backend
    store_config = ElementStoreConfig(data_config=rest_config, operation=rest_storage)

    # Create ElementStore
    store = ElementStore(store_config)

    try:
        # Load elements from remote API
        await store.load_elements()

        print(f"Loaded {len(store.elements)} elements from REST API")

        # Get elements by class ID using ElementStore method
        class_id = "Person"  # Replace with actual class ID
        elements_kg = await store.get_elements_by_class_id(class_id)

        print(
            f"Found {len(elements_kg)} elements with class ID '{class_id}' via ElementStore"
        )

        # Also try the REST storage method directly
        elements_dict = await rest_storage.get_elements_by_class_id(class_id)
        print(
            f"Found {len(elements_dict)} elements with class ID '{class_id}' via REST storage"
        )

        # Show some details
        for element_id, element in list(elements_dict.items())[:3]:  # Show first 3
            print(f"  - {element_id}: {element.class_id}")

    except Exception as e:
        print(f"Error with ElementStore: {e}")

    finally:
        # Clean up
        await rest_storage.close()


if __name__ == "__main__":
    print("Graph API - Get Elements by Class ID Example")
    print("=" * 50)

    # Run the main example
    asyncio.run(main())

    # Run the ElementStore example
    asyncio.run(example_with_element_store())

    print("\nExample completed!")
