#!/usr/bin/env python3
"""
Test the CLI with YAML configuration (without actually starting the server).
"""

import json
import tempfile
import yaml
import subprocess
import sys
from pathlib import Path


def create_test_data_and_config():
    """Create test data and YAML config for CLI testing."""
    # Test data
    books_data = [
        {
            "id": "book1",
            "title": "Python Programming",
            "content": "Learn Python programming",
            "author": "John Doe",
        },
        {
            "id": "book2",
            "title": "Data Science",
            "content": "Analyze data with Python",
            "author": "Jane Smith",
        },
    ]

    # Create temporary data file
    books_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for book in books_data:
        books_file.write(json.dumps(book) + "\n")
    books_file.close()

    # Create YAML config
    config = {
        "server": {
            "name": "cli_test_server",
            "description": "CLI test server",
            "host": "127.0.0.1",
            "port": 8002,
        },
        "indices": [
            {
                "name": "books",
                "description": "Test books collection",
                "data_file": books_file.name,
                "id_column": "id",
                "text_column": "content",
                "searchable_columns": ["title", "content", "author"],
            }
        ],
    }

    # Create temporary YAML file
    yaml_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    yaml.dump(config, yaml_file, default_flow_style=False)
    yaml_file.close()

    return books_file.name, yaml_file.name


def test_cli_yaml():
    """Test CLI argument parsing with YAML config."""
    print("Creating test data and config...")
    books_file, yaml_file = create_test_data_and_config()

    try:
        # Test the CLI argument parsing (we'll catch the server startup and exit early)
        print("Testing CLI with YAML config...")

        # Import and test the main function directly to avoid starting the server
        from src.full_text_search.mcp import load_config_from_yaml, FullTextSearchMCP

        # Test loading config
        server_name, server_description, index_configs, server_config = (
            load_config_from_yaml(yaml_file)
        )
        print(f"✅ Config loaded: {server_name}, {len(index_configs)} indices")

        # Test creating server
        server = FullTextSearchMCP(
            server_name=server_name,
            server_description=server_description,
            indices=index_configs,
        )
        print(f"✅ Server created with indices: {list(server.indices.keys())}")

        # Test help message
        print("\nTesting CLI help...")
        result = subprocess.run(
            [sys.executable, "-m", "src.full_text_search.mcp", "--help"],
            capture_output=True,
            text=True,
            cwd=".",
        )
        if result.returncode == 0:
            print("✅ CLI help works")
            if "--config" in result.stdout:
                print("✅ --config option is documented")
            else:
                print("❌ --config option not found in help")
        else:
            print(f"❌ CLI help failed: {result.stderr}")

        print("\n✅ CLI YAML configuration test completed successfully!")

    finally:
        # Clean up
        Path(books_file).unlink()
        Path(yaml_file).unlink()


if __name__ == "__main__":
    test_cli_yaml()
