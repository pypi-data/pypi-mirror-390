"""
Examples demonstrating how to use the Python Graph API REST client to communicate with
the TypeScript Bun/Hono/OpenAPI endpoint.

This file shows various scenarios for interacting with the Graph API including:
- Setting up the client and data storage
- CRUD operations on elements
- Querying elements and schemas
- Error handling
- Integration with ElementStore
"""

import asyncio
import json
import logging

from graph_api import (
    ElementNotFoundError,
    ElementStore,
    ElementStoreConfig,
    GraphApiError,
    RestClientConfig,
    RestDataStorage,
    RestDataStorageConfig,
    RestGraphApiClient,
    ValidationError,
)

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_rest_client():
    """
    Basic example showing how to use the REST client directly.
    """
    print("\n=== Basic REST Client Example ===")

    # Configure the client
    config = RestClientConfig(
        base_url="http://localhost:9800", timeout=30.0, verify_ssl=True
    )

    # Use async context manager for proper cleanup
    async with RestGraphApiClient(config) as client:
        try:
            # Get all elements
            print("Getting all elements...")
            all_elements = await client.get_all_elements()
            print(f"Found {len(all_elements)} elements")

            # Get a specific element by ID (if any exist)
            if all_elements:
                first_id = list(all_elements.keys())[0]
                print(f"\nGetting element {first_id}...")
                element = await client.get_element_by_id(first_id)
                print(f"Element: {json.dumps(element, indent=2)}")

            # Create a new element
            print("\nCreating a new element...")
            new_element_data = [
                {
                    "id": "python-example-1",
                    "type": "node",
                    "classId": "person",
                    "properties": {
                        "name": "Python API Test",
                        "description": "Created via Python REST client",
                        "tags": ["python", "api", "test"],
                    },
                    "source": "python-example",
                }
            ]

            created_elements = await client.create_elements(new_element_data)
            print(f"Created: {json.dumps(created_elements, indent=2)}")

            # Query elements
            print("\nQuerying elements...")
            query_result = await client.query_elements({"source": "python-example"})
            print(f"Query result: {json.dumps(query_result, indent=2)}")

            # Get all schemas
            print("\nGetting schemas...")
            schemas = await client.get_all_schemas()
            print(f"Found {len(schemas.get('schema', {}))} schemas")

        except GraphApiError as e:
            print(f"Graph API Error: {e} (code: {e.code})")
        except Exception as e:
            print(f"Unexpected error: {e}")


async def example_element_store_with_rest():
    """
    Example showing how to use ElementStore with REST data storage.
    This allows seamless integration with existing code while using a remote API.
    """
    print("\n=== ElementStore with REST Storage Example ===")

    # Configure REST data storage
    rest_config = RestDataStorageConfig(
        type="rest", base_url="http://localhost:9800", timeout=30.0
    )

    # Configure ElementStore to use REST storage
    store_config = ElementStoreConfig(data_config=rest_config)  # Correct parameter name

    # Create custom data storage instance
    rest_storage = RestDataStorage(rest_config.to_rest_config())

    try:
        # Initialize storage
        await rest_storage.init()

        # Create ElementStore with REST storage
        store = ElementStore(store_config)
        store.data_operation = rest_storage  # Correct attribute name

        # Initialize the store (loads data from REST API)
        await store.load_elements()

        print(f"Store initialized with {len(store.elements)} elements from REST API")

        # Create a new node using the familiar ElementStore API
        print("\nCreating element via ElementStore...")
        from graph_api import ElementDetails, NodeTypes, Props

        # Create ElementDetails properly
        element_details = ElementDetails(
            id="python-store-example-1",
            class_id="person",
            type=NodeTypes.NODE,
            properties=Props(
                name="Store Example",
                description="Created via ElementStore with REST storage",
            ),
        )

        # This will automatically sync to the REST API
        new_node = store.create_new_element("person", element_details)
        await store.add_elements([new_node])

        print(f"Created node: {new_node.id}")

        # Query using ElementStore methods (queries local cache)
        matching_elements = await store.get_elements_by_class_id("person")
        print(f"Found {len(matching_elements)} person elements")

        # Update an element
        if new_node:
            new_node.properties["description"] = "Updated via ElementStore"
            await store.update_elements([new_node])
            print("Updated element properties")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await rest_storage.close()


async def example_crud_operations():
    """
    Comprehensive example showing all CRUD operations.
    """
    print("\n=== CRUD Operations Example ===")

    async with RestGraphApiClient() as client:
        try:
            # CREATE - Create multiple elements
            print("Creating elements...")
            elements_to_create = [
                {
                    "id": "python-crud-1",
                    "type": "node",
                    "classId": "person",
                    "properties": {
                        "name": "Alice Python",
                        "age": 30,
                        "city": "San Francisco",
                    },
                    "source": "python-crud",
                },
                {
                    "id": "python-crud-2",
                    "type": "node",
                    "classId": "person",
                    "properties": {"name": "Bob Python", "age": 25, "city": "New York"},
                    "source": "python-crud",
                },
            ]

            created = await client.create_elements(elements_to_create)
            print(f"Created {len(created)} elements")

            # READ - Get elements by class
            print("\nReading elements by class...")
            person_elements = await client.get_elements_by_class("person")
            print(f"Found {len(person_elements)} person elements")

            # READ - Get specific element
            print("\nReading specific element...")
            alice = await client.get_element_by_id("python-crud-1")
            if alice and "properties" in alice:
                print(f"Alice: {alice['properties']['name']}")
            else:
                print("Failed to get Alice")

            # UPDATE - Patch elements (partial update)
            print("\nPatching elements...")
            patches = [
                {
                    "id": "python-crud-1",
                    "type": "node",
                    "classId": "person",
                    "properties": {
                        "name": "Alice Python Updated",
                        "age": 31,  # Updated age
                    },
                }
            ]

            patched = await client.patch_elements(patches)
            print(f"Patched {len(patched)} elements")

            # Verify update
            updated_alice = await client.get_element_by_id("python-crud-1")
            if updated_alice and "properties" in updated_alice:
                print(f"Updated Alice age: {updated_alice['properties']['age']}")
            else:
                print("Failed to get updated Alice")

            # DELETE - Delete elements
            print("\nDeleting elements...")
            deleted_ids = await client.delete_elements(
                ["python-crud-1", "python-crud-2"]
            )
            print(f"Deleted elements: {deleted_ids}")

            # Verify deletion
            try:
                await client.get_element_by_id("python-crud-1")
                print("ERROR: Element should have been deleted!")
            except ElementNotFoundError:
                print("Confirmed: Element was successfully deleted")

        except GraphApiError as e:
            print(f"Graph API Error: {e}")


async def example_error_handling():
    """
    Example showing proper error handling for various scenarios.
    """
    print("\n=== Error Handling Example ===")

    async with RestGraphApiClient() as client:
        # Test different error scenarios

        # 1. Element not found
        print("Testing element not found...")
        try:
            await client.get_element_by_id("non-existent-id")
        except ElementNotFoundError as e:
            print(f"✓ Caught ElementNotFoundError: {e}")

        # 2. Validation error
        print("\nTesting validation error...")
        try:
            # Invalid data (missing required fields)
            invalid_elements = [
                {
                    "type": "node",
                    # Missing id and classId
                    "properties": {"name": "Invalid"},
                }
            ]
            await client.create_elements(invalid_elements)
        except ValidationError as e:
            print(f"✓ Caught ValidationError: {e}")
        except GraphApiError as e:
            print(f"✓ Caught GraphApiError: {e}")

        # 3. Class not found
        print("\nTesting class not found...")
        try:
            await client.get_elements_by_class("non-existent-class")
        except ElementNotFoundError as e:
            print(f"✓ Caught ElementNotFoundError for class: {e}")


async def example_schema_operations():
    """
    Example showing schema-related operations.
    """
    print("\n=== Schema Operations Example ===")

    async with RestGraphApiClient() as client:
        try:
            # Get all schemas in default format
            print("Getting all schemas (default format)...")
            schemas_default = await client.get_all_schemas("default")
            schema_names = list(schemas_default.keys())
            print(f"Found schemas: {schema_names}")

            # Get all schemas in JSON Schema format
            print("\nGetting all schemas (JSON Schema format)...")
            schemas_json = await client.get_all_schemas("jsonschema")
            print(f"JSON Schema format count: {len(schemas_json)}")

            # Get specific schema
            # Find a non-null schema to test with
            valid_schema_names = [
                name for name, schema in schemas_default.items() if schema is not None
            ]
            if valid_schema_names:
                first_schema_id = valid_schema_names[0]
                print(f"\nGetting specific schema: {first_schema_id}...")

                schema_default = await client.get_schema_by_id(
                    first_schema_id, "default"
                )
                schema_json = await client.get_schema_by_id(
                    first_schema_id, "jsonschema"
                )

                print(
                    f"Default format keys: {list(schema_default.keys()) if schema_default else 'None'}"
                )
                print(
                    f"JSON Schema format keys: {list(schema_json.keys()) if schema_json else 'None'}"
                )
            else:
                print("\nNo valid schemas found to test individual retrieval")

        except GraphApiError as e:
            print(f"Schema Error: {e}")


async def example_complex_queries():
    """
    Example showing complex query operations.
    """
    print("\n=== Complex Queries Example ===")

    async with RestGraphApiClient() as client:
        try:
            # Example fluent query operations
            complex_query_operations = [
                {"method": "filterBySource", "params": {"source": "news"}},
                {
                    "method": "filterByElement",
                    "params": {
                        "element": {
                            "type": "node",
                            "classId": "bookmark",
                            "properties": {},
                        }
                    },
                },
            ]

            print("Executing complex query...")
            results = await client.execute_complex_query(complex_query_operations)
            print(f"Query returned {len(results)} results")

            # Simple element query
            simple_query = {"classId": "person"}

            print("\nExecuting simple element query...")
            element_results = await client.query_elements(simple_query)
            print(f"Element query returned {len(element_results)} results")

        except GraphApiError as e:
            print(f"Query Error: {e}")


async def main():
    """
    Main function that runs all examples.
    """
    print("Python Graph API REST Client Examples")
    print("=" * 50)

    examples = [
        example_basic_rest_client,
        example_element_store_with_rest,
        example_crud_operations,
        example_error_handling,
        example_schema_operations,
        example_complex_queries,
    ]

    for example in examples:
        try:
            await example()
            await asyncio.sleep(1)  # Brief pause between examples
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")

    print("\n" + "=" * 50)
    print("Examples completed!")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
