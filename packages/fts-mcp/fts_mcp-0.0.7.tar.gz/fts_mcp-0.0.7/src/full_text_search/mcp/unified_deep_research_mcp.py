#!/usr/bin/env python3
"""
Multi Deep Research MCP servers compatible with OpenAI's specification.
Creates separate MCP server instances for each index (one per port).
Each server has exactly one search and one fetch tool as required by OpenAI.
"""

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI
from fastmcp import FastMCP

from ..index.tantivy_index import TantivySearch
from .mcp import (
    IndexConfig,
    ensure_id_column,
    load_jsonl_data,
    normalize_field_value,
    load_config_from_yaml,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DeepResearchResult:
    """Result format for deep research compatibility."""

    id: str
    title: str
    text: str
    url: str
    metadata: Optional[Dict[str, Any]] = None


class SingleIndexMCP:
    """Single-index MCP server for mounting into the unified server."""

    def __init__(self, config: IndexConfig, base_url: str = ""):
        self.config = config
        self.base_url = base_url.rstrip("/")
        self.search_index: Optional[TantivySearch] = None
        self.original_data: List[Dict] = []
        self.id_to_record: Dict[str, Dict] = {}

        # Initialize the index
        self._initialize_index()

    def _initialize_index(self) -> None:
        """Initialize the search index and load data."""
        logger.info(f"Initializing index '{self.config.name}'...")

        # Load data
        logger.info(f"Loading data from {self.config.data_file}...")
        self.original_data = load_jsonl_data(self.config.data_file)
        if not self.original_data:
            raise ValueError(f"No data found in file {self.config.data_file}")

        # Ensure id column exists
        self.original_data = ensure_id_column(self.original_data, self.config.id_column)

        # Create id lookup
        for record in self.original_data:
            doc_id = str(record.get(self.config.id_column, ""))
            self.id_to_record[doc_id] = record

        # Validate columns exist
        sample_record = self.original_data[0]
        missing_cols = []
        if self.config.id_column not in sample_record:
            missing_cols.append(self.config.id_column)
        if self.config.text_column not in sample_record:
            missing_cols.append(self.config.text_column)
        for col in self.config.searchable_columns:
            if col not in sample_record:
                missing_cols.append(col)

        if missing_cols:
            raise ValueError(f"Missing columns in data: {missing_cols}")

        # Set default index path if not provided
        index_path = self.config.index_path
        if index_path is None:
            data_file_path = Path(self.config.data_file)
            index_path = str(data_file_path.parent / f"{data_file_path.stem}_index")

        # Create search index
        logger.info(f"Building search index at {index_path}...")
        self.search_index = TantivySearch(index_path)

        # Build index with all searchable columns plus id
        all_columns = [self.config.id_column, self.config.text_column] + [
            col
            for col in self.config.searchable_columns
            if col not in [self.config.id_column, self.config.text_column]
        ]

        # Filter records to only include relevant columns and normalize values
        filtered_records = []
        for record in self.original_data:
            filtered_record = {}
            for col in all_columns:
                if col in record:
                    filtered_record[col] = normalize_field_value(record[col])

            # Ensure id is string
            filtered_record["id"] = str(filtered_record.get(self.config.id_column, ""))
            # Remove the original id column if it's different from "id"
            if (
                self.config.id_column != "id"
                and self.config.id_column in filtered_record
            ):
                del filtered_record[self.config.id_column]
            filtered_records.append(filtered_record)

        # Build index without deduplication
        self.search_index.build_index(filtered_records, deduplicate_strategy=None)

        logger.info(
            f"Successfully initialized index '{self.config.name}' with {len(self.original_data)} documents"
        )

    def _create_result(self, record: Dict, snippet: str = "") -> DeepResearchResult:
        """Create a DeepResearchResult from a record."""
        doc_id = str(record.get(self.config.id_column, ""))

        # Extract title - try different fields
        title = ""
        title_fields = ["title", "name", "headline", self.config.text_column]
        for field in title_fields:
            if field in record and record[field]:
                title = str(record[field])
                # If it's the text column, truncate for title
                if field == self.config.text_column and len(title) > 100:
                    title = title[:100] + "..."
                break

        if not title:
            title = f"Document {doc_id}"

        # Use snippet if provided, otherwise use text content
        text = snippet if snippet else str(record.get(self.config.text_column, ""))

        # Create URL
        url = (
            f"{self.base_url}/document/{doc_id}"
            if self.base_url
            else f"document://{doc_id}"
        )

        # Extract metadata (exclude main fields)
        metadata = {}
        exclude_fields = {self.config.id_column, self.config.text_column, "id"}
        for key, value in record.items():
            if key not in exclude_fields and value is not None:
                metadata[key] = value

        return DeepResearchResult(
            id=doc_id,
            title=title,
            text=text,
            url=url,
            metadata=metadata if metadata else None,
        )

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search documents and return results in deep research format."""
        if not query or not query.strip():
            return []

        if not self.search_index:
            raise RuntimeError("Search index not initialized")

        try:
            # Search across all searchable columns
            all_searchable = [self.config.text_column] + self.config.searchable_columns
            # Remove duplicates while preserving order
            search_fields = []
            for field in all_searchable:
                if field not in search_fields and field != self.config.id_column:
                    search_fields.append(field)

            # Use single query for deep research
            results = self.search_index.search([query], search_fields, limit=limit)

            # Convert to deep research format
            deep_results = []
            for result in results:
                doc_id = str(result.id)
                if doc_id in self.id_to_record:
                    original_record = self.id_to_record[doc_id]

                    # Create snippet from main text content
                    main_text = str(original_record.get(self.config.text_column, ""))
                    snippet = (
                        main_text[:300] + "..." if len(main_text) > 300 else main_text
                    )

                    deep_result = self._create_result(original_record, snippet)
                    deep_results.append(
                        {
                            "id": deep_result.id,
                            "title": deep_result.title,
                            "text": deep_result.text,
                            "url": deep_result.url,
                        }
                    )

            logger.info(
                f"Search for '{query}' returned {len(deep_results)} results in index '{self.config.name}'"
            )
            return deep_results

        except Exception as e:
            logger.error(f"Error during search in index '{self.config.name}': {str(e)}")
            raise

    def fetch(self, document_id: str) -> Dict[str, Any]:
        """Fetch full document content by ID."""
        if not document_id:
            raise ValueError("Document ID is required")

        if document_id not in self.id_to_record:
            raise ValueError(
                f"Document with ID '{document_id}' not found in index '{self.config.name}'"
            )

        try:
            record = self.id_to_record[document_id]
            deep_result = self._create_result(record)

            result: dict[str, Any] = {
                "id": deep_result.id,
                "title": deep_result.title,
                "text": deep_result.text,
                "url": deep_result.url,
            }

            if deep_result.metadata:
                result["metadata"] = deep_result.metadata

            logger.info(
                f"Fetched document: {document_id} from index '{self.config.name}'"
            )
            return result

        except Exception as e:
            logger.error(
                f"Error fetching document {document_id} from index '{self.config.name}': {str(e)}"
            )
            raise

    def create_mcp_server(self) -> FastMCP:
        """Create MCP server with search and fetch tools for this index."""
        server_name = f"{self.config.name}_server"

        instructions = f"""
        This MCP server provides search and document retrieval capabilities
        for the '{self.config.name}' index.

        Index description: {self.config.description}

        Use the search tool to find relevant documents based on keywords,
        then use the fetch tool to retrieve complete document content.
        """

        mcp = FastMCP(name=server_name, instructions=instructions.strip())

        @mcp.tool()
        async def search(query: str) -> Dict[str, List[Dict[str, Any]]]:
            """
            Search for documents using full-text search.

            This tool searches through the document index to find relevant matches.
            Returns a list of search results with basic information. Use the fetch tool to get
            complete document content.

            Args:
                query: Search query string. Natural language queries work best.

            Returns:
                Dictionary with 'results' key containing list of matching documents.
                Each result includes id, title, text snippet, and URL.
            """
            results = self.search(query, limit=10)
            return {"results": results}

        @mcp.tool()
        async def fetch(id: str) -> Dict[str, Any]:
            """
            Retrieve complete document content by ID for detailed analysis and citation.

            This tool fetches the full document content from the index. Use this after finding
            relevant documents with the search tool to get complete information for analysis
            and proper citation.

            Args:
                id: Document ID from search results

            Returns:
                Complete document with id, title, full text content, URL, and optional metadata

            Raises:
                ValueError: If the specified ID is not found
            """
            return self.fetch(id)

        return mcp


class FastAPIMountedMCP:
    """FastAPI-mounted MCP servers for OpenAI Deep Research (separate URL paths)."""

    def __init__(self, server_name: str, server_description: str, base_url: str = ""):
        self.server_name = server_name
        self.server_description = server_description
        self.base_url = base_url.rstrip("/")
        self.index_servers: Dict[str, SingleIndexMCP] = {}
        self.mcp_servers: Dict[str, FastMCP] = {}
        self.fastapi_app: Optional[FastAPI] = None

    def add_index(self, config: IndexConfig) -> None:
        """Add a new index and create its MCP server."""
        logger.info(f"Adding index '{config.name}' for FastAPI mounting...")

        # Create single-index MCP server
        index_server = SingleIndexMCP(config, self.base_url)
        self.index_servers[config.name] = index_server

        # Create FastMCP server for this index
        mcp_server = index_server.create_mcp_server()
        self.mcp_servers[config.name] = mcp_server

        logger.info(f"Successfully created MCP server for index '{config.name}'")

    def create_fastapi_app(self) -> FastAPI:
        """Create FastAPI app with mounted MCP servers."""
        if not self.mcp_servers:
            raise ValueError(
                "No indices configured. Add at least one index before creating app."
            )

        # Get the first MCP server's ASGI app to extract lifespan
        first_mcp = list(self.mcp_servers.values())[0]
        first_asgi_app = first_mcp.http_app(path="/mcp")

        # Create main FastAPI app with the lifespan from MCP
        self.fastapi_app = FastAPI(
            title=self.server_name,
            description=self.server_description,
            lifespan=first_asgi_app.lifespan,
        )

        # Mount each MCP server at its own path
        for index_name, mcp_server in self.mcp_servers.items():
            mount_path = f"/{index_name}"

            # Create ASGI app from MCP server
            mcp_asgi_app = mcp_server.http_app(path="/mcp")

            # Mount the MCP server
            self.fastapi_app.mount(mount_path, mcp_asgi_app)

            logger.info(
                f"Mounted '{index_name}' MCP server at path '{mount_path}' -> accessible at {mount_path}/mcp"
            )

        logger.info(
            f"Created FastAPI app with {len(self.mcp_servers)} mounted MCP servers"
        )
        return self.fastapi_app

    def run_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the FastAPI app with mounted MCP servers."""
        if not self.fastapi_app:
            self.create_fastapi_app()

        logger.info(
            f"Starting FastAPI server with mounted MCP servers on {host}:{port}"
        )
        logger.info("Available MCP endpoints:")

        for index_name in self.mcp_servers.keys():
            logger.info(
                f"  - {index_name}: http://{host}:{port}/{index_name}/mcp (tools: search, fetch)"
            )

        # Run with uvicorn
        uvicorn.run(self.fastapi_app, host=host, port=port)

    def print_server_info(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Print information about all mounted servers."""
        logger.info("\n" + "=" * 80)
        logger.info("FASTAPI-MOUNTED MCP SERVERS")
        logger.info("=" * 80)
        for index_name, index_server in self.index_servers.items():
            logger.info(f"Index: {index_name}")
            logger.info(f"  Description: {index_server.config.description}")
            logger.info(f"  URL: http://{host}:{port}/{index_name}/mcp")
            logger.info("  Tools: search, fetch (OpenAI compliant)")
        logger.info("=" * 80)

    def print_server_urls(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Print the URLs for OpenAI configuration."""
        logger.info("\nOpenAI Deep Research Configuration:")
        logger.info("Each index accessible at separate URL path:")

        for index_name in self.mcp_servers.keys():
            logger.info(f"\n{index_name}:")
            logger.info(f"  URL: http://{host}:{port}/{index_name}/mcp")
            logger.info("  Tools: search, fetch")


def main():
    """CLI entry point for running multiple deep research MCP servers."""
    parser = argparse.ArgumentParser(
        description="Multi Deep Research MCP servers for OpenAI compatibility (one server per index)"
    )

    # Multi-config support
    parser.add_argument(
        "--config",
        action="append",
        help="Path to YAML configuration file (can be specified multiple times for multiple indices)",
    )

    # Single index configuration (for backward compatibility)
    parser.add_argument("--name", help="Name for single index")
    parser.add_argument("--description", help="Description for single index")
    parser.add_argument("--data-file", help="Path to JSONL file for single index")
    parser.add_argument("--id-column", help="ID column name for single index")
    parser.add_argument("--text-column", help="Text column name for single index")
    parser.add_argument(
        "--searchable-columns",
        nargs="+",
        help="Searchable columns for single index",
    )
    parser.add_argument("--index-path", help="Index path for single index")

    # Server configuration
    parser.add_argument("--base-url", default="", help="Base URL for document URLs")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP servers")
    parser.add_argument(
        "--base-port",
        type=int,
        default=8000,
        help="Base port for HTTP servers (each index gets sequential ports)",
    )
    parser.add_argument(
        "--show-urls",
        action="store_true",
        help="Show server URLs for OpenAI configuration",
    )

    args = parser.parse_args()

    try:
        # Determine server name and description
        if args.config and len(args.config) == 1:
            # Single config file - use its server info
            server_name, server_description, _, _ = load_config_from_yaml(
                args.config[0]
            )
        else:
            server_name = "unified_deep_research_server"
            server_description = (
                "Unified deep research MCP server with URL prefix routing"
            )

        # Create FastAPI-mounted MCP server
        fastapi_mcp = FastAPIMountedMCP(
            server_name=server_name,
            server_description=server_description,
            base_url=args.base_url,
        )

        if args.config:
            # Load from config files
            for config_path in args.config:
                logger.info(f"Loading configuration from {config_path}...")
                _, _, index_configs, _ = load_config_from_yaml(config_path)

                for index_config in index_configs:
                    fastapi_mcp.add_index(index_config)

        elif all(
            [
                args.name,
                args.description,
                args.data_file,
                args.id_column,
                args.text_column,
                args.searchable_columns,
            ]
        ):
            # Single index from CLI arguments
            config = IndexConfig(
                name=args.name,
                description=args.description,
                data_file=args.data_file,
                id_column=args.id_column,
                text_column=args.text_column,
                searchable_columns=args.searchable_columns,
                index_path=args.index_path,
            )
            fastapi_mcp.add_index(config)

        else:
            parser.error(
                "Either provide --config file(s) or all single-index arguments "
                "(--name, --description, --data-file, --id-column, --text-column, --searchable-columns)"
            )

        if args.show_urls:
            fastapi_mcp.print_server_urls(host=args.host, port=args.base_port)
            return 0

        # Run the FastAPI server
        fastapi_mcp.run_server(host=args.host, port=args.base_port)

    except Exception as e:
        logger.error(f"Error starting multi deep research servers: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
