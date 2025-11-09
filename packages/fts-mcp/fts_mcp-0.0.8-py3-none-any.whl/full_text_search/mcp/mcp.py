#!/usr/bin/env python3
"""
MCP server for full-text search using Tantivy.
Initializes with a fixed JSONL file and provides search/read tools via HTTP.
"""

import argparse
import asyncio
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, TypeAlias, Union

import yaml
from fastmcp import FastMCP
from pydantic import BaseModel

from ..index import TantivySearch


@dataclass
class IndexConfig:
    """Configuration for a single search index."""

    name: str
    description: str
    data_file: str
    id_column: str
    text_column: str
    searchable_columns: list[str]
    index_path: Optional[str] = None
    include_fields: Optional[list[str]] = None
    exclude_fields: Optional[list[str]] = None


def load_config_from_yaml(config_path: str) -> tuple[str, str, list[IndexConfig], dict]:
    """Load server and indices configuration from YAML file.

    Expected YAML structure:
    server:
      name: "my_search_server"
      description: "Multi-index search server"
      mount: "/my-cool-mcp-server" # defaults to /mcp/
      host: "0.0.0.0"  # optional
      port: 8000       # optional

    indices:
      - name: "books"
        description: "Programming books collection"
        data_file: "data/books.jsonl"
        id_column: "id"
        text_column: "content"
        searchable_columns: ["title", "content", "author"]
        index_path: "data/books_index"  # optional
        include_fields: ["title", "content"]  # optional: only these fields are searchable
        exclude_fields: ["metadata"]  # optional: all fields except these are searchable
      - name: "articles"
        description: "News articles"
        data_file: "data/articles.jsonl"
        id_column: "doc_id"
        text_column: "body"
        searchable_columns: ["headline", "body", "category"]

    Returns:
        tuple: (server_name, server_description, list_of_index_configs)
    """
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Extract server configuration
    server_config = config.get("server", {})
    server_name = server_config.get("name")
    server_description = server_config.get("description")

    if not server_name:
        raise ValueError("Server name is required in YAML config")
    if not server_description:
        raise ValueError("Server description is required in YAML config")

    # Extract indices configuration
    indices_config = config.get("indices", [])
    if not indices_config:
        raise ValueError("At least one index must be defined in YAML config")

    # Convert to IndexConfig objects
    index_configs = []
    for idx_config in indices_config:
        # Validate required fields
        required_fields = [
            "name",
            "description",
            "data_file",
            "id_column",
            "text_column",
            "searchable_columns",
        ]
        missing_fields = [field for field in required_fields if field not in idx_config]
        if missing_fields:
            raise ValueError(f"Missing required fields for index: {missing_fields}")

        index_config = IndexConfig(
            name=idx_config["name"],
            description=idx_config["description"],
            data_file=idx_config["data_file"],
            id_column=idx_config["id_column"],
            text_column=idx_config["text_column"],
            searchable_columns=idx_config["searchable_columns"],
            index_path=idx_config.get("index_path"),  # Optional
            include_fields=idx_config.get("include_fields"),  # Optional
            exclude_fields=idx_config.get("exclude_fields"),  # Optional
        )
        index_configs.append(index_config)

    return server_name, server_description, index_configs, server_config


def load_jsonl_data(file_path: str) -> list[dict]:
    """Load data from a JSONL file with auto-conversion for legacy schema."""
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                record = json.loads(line)

                # Auto-convert legacy schema fields
                if "text" in record and "content" not in record:
                    record["content"] = record["text"]

                if "summary" in record and "description" not in record:
                    record["description"] = record["summary"]

                data.append(record)
    return data


def ensure_id_column(data: list[dict], id_column: str) -> list[dict]:
    """Ensure the specified id_column exists, adding it with index values if missing."""
    if not data:
        return data

    # Check if id_column exists in the first record
    if id_column not in data[0]:
        # If id_column is 'id' and it doesn't exist, add it using index
        if id_column == "id":
            for i, record in enumerate(data):
                record["id"] = str(i)
        else:
            # For non-'id' columns, still add with index but warn
            print(f"Warning: Column '{id_column}' not found. Adding with index values.")
            for i, record in enumerate(data):
                record[id_column] = str(i)

    return data


def preview_text(text: str, max_length: int = 200) -> str:
    """Create a preview of text content."""
    if not text or len(text) <= max_length:
        return text
    return text[:max_length] + " [...]"


def normalize_field_value(value) -> str:
    """Convert field value to string, handling JSON/list columns."""
    if value is None:
        return ""
    elif isinstance(value, (list, tuple)):
        # Join list/tuple elements with spaces
        return " ".join(str(item) for item in value if item is not None)
    elif isinstance(value, dict):
        # For dict/JSON, join all values
        return " ".join(str(v) for v in value.values() if v is not None)
    else:
        return str(value)


class FullTextSearchMCP:
    """Encapsulates full-text search MCP server functionality with support for multiple indices."""

    def __init__(
        self,
        server_name: str,
        server_description: str,
        indices: Optional[list[IndexConfig]] = None,
        max_workers: int = 4,
    ):
        """Initialize the MCP server.

        Args:
            server_name: Name of the server
            server_description: Description of the server
            indices: List of index configurations
            max_workers: Number of worker threads for search operations (default: 4)
        """
        self.server_name = server_name
        self.server_description = server_description
        self.indices: dict[
            str, dict
        ] = {}  # index_name -> {config, search_index, original_data}
        self.citations = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        if indices:
            for index_config in indices:
                self.add_index(index_config)

    def __del__(self):
        """Cleanup executor on object destruction."""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=True)

    def add_index(self, config: IndexConfig) -> None:
        """Add and initialize a single index."""
        print(f"Adding index '{config.name}'...")

        # Load data
        print(f"Loading data from {config.data_file}...")
        original_data = load_jsonl_data(config.data_file)
        if not original_data:
            raise ValueError(f"No data found in file {config.data_file}")

        # Ensure id column exists (auto-generate if missing and id_column is 'id')
        original_data = ensure_id_column(original_data, config.id_column)

        # Validate columns exist
        sample_record = original_data[0]
        missing_cols = []
        if config.id_column not in sample_record:
            missing_cols.append(config.id_column)
        if config.text_column not in sample_record:
            missing_cols.append(config.text_column)
        for col in config.searchable_columns:
            if col not in sample_record:
                missing_cols.append(col)

        if missing_cols:
            raise ValueError(
                f"Missing columns in data for index '{config.name}': {missing_cols}"
            )

        # Set default index path if not provided
        index_path = config.index_path
        if index_path is None:
            data_file_path = Path(config.data_file)
            index_path = str(data_file_path.parent / f"{data_file_path.stem}_index")

        # Create search index
        print(f"Building search index at {index_path}...")
        search_index = TantivySearch(
            index_path,
            include_fields=config.include_fields,
            exclude_fields=config.exclude_fields,
        )

        # Build index with all searchable columns plus id
        all_columns = [config.id_column, config.text_column] + [
            col
            for col in config.searchable_columns
            if col not in [config.id_column, config.text_column]
        ]

        # Filter records to only include relevant columns and normalize values
        filtered_records = []
        for record in original_data:
            filtered_record = {}
            for col in all_columns:
                if col in record:
                    # Normalize field values (handles JSON/list columns)
                    filtered_record[col] = normalize_field_value(record[col])

            # Ensure id is string
            filtered_record["id"] = str(filtered_record.get(config.id_column, ""))
            # Remove the original id column if it's different from "id"
            if config.id_column != "id" and config.id_column in filtered_record:
                del filtered_record[config.id_column]
            filtered_records.append(filtered_record)

        # Build index without deduplication
        search_index.build_index(filtered_records, deduplicate_strategy=None)

        # Cache original documents for efficient fetching
        search_index.cache_documents_for_fetch(original_data, config.id_column)

        # Store the index data
        self.indices[config.name] = {
            "config": config,
            "search_index": search_index,
            "original_data": original_data,
            "index_path": index_path,
        }

        # Add all documents to citations dict as index_name:doc_id -> {title, url}
        for record in original_data:
            doc_id = str(record.get(config.id_column, ""))
            citation_key = f"{config.name}:{doc_id}"
            citation_value = {}

            # Add title if available
            if "title" in record:
                citation_value["title"] = record["title"]

            # Add url if available
            if "url" in record:
                citation_value["url"] = record["url"]

            # Only add to citations if we have title or url
            if citation_value:
                self.citations[citation_key] = citation_value

        print(
            f"Successfully initialized index '{config.name}' with {len(original_data)} documents"
        )

    async def search(
        self, queries: list[str], index_name: str = "default", limit: int = 5
    ) -> str:
        """Search documents using multiple queries with result fusion and return previews."""
        if index_name not in self.indices:
            available = list(self.indices.keys())
            return (
                f"Error: Index '{index_name}' not found. Available indices: {available}"
            )

        index_data = self.indices[index_name]
        search_index = index_data["search_index"]
        config = index_data["config"]

        try:
            # Run blocking search in thread pool
            loop = asyncio.get_event_loop()

            def _search():
                # Search across all searchable columns
                all_searchable = [config.text_column] + config.searchable_columns
                # Remove duplicates while preserving order
                search_fields = []
                for field in all_searchable:
                    if field not in search_fields and field != config.id_column:
                        search_fields.append(field)

                return search_index.search(queries, search_fields, limit=limit)

            results = await loop.run_in_executor(self.executor, _search)

            if not results:
                query_str = "', '".join(queries)
                return f"No results found for queries: ['{query_str}'] in index '{index_name}'"

            # Format results with previews
            query_str = "', '".join(queries)
            formatted_results = [
                f"Found {len(results)} results for queries ['{query_str}'] in index '{index_name}':\n"
            ]

            for i, result in enumerate(results, 1):
                content = result.content
                doc_id = result.id
                score = result.score

                # Get preview of main text content
                main_text = content.get(config.text_column, "")
                preview = preview_text(main_text)

                formatted_results.append(f"Result {i} (Score: {score:.3f})")
                formatted_results.append(f"ID: {doc_id}")
                formatted_results.append(f"Preview: {preview}")

                # Show other searchable fields (abbreviated)
                for field in config.searchable_columns:
                    if field != config.text_column and field in content:
                        value = content[field]
                        if len(str(value)) > 100:
                            value = str(value)[:100] + "..."
                        formatted_results.append(f"{field}: {value}")

                formatted_results.append("")  # Empty line between results

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error during search in index '{index_name}': {str(e)}"

    async def read_documents(
        self, document_ids: list[str], index_name: str = "default"
    ) -> str:
        """Retrieve full content for specific document IDs."""
        if index_name not in self.indices:
            available = list(self.indices.keys())
            return (
                f"Error: Index '{index_name}' not found. Available indices: {available}"
            )

        index_data = self.indices[index_name]
        search_index = index_data["search_index"]

        try:
            # Run in thread pool for consistency
            loop = asyncio.get_event_loop()

            def _fetch():
                # Use TantivySearch's cached fetch method
                return search_index.fetch(document_ids)

            results, found_ids, missing_ids = await loop.run_in_executor(
                self.executor, _fetch
            )

            # Format results
            if not results:
                return f"No documents found for IDs: {document_ids} in index '{index_name}'"

            formatted_results = [
                f"Retrieved {len(results)} documents from index '{index_name}':\n"
            ]

            for i, record in enumerate(results):
                doc_id = found_ids[i]
                formatted_results.append(f"Document {i + 1} (ID: {doc_id})")
                formatted_results.append("-" * 3)

                # Show all fields
                for key, value in record.items():
                    formatted_results.append(f"{key}: {value}")

                formatted_results.append("")  # Empty line between documents

            if missing_ids:
                formatted_results.append(f"Missing document IDs: {missing_ids}")

            return "\n".join(formatted_results)

        except Exception as e:
            return f"Error retrieving documents from index '{index_name}': {str(e)}"

    def create_mcp_server(self) -> FastMCP:
        """Create MCP server with tools for each index."""
        mcp = FastMCP(self.server_name, stateless_http=True)

        # Create search and read tools for each index
        search_tool_name = "search"
        search_description = (
            "Search documents in one of the available search indices using one or more queries, returning return previews. "
            "Search uses full-text keyword search with Tantivy (not neural/embedding search), "
            "so longer queries or multiple queries with synonyms and more keywords can improve recall. "
            "Multi-queries will have their results fused with reciprocal rank fusion. "
            "Use multiple queries + higher limit for speed/breadth of search, since some queries may not return any results "
            "if you don't know what the index contains.\n\n"
            "Available indices:\n"
        )
        for index_name, index_data in self.indices.items():
            config = index_data["config"]
            search_description += f" - {index_name}: {config.description}\n"

        search_description += (
            "Args:\n\t\n\tindex (str): which index to search.\n\tqueries: List of search query strings (allows multiple queries for better results)"
            "\n\tlimit: Maximum total number of results to return (default 5)"
        )

        fetch_tool_name = "fetch"
        fetch_description = (
            "Retrieve full content from an index for specific document IDs from that index."
            "Args:\n\tindex (str): which index to read documents from."
            "\n\tdocument_ids: List of document IDs to retrieve"
        )

        batch_tool_name = "batch"
        batch_description = (
            "Execute any number of search/fetch operations in parallel. "
            "This is recommended to speed up your research, reducing "
            "latency for the end user. In order to use this tool, "
            "simply provide a list (array) of commands, where each command "
            'has name ("search" or "fetch"), index, and either queries + limit (for search) '
            "or document_ids (for fetch). For example:\n\n"
            '[\n\t{"name": "search", "index": "my_index", "queries": ["query1", "query2"], "limit": 5},\n'
            '\t{"name": "fetch", "index": "my_index", "document_ids": ["121", "3"]}\n]\n\n'
            "For example, you can read one set of documents while performing your "
            "next search in parallel; or perform several searches in parallel across several indices."
        )

        # We need to capture the index_name in the closure
        async def search_tool(index: str, queries: list[str], limit: int = 5) -> str:
            return await self.search(queries, index, limit)

        async def fetch_tool(index: str, document_ids: list[str]) -> str:
            return await self.read_documents(document_ids, index)

        class SearchCall(BaseModel):
            name: Literal["search"]
            index: str
            queries: list[str]
            limit: int = 5

        class FetchCall(BaseModel):
            name: Literal["fetch"]
            index: str
            document_ids: list[str]

        Command: TypeAlias = Union[SearchCall, FetchCall]  # type: ignore

        async def batch_tool(commands: list[Command]) -> str:
            # Execute all commands concurrently
            tasks = []
            for command in commands:
                if command.name == "search":
                    task = search_tool(command.index, command.queries, command.limit)
                elif command.name == "fetch":
                    task = fetch_tool(command.index, command.document_ids)
                else:
                    # Create a coroutine that returns an error message
                    async def error_task():
                        return "unknown command: " + command.name

                    task = error_task()
                tasks.append(task)

            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Convert exceptions to error messages
            formatted_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    formatted_results.append(
                        f"error executing {commands[i].name}: {str(result)}"
                    )
                else:
                    formatted_results.append(result)

            return "# Batch Tool Results\n\n" + "\n\n---\n\n".join(formatted_results)

        # Register the tools
        mcp.tool(name=search_tool_name, description=search_description)(search_tool)
        mcp.tool(name=fetch_tool_name, description=fetch_description)(fetch_tool)
        mcp.tool(name=batch_tool_name, description=batch_description)(batch_tool)

        # add resource for citations
        def get_citation(index: str, doc_id: str):
            key = f"{index}:{doc_id}"
            if key in self.citations:
                return self.citations[key]
            else:
                return None

        mcp.resource("cite://{index}/{doc_id}")(get_citation)
        return mcp

    def run_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the MCP server."""
        mcp = self.create_mcp_server()
        print(f"Starting MCP server on {host}:{port}")
        print(f"MCP endpoint: http://{host}:{port}/mcp")
        mcp.run(transport="streamable-http", host=host, port=port)


def main():
    """CLI entry point for running the MCP server."""
    parser = argparse.ArgumentParser(description="Full-text search MCP server")

    # Add config file option
    parser.add_argument(
        "--config",
        help="Path to YAML configuration file. If provided, other arguments are ignored.",
    )

    # Required arguments for server configuration (when not using config file)
    parser.add_argument(
        "--name",
        help="Name for the server (should be alpha + underscores)",
    )
    parser.add_argument(
        "--description",
        help="Description of what this search index contains",
    )
    parser.add_argument("--data-file", help="Path to JSONL file containing documents")
    parser.add_argument(
        "--id-column",
        help="Name of column containing unique document IDs",
    )
    parser.add_argument("--text-column", help="Name of main text column for content")
    parser.add_argument(
        "--searchable-columns",
        nargs="+",
        help="List of column names to make searchable",
    )

    # Optional arguments
    parser.add_argument(
        "--index-path", help="Path for index storage (defaults to data_file_index)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP server")
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Number of worker threads for concurrent search operations (default: 4)",
    )

    args = parser.parse_args()

    try:
        if args.config:
            # Load configuration from YAML file
            server_name, server_description, index_configs, server_config = (  # type: ignore
                load_config_from_yaml(args.config)
            )

            # Create multi-index search server with configurable max_workers
            max_workers = server_config.get("max_workers", args.max_workers)
            search_server = FullTextSearchMCP(
                server_name=server_name,
                server_description=server_description,
                indices=index_configs,
                max_workers=max_workers,
            )

            # Use host/port from YAML config if specified, otherwise use CLI args
            host = server_config.get("host", args.host)
            port = server_config.get("port", args.port)

        else:
            raise NotImplementedError("Must use YAML config to launch server.")

        # Start HTTP server
        search_server.run_server(host=host, port=port)

    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    main()
