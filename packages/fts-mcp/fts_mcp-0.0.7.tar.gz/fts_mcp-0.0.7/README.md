# Full Text Search MCP

A full-text search server using Tantivy that can be used as both an MCP (Model Context Protocol) server and a Python library.

## Installation

```bash
pip install -e .
```

## Usage

### As an MCP Server (CLI)

```bash
python -m full_text_search.mcp \
    --data-file data.jsonl \
    --id-column id \
    --text-column content \
    --searchable-columns title content tags \
    --description "My document search index" \
    --host 0.0.0.0 \
    --port 8000
```

### As a Python Library

The `FullTextSearchMCP` class can be imported and used programmatically:

```python
from full_text_search.mcp import FullTextSearchMCP

# Create and initialize the search server
server = FullTextSearchMCP()
server.initialize(
    data_file="data.jsonl",
    id_column="id", 
    text_column="content",
    searchable_columns=["title", "content", "tags"],
    description="My search index"
)

# Use search functionality directly
results = server.search("python programming", limit=10)
print(results)

# Retrieve specific documents
docs = server.read_documents(["doc1", "doc2"])
print(docs)

# Or run as MCP server programmatically
server.run_server(host="localhost", port=8080)
```

### Creating an MCP Server Instance

You can also create a FastMCP server instance for integration with other applications:

```python
from full_text_search.mcp import FullTextSearchMCP

server = FullTextSearchMCP()
server.initialize(
    data_file="data.jsonl",
    id_column="id",
    text_column="content", 
    searchable_columns=["title", "content"],
    description="My search index"
)

# Get the FastMCP server instance
mcp_server = server.create_mcp_server()
# Use mcp_server with your preferred transport
```

## Data Format

The input data should be in JSONL format (one JSON object per line):

```jsonl
{"id": "1", "title": "Python Basics", "content": "Introduction to Python programming..."}
{"id": "2", "title": "Advanced Python", "content": "Advanced concepts in Python..."}
```

## Features

- **Full-text search** using Tantivy search engine
- **Modular design** - can be used as a library or standalone server
- **No global state** - all functionality encapsulated in the `FullTextSearchMCP` class
- **MCP protocol support** for integration with AI assistants
- **Flexible column mapping** - specify which columns to search and how to identify documents
- **Document retrieval** by ID for full content access

## API Methods

### `FullTextSearchMCP.initialize()`

Initialize the search index with your data.

**Parameters:**
- `data_file`: Path to JSONL file containing documents
- `id_column`: Name of column containing unique document IDs  
- `text_column`: Name of main text column for content
- `searchable_columns`: List of column names to make searchable
- `description`: Description of what this search index contains
- `index_path`: Optional path for index storage (defaults to `{data_file}_index`)

### `FullTextSearchMCP.search(query, limit=5)`

Search documents and return previews.

**Parameters:**
- `query`: Search query string
- `limit`: Maximum number of results to return

**Returns:** Formatted string with search results and previews

### `FullTextSearchMCP.read_documents(document_ids)`

Retrieve full content for specific document IDs.

**Parameters:**
- `document_ids`: List of document IDs to retrieve

**Returns:** Formatted string with full document content

### `FullTextSearchMCP.create_mcp_server()`

Create a FastMCP server instance with search tools.

**Returns:** FastMCP server instance

### `FullTextSearchMCP.run_server(host="0.0.0.0", port=8000)`

Run the MCP server.

**Parameters:**
- `host`: Host address for the server
- `port`: Port number for the server