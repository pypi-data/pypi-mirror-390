#!/usr/bin/env python3
"""
FastAPI server for full-text search.
Provides REST API endpoints for search and document retrieval with async support.
"""

import argparse
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..index import TantivySearch
from ..mcp.mcp import (
    IndexConfig,
    load_config_from_yaml,
    load_jsonl_data,
    ensure_id_column,
    normalize_field_value,
)


# Request/Response Models
class SearchRequest(BaseModel):
    """Request model for search endpoint."""

    index: str = Field(..., description="Name of the index to search")
    queries: list[str] = Field(..., description="List of search query strings")
    limit: int = Field(5, description="Maximum number of results to return")


class FetchRequest(BaseModel):
    """Request model for fetch endpoint."""

    index: str = Field(..., description="Name of the index to fetch from")
    document_ids: list[str] = Field(..., description="List of document IDs to retrieve")


class BatchCommandSearch(BaseModel):
    """Search command for batch operations."""

    name: str = Field("search", description="Command name")
    index: str = Field(..., description="Index to search")
    queries: list[str] = Field(..., description="Search queries")
    limit: int = Field(5, description="Result limit")


class BatchCommandFetch(BaseModel):
    """Fetch command for batch operations."""

    name: str = Field("fetch", description="Command name")
    index: str = Field(..., description="Index to fetch from")
    document_ids: list[str] = Field(..., description="Document IDs to retrieve")


class BatchRequest(BaseModel):
    """Request model for batch operations."""

    commands: list[dict[str, Any]] = Field(
        ..., description="List of search/fetch commands"
    )


class SearchResult(BaseModel):
    """Single search result."""

    id: str
    score: float
    preview: str
    content: dict[str, Any]


class SearchResponse(BaseModel):
    """Response model for search endpoint."""

    index: str
    queries: list[str]
    results: list[SearchResult]
    total: int


class FetchResponse(BaseModel):
    """Response model for fetch endpoint."""

    index: str
    documents: list[dict[str, Any]]
    found_ids: list[str]
    missing_ids: list[str]


class BatchResponse(BaseModel):
    """Response model for batch operations."""

    results: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None


class SearchAPI:
    """FastAPI server for full-text search with async support."""

    def __init__(
        self,
        server_name: str,
        server_description: str,
        indices: Optional[list[IndexConfig]] = None,
        max_workers: int = 4,
    ):
        """Initialize the search API server.

        Args:
            server_name: Name of the server
            server_description: Description of the server
            indices: List of index configurations
            max_workers: Number of worker threads for search operations
        """
        self.server_name = server_name
        self.server_description = server_description
        self.indices: dict[str, dict] = {}
        self.citations = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Initialize indices if provided
        if indices:
            for index_config in indices:
                self.add_index(index_config)

        # Create FastAPI app
        self.app = self._create_app()

    def add_index(self, config: IndexConfig) -> None:
        """Add and initialize a single index."""
        print(f"Adding index '{config.name}'...")

        # Load data
        print(f"Loading data from {config.data_file}...")
        original_data = load_jsonl_data(config.data_file)
        if not original_data:
            raise ValueError(f"No data found in file {config.data_file}")

        # Ensure id column exists
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
        search_index = TantivySearch(index_path)

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

        # Add all documents to citations dict
        for record in original_data:
            doc_id = str(record.get(config.id_column, ""))
            citation_key = f"{config.name}:{doc_id}"
            citation_value = {}

            if "title" in record:
                citation_value["title"] = record["title"]
            if "url" in record:
                citation_value["url"] = record["url"]

            if citation_value:
                self.citations[citation_key] = citation_value

        print(
            f"Successfully initialized index '{config.name}' with {len(original_data)} documents"
        )

    async def _search_async(
        self, queries: list[str], index_name: str, limit: int = 5
    ) -> dict[str, Any]:
        """Async wrapper for search operation."""
        if index_name not in self.indices:
            raise HTTPException(
                status_code=404,
                detail=f"Index '{index_name}' not found. Available: {list(self.indices.keys())}",
            )

        index_data = self.indices[index_name]
        search_index = index_data["search_index"]
        config = index_data["config"]

        # Run blocking search in thread pool
        loop = asyncio.get_event_loop()

        def _search():
            # Search across all searchable columns
            all_searchable = [config.text_column] + config.searchable_columns
            search_fields = []
            for field in all_searchable:
                if field not in search_fields and field != config.id_column:
                    search_fields.append(field)

            return search_index.search(queries, search_fields, limit=limit)

        results = await loop.run_in_executor(self.executor, _search)

        # Format results
        formatted_results = []
        for result in results:
            content = result.content
            doc_id = result.id
            score = result.score

            # Get preview of main text content
            main_text = content.get(config.text_column, "")
            preview = main_text[:200] + " [...]" if len(main_text) > 200 else main_text

            formatted_results.append(
                {
                    "id": doc_id,
                    "score": score,
                    "preview": preview,
                    "content": content,
                }
            )

        return {
            "index": index_name,
            "queries": queries,
            "results": formatted_results,
            "total": len(formatted_results),
        }

    async def _fetch_async(
        self, document_ids: list[str], index_name: str
    ) -> dict[str, Any]:
        """Async wrapper for document fetch operation."""
        if index_name not in self.indices:
            raise HTTPException(
                status_code=404,
                detail=f"Index '{index_name}' not found. Available: {list(self.indices.keys())}",
            )

        index_data = self.indices[index_name]
        search_index = index_data["search_index"]

        # Run in thread pool for consistency
        loop = asyncio.get_event_loop()

        def _fetch():
            # Use TantivySearch's cached fetch method
            return search_index.fetch(document_ids)

        results, found_ids, missing_ids = await loop.run_in_executor(
            self.executor, _fetch
        )

        return {
            "index": index_name,
            "documents": results,
            "found_ids": found_ids,
            "missing_ids": missing_ids,
        }

    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title=self.server_name,
            description=self.server_description,
            version="1.0.0",
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Health check endpoint
        @app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "indices": list(self.indices.keys()),
                "server": self.server_name,
            }

        # List indices endpoint
        @app.get("/indices")
        async def list_indices():
            indices_info = []
            for name, data in self.indices.items():
                config = data["config"]
                indices_info.append(
                    {
                        "name": name,
                        "description": config.description,
                        "document_count": len(data["original_data"]),
                        "searchable_columns": config.searchable_columns,
                    }
                )
            return {"indices": indices_info}

        # Search endpoint
        @app.post("/search", response_model=SearchResponse)
        async def search(request: SearchRequest):
            try:
                result = await self._search_async(
                    request.queries, request.index, request.limit
                )
                return result
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Fetch endpoint
        @app.post("/fetch", response_model=FetchResponse)
        async def fetch(request: FetchRequest):
            try:
                result = await self._fetch_async(request.document_ids, request.index)
                return result
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Batch endpoint
        @app.post("/batch", response_model=BatchResponse)
        async def batch(request: BatchRequest):
            try:
                # Execute all commands concurrently
                tasks = []
                for command in request.commands:
                    cmd_name = command.get("name")
                    if cmd_name == "search":
                        task = self._search_async(
                            command["queries"],
                            command["index"],
                            command.get("limit", 5),
                        )
                    elif cmd_name == "fetch":
                        task = self._fetch_async(
                            command["document_ids"], command["index"]
                        )
                    else:
                        # Return error for unknown command
                        async def error_task() -> dict[str, str]:
                            return {"error": f"Unknown command: {cmd_name}"}

                        task = error_task()
                    tasks.append(task)

                # Wait for all tasks to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Convert exceptions to error dictionaries
                formatted_results = []
                for result in results:
                    if isinstance(result, Exception):
                        formatted_results.append({"error": str(result)})
                    else:
                        formatted_results.append(result)

                return {"results": formatted_results}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Citation endpoint
        @app.get("/citation/{index}/{doc_id}")
        async def get_citation(index: str, doc_id: str):
            key = f"{index}:{doc_id}"
            if key in self.citations:
                return self.citations[key]
            else:
                raise HTTPException(status_code=404, detail="Citation not found")

        return app

    async def shutdown(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)

    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the FastAPI server.

        Args:
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional uvicorn configuration
        """
        print(f"Starting search API server on {host}:{port}")
        print(f"Indices: {list(self.indices.keys())}")
        print(f"API docs: http://{host}:{port}/docs")

        uvicorn.run(self.app, host=host, port=port, **kwargs)


def main():
    """CLI entry point for running the search API server."""
    parser = argparse.ArgumentParser(description="Full-text search API server")

    # Add config file option
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file",
    )

    # Optional arguments
    parser.add_argument("--host", default="0.0.0.0", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP server")
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker threads for search operations",
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    try:
        # Load configuration from YAML file
        server_name, server_description, index_configs, server_config = (
            load_config_from_yaml(args.config)
        )

        # Create search API server
        api_server = SearchAPI(
            server_name=server_name,
            server_description=server_description,
            indices=index_configs,
            max_workers=args.workers,
        )

        # Use host/port from YAML config if specified, otherwise use CLI args
        host = server_config.get("host", args.host)
        port = server_config.get("port", args.port)

        # Start server
        api_server.run(host=host, port=port, reload=args.reload)

    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
