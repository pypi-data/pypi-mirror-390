#!/usr/bin/env python3
"""
Deep Research MCP server compatible with OpenAI's specification.
Implements search and fetch tools with proper schema for deep research integration.
"""

import argparse
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from ..index.tantivy_index import TantivySearch
from .mcp import IndexConfig, ensure_id_column, load_jsonl_data, normalize_field_value

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


class DeepResearchMCP:
    """Single-index MCP server compatible with OpenAI's deep research specification."""

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

            logger.info(f"Search for '{query}' returned {len(deep_results)} results")
            return deep_results

        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise

    def fetch(self, document_id: str) -> Dict[str, Any]:
        """Fetch full document content by ID."""
        if not document_id:
            raise ValueError("Document ID is required")

        if document_id not in self.id_to_record:
            raise ValueError(f"Document with ID '{document_id}' not found")

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

            logger.info(f"Fetched document: {document_id}")
            return result

        except Exception as e:
            logger.error(f"Error fetching document {document_id}: {str(e)}")
            raise

    def create_mcp_server(self) -> FastMCP:
        """Create MCP server with search and fetch tools."""
        server_name = f"{self.config.name}_deep_research"

        instructions = f"""
        This MCP server provides search and document retrieval capabilities
        for deep research on the '{self.config.name}' index.

        Index description: {self.config.description}

        Use the search tool to find relevant documents based on keywords,
        then use the fetch tool to retrieve complete document content with citations.
        """

        mcp = FastMCP(name=server_name, instructions=instructions.strip())

        @mcp.tool()
        async def search(query: str) -> Dict[str, List[Dict[str, Any]]]:
            """
            Search for documents using full-text search.

            This tool searches through the document index to find semantically relevant matches.
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

    def run_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the MCP server."""
        mcp = self.create_mcp_server()
        logger.info(
            f"Starting deep research MCP server for '{self.config.name}' on {host}:{port}"
        )
        logger.info(f"MCP endpoint: http://{host}:{port}/sse")
        mcp.run(transport="sse", host=host, port=port)


def load_config_from_yaml(config_path: str) -> tuple[str, str, List[IndexConfig], Dict]:
    """Load configuration from YAML file (reuse from mcp.py)."""
    from .mcp import load_config_from_yaml as _load_config

    return _load_config(config_path)


def main():
    """CLI entry point for running the deep research MCP server."""
    parser = argparse.ArgumentParser(
        description="Deep Research MCP server for OpenAI compatibility"
    )

    # Add config file option
    parser.add_argument(
        "--config",
        help="Path to YAML configuration file with single index. For multiple indices, use multi_deep_research_mcp.py",
    )

    # Required arguments for single index configuration
    parser.add_argument("--name", help="Name for the index")
    parser.add_argument(
        "--description", help="Description of what this search index contains"
    )
    parser.add_argument("--data-file", help="Path to JSONL file containing documents")
    parser.add_argument(
        "--id-column", help="Name of column containing unique document IDs"
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
    parser.add_argument("--base-url", default="", help="Base URL for document URLs")
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP server")

    args = parser.parse_args()

    try:
        if args.config:
            # Load configuration from YAML file
            server_name, server_description, index_configs, server_config = (
                load_config_from_yaml(args.config)
            )

            if len(index_configs) > 1:
                print(
                    "Error: Deep research MCP requires single index per server.",
                    file=sys.stderr,
                )
                print(
                    "Use multi_deep_research_mcp.py for multiple indices.",
                    file=sys.stderr,
                )
                return 1

            config = index_configs[0]

            # Use host/port from YAML config if specified
            host = server_config.get("host", args.host)
            port = server_config.get("port", args.port)

        else:
            # Single index from CLI arguments
            if not all(
                [
                    args.name,
                    args.description,
                    args.data_file,
                    args.id_column,
                    args.text_column,
                    args.searchable_columns,
                ]
            ):
                parser.error(
                    "When not using --config, all arguments are required except --index-path and --base-url"
                )

            config = IndexConfig(
                name=args.name,
                description=args.description,
                data_file=args.data_file,
                id_column=args.id_column,
                text_column=args.text_column,
                searchable_columns=args.searchable_columns,
                index_path=args.index_path,
            )

            host = args.host
            port = args.port

        # Create and run deep research MCP server
        server = DeepResearchMCP(config, base_url=args.base_url)
        server.run_server(host=host, port=port)

    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
