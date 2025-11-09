#!/usr/bin/env python3
"""
Test script for ID auto-generation functionality.
"""

import json
import tempfile
from pathlib import Path

from src.full_text_search.mcp import FullTextSearchMCP, IndexConfig


def test_id_autogen():
    """Test that ID column is auto-generated when missing."""
    # Create test data WITHOUT id column
    test_data = [
        {"text": "First document content", "title": "Doc 1"},
        {"text": "Second document content", "title": "Doc 2"},
        {"text": "Third document content", "title": "Doc 3"},
    ]

    # Create temporary JSONL file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for item in test_data:
        temp_file.write(json.dumps(item) + "\n")
    temp_file.close()

    try:
        print("Testing ID auto-generation...")

        # Test with IndexConfig using default 'id' column
        config = IndexConfig(
            name="test_index",
            description="Test index without ID column",
            data_file=temp_file.name,
            id_column="id",  # This column doesn't exist in the data
            text_column="text",
            searchable_columns=["text", "title"],
        )

        # Create server and add index
        server = FullTextSearchMCP(
            server_name="test_server",
            server_description="Test server for ID auto-generation",
        )

        # This should auto-generate ID column
        server.add_index(config)

        print(
            f"✅ Index created successfully with {len(server.indices['test_index']['original_data'])} documents"
        )

        # Verify IDs were added
        original_data = server.indices["test_index"]["original_data"]
        for i, record in enumerate(original_data):
            expected_id = str(i)
            actual_id = record.get("id")
            if actual_id != expected_id:
                print(f"❌ ID mismatch: expected '{expected_id}', got '{actual_id}'")
                return
            else:
                print(f"✅ Record {i}: ID = '{actual_id}'")

        # Test search functionality
        print("\nTesting search with auto-generated IDs...")
        result = server.search("First", "test_index", limit=1)
        if "ID: 0" in result:
            print("✅ Search works with auto-generated IDs")
        else:
            print("❌ Search failed with auto-generated IDs")
            print(result)

        # Test legacy initialize method with defaults
        # print("\nTesting legacy initialize method...")
        # server2 = FullTextSearchMCP("test_server2", "Test server 2")
        # server2.initialize(data_file=temp_file.name)  # Using all defaults

        # if "default" in server2.indices:
        #     print("✅ Legacy initialize works with defaults")
        #     data = server2.indices["default"]["original_data"]
        #     print(f"✅ Auto-generated IDs: {[record['id'] for record in data]}")
        # else:
        #     print("❌ Legacy initialize failed")

        print("\n✅ ID auto-generation test completed successfully!")

    finally:
        # Clean up
        Path(temp_file.name).unlink()


if __name__ == "__main__":
    test_id_autogen()
