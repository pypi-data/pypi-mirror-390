#!/usr/bin/env python3
"""Simple test to debug escaping."""

import tempfile
from pathlib import Path
from src.full_text_search.index import TantivySearch
from src.full_text_search.index.tantivy_index import escape_query


def test_escape_function():
    """Test what the escape function actually produces."""
    test_cases = [
        "3:4 ratio",
        'emergency telephone number "911"',
        "What minimum letter height is required",
        "on-site",
    ]

    print("=== Escape function output ===")
    for query in test_cases:
        escaped = escape_query(query)
        print(f"Input:  {query}")
        print(f"Output: {escaped}")
        print()


def test_simple_query():
    """Test with simple documents."""
    print("\n=== Simple query test ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"
        search_index = TantivySearch(str(index_path))

        records = [
            {"id": "1", "content": "The emergency telephone number is 911"},
            {"id": "2", "content": "What is the minimum height required"},
            {"id": "3", "content": "The ratio is 3:4 for this calculation"},
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Test individual words first
        test_queries = [
            ("emergency", True),
            ("911", True),
            ("3:4", True),
            ("minimum height", True),
            ('emergency "911"', True),
        ]

        for query, should_escape in test_queries:
            try:
                results = search_index.search(
                    [query], ["content"], limit=5, escape=should_escape
                )
                print(
                    f"✓ Query '{query}' (escape={should_escape}): {len(results)} results"
                )
                if results:
                    print(f"  Matched IDs: {[r.id for r in results]}")
            except Exception as e:
                print(f"✗ Query '{query}' (escape={should_escape}): {e}")


if __name__ == "__main__":
    test_escape_function()
    test_simple_query()
