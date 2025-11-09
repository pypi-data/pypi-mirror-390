#!/usr/bin/env python3
"""Debug the syntax error."""

import tempfile
from pathlib import Path
from src.full_text_search.index import TantivySearch


def test_parts():
    """Test parts of the problematic query."""
    print("=== Testing parts of query ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"
        search_index = TantivySearch(str(index_path))

        records = [
            {
                "id": "1",
                "content": "What minimum letter height is required for posting the pool's emergency telephone number 911",
            },
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Test progressively longer parts
        test_queries = [
            "What minimum",
            "What minimum letter height",
            "pool's emergency",
            "telephone number 911",
            "What minimum letter height is required",
            "What minimum letter height is required for posting",
            "What minimum letter height is required for posting the pool's",
            "What minimum letter height is required for posting the pool's emergency",
            "What minimum letter height is required for posting the pool's emergency telephone",
            "What minimum letter height is required for posting the pool's emergency telephone number",
            "What minimum letter height is required for posting the pool's emergency telephone number 911",
        ]

        for i, query in enumerate(test_queries, 1):
            try:
                results = search_index.search(
                    [query], ["content"], limit=5, escape=True
                )
                print(
                    f"{i}. ✓ Query succeeded ({len(query)} chars): {len(results)} results"
                )
            except Exception as e:
                print(f"{i}. ✗ Query failed ({len(query)} chars): {e}")
                print(f"   Query: {query}")
                break


if __name__ == "__main__":
    test_parts()
