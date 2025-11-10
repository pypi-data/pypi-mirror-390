# Graph Elements Python Library

A Python library for graph-based data structures and queries, providing TypeScript-equivalent functionality for managing BaseElement, Node, Edge, MetaNode, and ElementStore classes with a powerful fluent GraphQuery API.

## Features

- 🧩 **Complete Graph Elements**: BaseElement, Node, Edge, MetaNode classes with full TypeScript parity
- 🔍 **Powerful Query API**: Fluent GraphQuery interface with comprehensive filtering operators
- 🌐 **REST API Client**: Async HTTP client for remote graph servers with automatic serialization
- 📡 **Real-time SSE Streaming**: Server-Sent Events for live updates on elements, schemas, and queries
- 🔄 **Synchronized Storage**: Bi-directional sync between local cache and remote server via SSE
- 🧹 **Clean API**: Simple `addNode()`, `createNode()`, `addEdge()` methods with `Props` class
- 🔗 **Shorter Query Syntax**: `classId()`, `where()`, `gte()`, `order_by()`, `first()` aliases
- 🗄️ **Flexible Storage**: ElementStore with pluggable backends (memory, REST, synchronized)
- 📊 **Rich Filtering**: Support for EQ, GT, LT, GTE, LTE, BETWEEN, CONTAINS, STARTS_WITH, ENDS_WITH, REGEX, IN operators
- 🔄 **Method Chaining**: Intuitive fluent API for complex query composition
- 📈 **Aggregation Functions**: count, sum, mean/avg, median, min, max operations
- 🎯 **Type Safe**: Full typing support with TypeScript-equivalent interfaces
- ⚡ **Async Support**: Async operations throughout (nodes, edges, queries, streaming)
- ✅ **Well Tested**: Comprehensive test suite with 361 test cases

## Installation

### For End Users

```bash
# Install from PyPI (recommended)
pip install graph-api-python

# Or install from GitHub (latest development version)
pip install git+https://github.com/damylen/graph-api-python.git@main

# Install specific version from GitHub
pip install git+https://github.com/damylen/graph-api-python.git@v0.1.0
```

### For Development

This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python package management.

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and set up the project
git clone <repository-url>
cd graph-api
uv sync
```

## Quick Start

```python
from graph_api import GraphQuery, ElementStore, Props

# Create an element store
store = ElementStore()

# Add nodes using the clean API
alice = store.addNode('person', name="Alice", age=30, tags=["developer", "senior"])
bob = store.addNode('person', name="Bob", age=28, tags=["designer"])

# Or create with Props object
props = Props(name="Carol", age=32, department="Engineering")
carol = store.addNode('person', props)

# Create edges between nodes
friendship = store.addEdge('friendship', alice, bob, strength=0.9, type="close_friends")

# Create queries with intuitive syntax
query = GraphQuery(store)

# Basic filtering
people = query.classId('person').r()

# Advanced filtering with method chaining
senior_devs = (query
    .classId('person')
    .gte('age', 25)
    .contains('tags', 'senior')
    .r())

# Aggregations
total_people = query.classId('person').count()
avg_age = query.classId('person').avg('age')

# Sorting and limiting
youngest = (query
    .classId('person')
    .order_by('age', 'asc')
    .first(5)
    .r())
```

## How It Works

### Local Storage (In-Memory)
The ElementStore maintains an in-memory graph that you can query and modify locally. Perfect for standalone applications or testing.

### REST API Integration
Connect to a remote TypeScript Graph API server (running on `http://localhost:9800`) to store and retrieve graph data:
- **Automatic Serialization**: Props objects and graph elements are automatically converted to/from JSON
- **Async Operations**: All REST calls are non-blocking
- **Class-based Filtering**: Query elements by their class ID efficiently

### Real-Time Synchronization with SSE
Server-Sent Events stream live updates from the server:
- **Synchronized Storage**: Combine local ElementStore with SSE for instant updates on every server change
- **Multiple Streams**: Monitor elements, schemas, queries, and health status concurrently
- **Conflict Resolution**: Server-wins strategy for automatic conflict resolution

```python
# Example: Synchronized storage with live updates
from graph_api import ElementStore, SynchronizedDataStorageConfig

sync_config = SynchronizedDataStorageConfig(
    base_url="http://localhost:9800",
    timeout=10.0
)
store = ElementStore(sync_config)

# Local operations are automatically synced to server via SSE
alice = store.addNode('person', name="Alice")

# Subscribe to live updates
async for event in store.stream_elements():
    print(f"Server updated: {event}")
```
```

## API Usage

The library provides a clean, intuitive API for graph operations:

### Node Operations

```python
from graph_api import ElementStore, Props

store = ElementStore()

# Add nodes with keyword arguments
person = store.addNode('person', name="John", age=30, city="Boston")

# Add nodes with Props object
props = Props(name="Alice", age=28, job="Engineer")
alice = store.addNode('person', props)

# Create nodes without adding to store
node = store.createNode('person', name="Bob", age=25)
# Later add to store
store.addNode(node)

# Async versions available
async def add_user():
    user = await store.addNodeAsync('user', name="Async User", active=True)
    return user
```

### Edge Operations

```python
# Create relationships between nodes
alice = store.addNode('person', name="Alice")
bob = store.addNode('person', name="Bob")

# Add edge with properties
friendship = store.addEdge('friendship', alice, bob,
                          strength=0.9, type="close_friends")

# Create edge without adding to store
edge = store.createEdge('relationship', alice, bob,
                       Props(type="colleague", department="Engineering"))

# Async edge creation
async def create_relationship():
    rel = await store.addEdgeAsync('follows', alice, bob, since="2023")
    return rel
```

### Props Class

The `Props` class provides a simple way to define element properties:

```python
from graph_api import Props

# Create props with keyword arguments
props = Props(name="Alice", age=30, job="Engineer")

# Props behaves like a dictionary
props['department'] = "Engineering"
assert props['name'] == "Alice"
assert 'age' in props
```



## Query Methods

### Filtering Methods

- `classId(class_id)`: Filter by element class ID
- `where(key, operator, value)`: Filter by property with operator
- `where(key, value)`: Filter by property equality (shorthand)
- `prop(key, value)`: Alias for property equality
- `gt(key, value)`, `lt(key, value)`, `gte(key, value)`, `lte(key, value)`: Comparison operators
- `contains(key, value)`: Check if property contains value
- `startsWith(key, value)`, `endsWith(key, value)`: String matching

### Sorting and Limiting

- `order_by(property, direction)`: Sort by property ('asc' or 'desc')
- `first(n)`: Limit to first N results
- `last(n)`: Limit to last N results

### Aggregation Methods

- `count()`: Count results
- `sum(property)`: Sum numeric property
- `avg(property)`: Average of numeric property
- `median(property)`: Median of numeric property
- `min(property)`: Minimum of numeric property
- `max(property)`: Maximum of numeric property

## REST Client API

Connect to a TypeScript Graph API server for remote graph operations. The client handles serialization automatically.

### Configuration

```python
from graph_api import RestGraphApiClient, RestClientConfig

# Configure the client
config = RestClientConfig(
    base_url="http://localhost:9800",
    timeout=30.0,
    verify_ssl=True
)

# Use the client
async with RestGraphApiClient(config) as client:
    # Get all elements
    all_elements = await client.get_all_elements()

    # Get single element by ID
    element = await client.get_element_by_id("element-id")

    # Get elements by class ID (NEW FEATURE)
    result = await client.get_elements_by_class_id("Person")
    print(f"Found {result['count']} Person elements")
    for person in result['data']:
        print(f"  - {person['properties'].get('name', 'Unknown')}")

    # Legacy method (returns list only)
    persons = await client.get_elements_by_class("Person")

    # Create/update elements
    new_elements = [
        {
            "id": "person-1",
            "classId": "Person",
            "type": "node",
            "properties": {"name": "Alice", "age": 30},
            "source": "python"
        }
    ]
    created = await client.create_elements(new_elements)

    # Query elements
    query_result = await client.query_elements({
        "classId": "Person",
        "filters": [{"property": "age", "operator": "gt", "value": 25}]
    })
```

### REST Data Storage Integration

Use REST backend with ElementStore for seamless remote data access:

```python
from graph_api import ElementStore, ElementStoreConfig
from graph_api import RestDataStorage, RestDataStorageConfig

# Configure REST storage
rest_config = RestDataStorageConfig(
    base_url="http://localhost:9800",
    timeout=30.0
)

# Create REST storage instance
rest_storage = RestDataStorage(rest_config.to_rest_config())

# Configure ElementStore with REST backend
store_config = ElementStoreConfig(
    data_config=rest_config,
    operation=rest_storage
)

# Create ElementStore
store = ElementStore(store_config)

# Load data from remote API
await store.load_elements()

# Use normal ElementStore methods - data is automatically synced with API
person = store.addNode('Person', name="Bob", age=35)

# Get elements by class ID from remote storage
persons = await store.get_elements_by_class_id("Person")
print(f"Found {len(persons)} persons in remote storage")

# Direct REST storage access
filtered_elements = await rest_storage.get_elements_by_class_id("Person")
```

### Error Handling

The REST client provides specific exception types for different error conditions:

```python
from graph_api import (
    GraphApiError, ValidationError, ElementNotFoundError,
    QueryError, InternalServerError, HttpError
)

try:
    result = await client.get_elements_by_class_id("NonExistentClass")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except ElementNotFoundError as e:
    print(f"No elements found: {e.message}")
except InternalServerError as e:
    print(f"Server error: {e.message}")
except HttpError as e:
    print(f"HTTP error: {e.message}")
except GraphApiError as e:
    print(f"General API error: {e.message}")
```

## Server-Sent Events (SSE) Integration

Receive real-time updates from the server using streaming. Use with synchronized storage for automatic local cache updates.

### Streaming Methods

```python
from graph_api import RestGraphApiClient

async with RestGraphApiClient() as client:
    # Stream all elements in real-time
    async for event in client.stream_elements():
        print(f"Element event: {event}")
        # Handle element creation, updates, deletions

    # Stream specific element changes
    async for event in client.stream_element_by_id("person-123"):
        print(f"Person 123 updated: {event}")

    # Stream elements by class ID
    async for event in client.stream_elements_by_class_id("Person"):
        print(f"Person element changed: {event}")

    # Stream schema changes
    async for event in client.stream_schema():
        print(f"Schema updated: {event}")

    # Stream continuous query results
    query = {"classId": "Person", "filters": [{"property": "active", "value": True}]}
    async for event in client.stream_query(query):
        print(f"Active person changed: {event}")

    # Stream health status
    async for event in client.stream_health():
        print(f"Health status: {event}")

    # Stream all graph events
    async for event in client.stream_events():
        print(f"Graph event: {event}")
```

### SSE Event Format

SSE events are JSON objects containing event data:

```json
{
  "type": "element_created",
  "elementId": "person-123",
  "data": {
    "id": "person-123",
    "classId": "Person",
    "type": "node",
    "properties": {"name": "Alice", "age": 30}
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Concurrent Streaming

Monitor multiple streams simultaneously:

```python
import asyncio

async def monitor_elements():
    async with RestGraphApiClient() as client:
        # Create concurrent monitoring tasks
        tasks = [
            asyncio.create_task(monitor_stream("Elements", client.stream_elements())),
            asyncio.create_task(monitor_stream("Health", client.stream_health())),
            asyncio.create_task(monitor_stream("Schema", client.stream_schema())),
        ]

        # Run for a limited time or until cancelled
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=300.0)

async def monitor_stream(name: str, stream):
    """Monitor a specific stream."""
    count = 0
    async for event in stream:
        count += 1
        print(f"{name} Event {count}: {event}")
        if count >= 10:  # Limit events per stream
            break
```

### SSE Error Handling

SSE streams include built-in error handling:

```python
try:
    async for event in client.stream_elements():
        process_event(event)
except HttpError as e:
    print(f"SSE connection failed: {e}")
except Exception as e:
    print(f"SSE processing error: {e}")
```

### SSE Connectivity Testing

Check if SSE endpoints are available:

```python
from graph_api.examples.sse_examples import sse_connectivity_test

# Run connectivity test
await sse_connectivity_test()
```

### Example Usage

```python
# Chain methods for complex queries
young_engineers = (query
    .classId('person')
    .where('department', 'Engineering')
    .lt('age', 35)
    .order_by('age', 'desc')
    .first(10)
    .r())

# Use comparison operators
seniors = query.classId('person').gte('age', 30).r()

# Aggregations
avg_age = query.classId('person').avg('age')
total_people = query.classId('person').count()
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and development workflows.

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### Setup

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd graph-api

# Create virtual environment and install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ -v --cov=graph_api --cov-report=html

# Run specific test file
uv run pytest tests/test_graph_query.py -v
```

### Code Quality

```bash
# Run linting
uv run ruff check .

# Format code
uv run black .

# Sort imports
uv run isort .

# Type checking
uv run mypy graph_api/

# All quality checks
uv run ruff check . && uv run black --check . && uv run isort --check-only . && uv run mypy graph_api/
```

### Adding Dependencies

```bash
# Add runtime dependency
uv add requests

# Add development dependency
uv add --dev pytest-mock

# Update dependencies
uv lock --upgrade
```

### Using Makefile (Optional)

For convenience, common development tasks are available via Makefile:

```bash
# Set up development environment
make dev

# Run all quality checks and tests
make qa

# Run tests with coverage
make test

# Format code and fix linting
make lint-fix

# Build package
make build

# See all available commands
make help
```

### Test Coverage

- ✅ 297 tests passing
- ✅ All filtering operators tested
- ✅ Method chaining validated
- ✅ Edge cases covered
- ✅ Aggregation functions verified
- ✅ Clean API methods tested
- ✅ Async operations validated

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
