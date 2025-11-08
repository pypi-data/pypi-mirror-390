# Chromia Console Client

A Python client library for interacting with the Chromia Console Vector Database API. This client provides a simple and type-safe way to manage vector collections, perform similarity searches, and work with embeddings.


## Installation

```bash
pip install de_console_client
```

## Quick Start

```python
from de_console_client import Configuration, ApiClient, ChromiaVectorDBApi
from de_console_client.models import VectorCollection

# 1. Configure the client
configuration = Configuration(
    host='https://chromia-console.chromia.dev',
    brid='YOUR_BLOCKCHAIN_RID',
    network='mainnet',  # or 'testnet' or 'https://node0.testnet.chromia.com'
    chromia_api_key='YOUR_API_KEY'
)

# 2. Create the API client
with ApiClient(configuration) as api_client:
    client = ChromiaVectorDBApi(api_client)
    
    # 3. Create a collection
    collection = VectorCollection(
        name='my_first_collection',
        dimension=384,  # Vector dimension for embeddings
        index='hnsw_cosine',
        query_max_vector=10,
        store_batch_size=100
    )
    client.add_collection(collection)
    
    # 4. Store some text as vector embeddings (batch operation)
    client.create_vector_embedding_batch(
        'my_first_collection',
        [
            'The quick brown fox jumps over the lazy dog',
            'Chromia is a relational blockchain platform',
            'Vector databases enable semantic search'
        ]
    )
    
    # 5. Search using text query
    search_results = client.search_objects(
        collection='my_first_collection',
        body='tell me about Chromia',
        max_vectors=2       # return top 2 results
    )
    
    print('Search results:', search_results.payloads)
```

## Configuration

The `Configuration` object accepts the following parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `host` | str | Yes | Base URL of the Chromia Console API |
| `brid` | str | Yes | Blockchain RID (Identifier) |
| `network` | str | Yes | Network name (e.g., 'mainnet', 'testnet') or url|
| `chromia_api_key` | str | Yes | API key for authentication |

### Environment Variables

You can use environment variables to configure the client:

```python
import os
from de_console_client import Configuration

configuration = Configuration(
    host=os.getenv('CHROMIA_CONSOLE_BASE_PATH'),
    brid=os.getenv('BRID'),
    network=os.getenv('NETWORK', 'mainnet'),
    chromia_api_key=os.getenv('API_KEY')
)
```

## API Reference

### Collection Management

- `get_collections()` - Get all available collections
- `add_collection(collection)` - Create a new collection
- `change_collection(changes)` - Update collection configuration
- `remove_collection(name)` - Remove a collection

### Vector Operations

- `create_vector(collection, vector_request)` - Create a single vector
- `create_vector_batch(collection, batch_request)` - Create multiple vectors
- `create_vector_batch_chunked(collection, batch_request)` - Create vectors in chunks
- `delete_vector(collection, payload)` - Delete a vector
- `delete_vector_batch(collection, payloads)` - Delete multiple vectors

### Embedding Operations

- `create_vector_embedding(collection, payload)` - Create text embedding
- `create_vector_embedding_batch(collection, payloads)` - Create text embeddings batch
- `create_vector_embedding_batch_chunked(collection, payloads)` - Create text embeddings in chunks
- `create_image_embedding(collection, image_request)` - Create image embedding
- `create_image_embedding_batch(collection, batch_request)` - Create image embeddings batch

### Search Operations

- `search_objects(collection, query, max_distance=None, max_vectors=None)` - Search by text
- `get_closest_objects(collection, vector_request, max_distance=None, max_vectors=None)` - Search by vector
- `get_closest_objects_with_distance(collection, vector_request, max_distance=None, max_vectors=None)` - Search with distances
- `get_closest_objects_with_filter(collection, filter_request, max_distance=None, max_vectors=None)` - Search with filter
- `search_images(collection, image_request, max_distance=None, max_vectors=None)` - Search similar images

### Import Operations

- `get_default_data_with_embedding()` - Get default import data
- `import_default_data(collection)` - Import default data

## Response Types

### TransactionResultBody

All write operations return a `TransactionResultBody`:

```python
{
    'tx_rid': str,         # Transaction ID
    'status': str,         # 'confirmed', 'waiting', 'pending', or 'rejected'
    'reject_reason': str   # Only present if status is 'rejected' (optional)
}
```

### GetClosestResponse

Search operations return a `GetClosestResponse`:

```python
{
    'payloads': [str]      # Array of matched payloads
}
```

### PayloadDistance

Distance-aware searches return `List[PayloadDistance]`:

```python
{
    'text': str,           # Payload text
    'distance': float      # Distance from query vector
}
```

## Error Handling

The client uses standard Python exceptions. Handle errors using try-except:

```python
from de_console_client import ApiClient, ChromiaVectorDBApi, Configuration
from de_console_client.rest import ApiException

configuration = Configuration(
    host='https://chromia-console.chromia.dev',
    brid='YOUR_BLOCKCHAIN_RID',
    network='mainnet',
    chromia_api_key='YOUR_API_KEY'
)

try:
    with ApiClient(configuration) as api_client:
        client = ChromiaVectorDBApi(api_client)
        response = client.create_vector(
            'my_collection',
            vector_request
        )
        print('Success:', response)
except ApiException as e:
    # API-specific error occurred
    print(f'API Exception: {e.status}')
    print(f'Reason: {e.reason}')
    print(f'Body: {e.body}')
except Exception as e:
    # General error occurred
    print(f'Error: {str(e)}')
```
