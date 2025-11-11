"""
Simple Graph API Client Example

This example demonstrates the most common use cases for the Python Graph API REST client
to communicate with the TypeScript Bun/Hono/OpenAPI endpoint at http://localhost:9800/reference

Usage:
    python simple_example.py
"""

import asyncio

from graph_api import GraphApiError, RestGraphApiClient


async def main():
    """Main example showing common operations."""

    print("Graph API REST Client - Simple Example")
    print("=" * 50)

    # Create client (defaults to http://localhost:9800)
    async with RestGraphApiClient() as client:

        try:
            print("\n1. Getting all elements...")
            all_elements = await client.get_all_elements()
            print(f"   Found {len(all_elements)} elements")

            print("\n2. Getting all schemas...")
            schemas = await client.get_all_schemas()
            schema_list = list(schemas.get("schema", {}).keys())
            print(f"   Found schemas: {schema_list}")

            print("\n3. Creating a test element...")
            test_element = [
                {
                    "id": "python-test-" + str(hash("test"))[:8],
                    "type": "node",
                    "classId": "person",  # Adjust based on your schemas
                    "properties": {
                        "name": "Python Test User",
                        "description": "Created from Python REST client",
                        "tags": ["python", "test"],
                    },
                    "source": "python-example",
                }
            ]

            created = await client.create_elements(test_element)
            print(f"   Created element with ID: {created[0]['id']}")
            element_id = created[0]["id"]

            print("\n4. Retrieving the created element...")
            retrieved = await client.get_element_by_id(element_id)
            if retrieved and "properties" in retrieved:
                print(f"   Retrieved: {retrieved['properties']['name']}")
            else:
                print("   Failed to retrieve element")

            print("\n5. Updating the element...")
            updated_data = [
                {
                    "id": element_id,
                    "type": "node",
                    "classId": "person",
                    "properties": {
                        "name": "Python Test User - Updated",
                        "description": "Updated from Python REST client",
                    },
                }
            ]

            await client.patch_elements(updated_data)
            print("   Element updated successfully")

            print("\n6. Querying elements by source...")
            query_result = await client.query_elements({"source": "python-example"})
            print(f"   Query found {len(query_result)} elements")

            print("\n7. Getting elements by class...")
            if schema_list:
                class_elements = await client.get_elements_by_class("person")
                print(f"   Found {len(class_elements)} person elements")

            print("\n8. Cleaning up - deleting test element...")
            await client.delete_elements([element_id])
            print("   Test element deleted")

            print("\n✓ All operations completed successfully!")

        except GraphApiError as e:
            print(f"\n✗ Graph API Error: {e}")
            if e.details:
                print(f"   Details: {e.details}")
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
