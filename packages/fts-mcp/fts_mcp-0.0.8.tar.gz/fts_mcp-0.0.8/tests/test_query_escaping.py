#!/usr/bin/env python3
"""Test script for query escaping functionality."""

import tempfile
from pathlib import Path
from src.full_text_search.index import TantivySearch


def test_query_escaping():
    """Test that queries with special characters are properly escaped."""
    print("\n=== Testing query escaping ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"
        search_index = TantivySearch(str(index_path))

        # Build index
        records = [
            {"id": "1", "content": "What is a 3:4 ratio in mathematics?"},
            {"id": "2", "content": "The score was 5:2 in the game"},
            {"id": "3", "content": "Use formula (a+b)*c for calculation"},
            {"id": "4", "content": "The range is [0, 100] inclusive"},
            {
                "id": "5",
                "content": "What minimum letter height is required for posting the pool's emergency telephone number 911 and the facility's name and street address on-site?",
            },
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Test queries with special characters that would normally break
        test_queries = [
            "3:4 ratio",  # Contains :
            "(a+b)*c",  # Contains parentheses and operators
            "[0, 100]",  # Contains brackets
            "5:2",  # Contains :
            'What minimum letter height is required for posting the pool\'s emergency telephone number "911"',  # Quotes and apostrophe
            "on-site",  # Dash in word
        ]

        print("\nTesting with escape=True (default):")
        for query in test_queries:
            try:
                results = search_index.search(
                    [query], ["content"], limit=5, escape=True
                )
                print(f"✓ Query '{query}' succeeded: {len(results)} results")
            except Exception as e:
                print(f"✗ Query '{query}' failed: {e}")
                return False

        print("\nTesting with escape=False (should fail on some):")
        try:
            # This should fail because "3" is not a valid field name
            results = search_index.search(
                ["3:4 ratio"], ["content"], limit=5, escape=False
            )
            print("✗ Query '3:4 ratio' with escape=False should have failed")
            return False
        except Exception as e:
            print(f"✓ Query '3:4 ratio' with escape=False correctly failed: {e}")

    return True


if __name__ == "__main__":
    print("Running query escaping tests...")

    if test_query_escaping():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
        exit(1)
