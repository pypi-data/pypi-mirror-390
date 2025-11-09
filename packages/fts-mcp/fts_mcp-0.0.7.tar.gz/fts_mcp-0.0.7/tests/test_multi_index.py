#!/usr/bin/env python3
"""
Test script for multi-index functionality.
"""

import asyncio
import json
import tempfile
from pathlib import Path
from full_text_search.mcp.mcp import FullTextSearchMCP, IndexConfig


def create_test_data():
    """Create test JSONL data files."""
    # Test data for first index (books)
    books_data = [
        {
            "id": "book1",
            "title": "Python Programming",
            "content": "Learn Python programming with examples",
            "author": "John Doe",
        },
        {
            "id": "book2",
            "title": "Data Science",
            "content": "Analyze data using Python and R",
            "author": "Jane Smith",
        },
        {
            "id": "book3",
            "title": "Web Development",
            "content": "Build modern web applications",
            "author": "Bob Johnson",
        },
    ]

    # Test data for second index (articles)
    articles_data = [
        {
            "doc_id": "art1",
            "headline": "AI Revolution",
            "body": "Artificial intelligence is transforming industries",
            "category": "Technology",
        },
        {
            "doc_id": "art2",
            "headline": "Climate Change",
            "body": "Global warming effects on the environment",
            "category": "Environment",
        },
        {
            "doc_id": "art3",
            "headline": "Space Exploration",
            "body": "Mars mission planning and execution",
            "category": "Science",
        },
    ]

    # Create temporary files
    books_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    articles_file = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)

    # Write books data
    for book in books_data:
        books_file.write(json.dumps(book) + "\n")
    books_file.close()

    # Write articles data
    for article in articles_data:
        articles_file.write(json.dumps(article) + "\n")
    articles_file.close()

    return books_file.name, articles_file.name


async def test_multi_index():
    """Test multi-index functionality."""
    print("Creating test data...")
    books_file, articles_file = create_test_data()

    try:
        # Create index configurations
        books_config = IndexConfig(
            name="books",
            description="Collection of programming and technical books",
            data_file=books_file,
            id_column="id",
            text_column="content",
            searchable_columns=["title", "content", "author"],
        )

        articles_config = IndexConfig(
            name="articles",
            description="News articles and blog posts",
            data_file=articles_file,
            id_column="doc_id",
            text_column="body",
            searchable_columns=["headline", "body", "category"],
        )

        # Create multi-index search server
        print("Initializing multi-index search server...")
        server = FullTextSearchMCP(
            server_name="test_server",
            server_description="Test server with multiple indices",
            indices=[books_config, articles_config],
        )

        print(f"Available indices: {list(server.indices.keys())}")

        # Test searching in books index
        print("\n=== Testing Books Index ===")
        result = await server.search(["Python"], "books", limit=2)
        print(result)

        # Test searching in articles index
        print("\n=== Testing Articles Index ===")
        result = await server.search(["AI"], "articles", limit=2)
        print(result)

        # Test reading documents from books index
        print("\n=== Testing Read Documents from Books ===")
        result = await server.read_documents(["book1", "book2"], "books")
        print(result)

        # Test reading documents from articles index
        print("\n=== Testing Read Documents from Articles ===")
        result = await server.read_documents(["art1"], "articles")
        print(result)

        # Test error handling - non-existent index
        print("\n=== Testing Error Handling ===")
        result = await server.search(["test"], "nonexistent")
        print(result)

        print("\n✅ Multi-index functionality test completed successfully!")

    finally:
        # Clean up temporary files
        Path(books_file).unlink()
        Path(articles_file).unlink()


if __name__ == "__main__":
    asyncio.run(test_multi_index())
