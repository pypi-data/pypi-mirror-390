#!/usr/bin/env python3
"""
Test script for YAML configuration functionality.
"""

import json
import tempfile
import yaml
from pathlib import Path
from src.full_text_search.mcp import load_config_from_yaml, FullTextSearchMCP


def create_test_data():
    """Create test JSONL data files for YAML config test."""
    # Test data for books
    books_data = [
        {
            "id": "book1",
            "title": "Python Programming",
            "content": "Learn Python programming with examples",
            "author": "John Doe",
            "category": "Programming",
        },
        {
            "id": "book2",
            "title": "Data Science",
            "content": "Analyze data using Python and R",
            "author": "Jane Smith",
            "category": "Data",
        },
        {
            "id": "book3",
            "title": "Web Development",
            "content": "Build modern web applications",
            "author": "Bob Johnson",
            "category": "Web",
        },
    ]

    # Test data for articles
    articles_data = [
        {
            "doc_id": "art1",
            "headline": "AI Revolution",
            "body": "Artificial intelligence is transforming industries",
            "category": "Technology",
            "tags": "AI, ML, tech",
        },
        {
            "doc_id": "art2",
            "headline": "Climate Change",
            "body": "Global warming effects on the environment",
            "category": "Environment",
            "tags": "climate, environment",
        },
        {
            "doc_id": "art3",
            "headline": "Space Exploration",
            "body": "Mars mission planning and execution",
            "category": "Science",
            "tags": "space, mars, science",
        },
    ]

    # Test data for docs
    docs_data = [
        {
            "doc_id": "doc1",
            "title": "API Reference",
            "content": "Complete API documentation for the service",
            "section": "Reference",
            "topic": "API",
        },
        {
            "doc_id": "doc2",
            "title": "Getting Started",
            "content": "Quick start guide for new users",
            "section": "Tutorial",
            "topic": "Setup",
        },
        {
            "doc_id": "doc3",
            "title": "Configuration",
            "content": "How to configure the application settings",
            "section": "Guide",
            "topic": "Config",
        },
    ]

    # Create temporary files
    books_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    articles_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    docs_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)

    # Write data
    for book in books_data:
        books_file.write(json.dumps(book) + "\n")
    books_file.close()

    for article in articles_data:
        articles_file.write(json.dumps(article) + "\n")
    articles_file.close()

    for doc in docs_data:
        docs_file.write(json.dumps(doc) + "\n")
    docs_file.close()

    return books_file.name, articles_file.name, docs_file.name


def create_test_yaml_config(books_file: str, articles_file: str, docs_file: str):
    """Create a test YAML configuration file."""
    config = {
        "server": {
            "name": "test_multi_server",
            "description": "Test multi-index search server",
            "host": "127.0.0.1",
            "port": 8001,
        },
        "indices": [
            {
                "name": "books",
                "description": "Programming and technical books",
                "data_file": books_file,
                "id_column": "id",
                "text_column": "content",
                "searchable_columns": ["title", "content", "author", "category"],
            },
            {
                "name": "articles",
                "description": "News articles and blog posts",
                "data_file": articles_file,
                "id_column": "doc_id",
                "text_column": "body",
                "searchable_columns": ["headline", "body", "category", "tags"],
            },
            {
                "name": "docs",
                "description": "Technical documentation",
                "data_file": docs_file,
                "id_column": "doc_id",
                "text_column": "content",
                "searchable_columns": ["title", "content", "section", "topic"],
            },
        ],
    }

    # Create temporary YAML file
    yaml_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    yaml.dump(config, yaml_file, default_flow_style=False)
    yaml_file.close()

    return yaml_file.name


def test_yaml_functionality():
    """Test YAML configuration loading and multi-index functionality."""
    print("Creating test data files...")
    books_file, articles_file, docs_file = create_test_data()

    print("Creating test YAML configuration...")
    yaml_config_file = create_test_yaml_config(books_file, articles_file, docs_file)

    try:
        # Test YAML config loading
        print("Testing YAML config loading...")
        server_name, server_description, index_configs, server_config = (
            load_config_from_yaml(yaml_config_file)
        )

        print(f"Server name: {server_name}")
        print(f"Server description: {server_description}")
        print(f"Server config: {server_config}")
        print(f"Number of indices: {len(index_configs)}")

        for config in index_configs:
            print(f"  - Index: {config.name} ({config.description})")

        # Test creating server from YAML config
        print("\nCreating server from YAML config...")
        server = FullTextSearchMCP(
            server_name=server_name,
            server_description=server_description,
            indices=index_configs,
        )

        print(f"Available indices: {list(server.indices.keys())}")

        # Test searching across different indices
        print("\n=== Testing searches across indices ===")

        # Search books
        print("\n--- Books Index ---")
        result = server.search("Python", "books", limit=2)
        print(result)

        # Search articles
        print("\n--- Articles Index ---")
        result = server.search("AI", "articles", limit=2)
        print(result)

        # Search docs
        print("\n--- Docs Index ---")
        result = server.search("API", "docs", limit=2)
        print(result)

        # Test reading documents
        print("\n=== Testing document reading ===")
        result = server.read_documents(["book1"], "books")
        print(result[:200] + "..." if len(result) > 200 else result)

        # Test MCP server creation (just verify it doesn't crash)
        print("\n=== Testing MCP server creation ===")
        mcp_server = server.create_mcp_server()
        print(f"MCP server created successfully with server name: {mcp_server.name}")

        print("\n✅ YAML configuration test completed successfully!")

    finally:
        # Clean up temporary files
        Path(books_file).unlink()
        Path(articles_file).unlink()
        Path(docs_file).unlink()
        Path(yaml_config_file).unlink()


if __name__ == "__main__":
    test_yaml_functionality()
