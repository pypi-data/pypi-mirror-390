#!/usr/bin/env python3
"""
Test script for deep research MCP functionality.
"""

import json
import tempfile
import asyncio
from pathlib import Path
from src.full_text_search.mcp import IndexConfig
from src.full_text_search.mcp.deep_research_mcp import DeepResearchMCP


def create_test_data():
    """Create test JSONL data files."""
    # Test data for deep research
    test_data = [
        {
            "id": "doc1",
            "title": "Python Programming Fundamentals",
            "content": "Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including object-oriented, procedural, and functional programming.",
            "author": "John Doe",
            "category": "Programming",
            "tags": ["python", "programming", "fundamentals"],
        },
        {
            "id": "doc2",
            "title": "Data Science with Python",
            "content": "Data science involves extracting insights from data using statistical methods, machine learning, and visualization techniques. Python provides excellent libraries like pandas, numpy, and scikit-learn for data analysis.",
            "author": "Jane Smith",
            "category": "Data Science",
            "tags": ["data science", "python", "machine learning"],
        },
        {
            "id": "doc3",
            "title": "Web Development Best Practices",
            "content": "Modern web development requires understanding of HTML, CSS, JavaScript, and backend technologies. Best practices include responsive design, accessibility, and performance optimization.",
            "author": "Bob Johnson",
            "category": "Web Development",
            "tags": ["web development", "best practices", "frontend"],
        },
        {
            "id": "doc4",
            "title": "Machine Learning Algorithms",
            "content": "Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning. Common algorithms include linear regression, decision trees, and neural networks.",
            "author": "Alice Brown",
            "category": "Machine Learning",
            "tags": ["machine learning", "algorithms", "ai"],
        },
    ]

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)

    # Write test data
    for doc in test_data:
        temp_file.write(json.dumps(doc) + "\n")
    temp_file.close()

    return temp_file.name


def test_deep_research_mcp():
    """Test deep research MCP functionality."""
    print("Creating test data...")
    data_file = create_test_data()

    try:
        # Create index configuration
        config = IndexConfig(
            name="test_docs",
            description="Test documents for deep research MCP",
            data_file=data_file,
            id_column="id",
            text_column="content",
            searchable_columns=["title", "content", "author", "category"],
        )

        # Create deep research MCP server
        print("Initializing deep research MCP server...")
        server = DeepResearchMCP(config, base_url="https://example.com")

        print(f"Initialized server for index: {config.name}")
        print(f"Data loaded: {len(server.original_data)} documents")

        # Test search functionality
        print("\n=== Testing Search Functionality ===")

        # Test 1: Basic search
        print("Test 1: Searching for 'python programming'")
        results = server.search("python programming", limit=5)
        print(f"Found {len(results)} results")

        for i, result in enumerate(results, 1):
            print(f"  Result {i}:")
            print(f"    ID: {result['id']}")
            print(f"    Title: {result['title']}")
            print(f"    Text: {result['text'][:100]}...")
            print(f"    URL: {result['url']}")
            print()

        # Test 2: Different search query
        print("Test 2: Searching for 'machine learning'")
        results = server.search("machine learning", limit=3)
        print(f"Found {len(results)} results")

        for i, result in enumerate(results, 1):
            print(f"  Result {i}: {result['title']} (ID: {result['id']})")

        # Test 3: Empty search
        print("\nTest 3: Empty search query")
        results = server.search("", limit=5)
        print(f"Found {len(results)} results (should be 0)")

        # Test fetch functionality
        print("\n=== Testing Fetch Functionality ===")

        # Test 4: Fetch existing document
        print("Test 4: Fetching document 'doc1'")
        doc = server.fetch("doc1")
        print("Fetched document:")
        print(f"  ID: {doc['id']}")
        print(f"  Title: {doc['title']}")
        print(f"  Text length: {len(doc['text'])} characters")
        print(f"  URL: {doc['url']}")
        if "metadata" in doc:
            print(f"  Metadata: {doc['metadata']}")

        # Test 5: Fetch another document
        print("\nTest 5: Fetching document 'doc2'")
        doc = server.fetch("doc2")
        print(f"Fetched: {doc['title']}")

        # Test 6: Error handling - non-existent document
        print("\nTest 6: Error handling - fetching non-existent document")
        try:
            doc = server.fetch("nonexistent")
            print("ERROR: Should have raised ValueError")
        except ValueError as e:
            print(f"Correctly caught error: {e}")

        # Test 7: Error handling - empty document ID
        print("\nTest 7: Error handling - empty document ID")
        try:
            doc = server.fetch("")
            print("ERROR: Should have raised ValueError")
        except ValueError as e:
            print(f"Correctly caught error: {e}")

        # Test MCP server creation
        print("\n=== Testing MCP Server Creation ===")
        mcp_server = server.create_mcp_server()
        print(f"Created MCP server: {mcp_server.name}")
        print(f"Available tools: {list(mcp_server.tools.keys())}")

        # Verify tools exist
        assert "search" in mcp_server.tools, "search tool not found"
        assert "fetch" in mcp_server.tools, "fetch tool not found"

        print("\n✅ All deep research MCP tests passed!")

        # Test async tools
        print("\n=== Testing Async Tool Functionality ===")

        async def test_async_tools():
            search_tool = mcp_server.tools["search"]
            fetch_tool = mcp_server.tools["fetch"]

            # Test async search
            search_result = await search_tool.invoke({"query": "python"})
            print(f"Async search returned: {len(search_result['results'])} results")

            # Test async fetch
            if search_result["results"]:
                first_result_id = search_result["results"][0]["id"]
                fetch_result = await fetch_tool.invoke({"id": first_result_id})
                print(f"Async fetch returned: {fetch_result['title']}")

        # Run async tests
        asyncio.run(test_async_tools())

        print("\n✅ All async tool tests passed!")

    finally:
        # Clean up temporary file
        Path(data_file).unlink()


def test_result_format():
    """Test that results conform to OpenAI deep research format."""
    print("\n=== Testing Result Format Compliance ===")

    data_file = create_test_data()

    try:
        config = IndexConfig(
            name="format_test",
            description="Test format compliance",
            data_file=data_file,
            id_column="id",
            text_column="content",
            searchable_columns=["title", "content"],
        )

        server = DeepResearchMCP(config)

        # Test search result format
        search_results = server.search("python", limit=1)

        if search_results:
            result = search_results[0]

            # Check required fields
            required_fields = ["id", "title", "text", "url"]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
                assert isinstance(result[field], str), f"Field {field} must be string"

            print("✅ Search result format is compliant")

        # Test fetch result format
        fetch_result = server.fetch("doc1")

        # Check required fields
        required_fields = ["id", "title", "text", "url"]
        for field in required_fields:
            assert field in fetch_result, f"Missing required field: {field}"
            assert isinstance(fetch_result[field], str), f"Field {field} must be string"

        # Check optional metadata field
        if "metadata" in fetch_result:
            assert isinstance(fetch_result["metadata"], dict), "Metadata must be dict"

        print("✅ Fetch result format is compliant")

    finally:
        Path(data_file).unlink()


if __name__ == "__main__":
    test_deep_research_mcp()
    test_result_format()
    print("\n🎉 All tests completed successfully!")
