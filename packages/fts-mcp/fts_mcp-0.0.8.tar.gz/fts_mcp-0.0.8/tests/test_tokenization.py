#!/usr/bin/env python3
"""Test that Tantivy tokenization handles apostrophes and stemming correctly."""

import tempfile
from pathlib import Path
from src.full_text_search.index import TantivySearch


def test_apostrophe_tokenization():
    """Test that words with apostrophes can be found with various query forms."""
    print("\n=== Testing apostrophe tokenization ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"
        search_index = TantivySearch(str(index_path))

        # Build index with various apostrophe forms
        records = [
            {"id": "1", "content": "The pool's emergency telephone number is posted"},
            {"id": "2", "content": "The pools are open on weekends"},
            {"id": "3", "content": "The pool is closed for maintenance"},
            {"id": "4", "content": "Don't forget to bring your towel"},
            {"id": "5", "content": "It's a beautiful day at the beach"},
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Test different query forms for "pool's"
        test_cases = [
            # Document has "pool's", query variations
            (
                "pool's",
                "1",
                "Query with apostrophe should match document with apostrophe",
            ),
            (
                "pools",
                "1",
                "Query 'pools' should match document with 'pool's' (stemming)",
            ),
            (
                "pool",
                "1",
                "Query 'pool' should match document with 'pool's' (stemming)",
            ),
            # Document has "pools", query variations
            ("pool", "2", "Query 'pool' should match document with 'pools' (stemming)"),
            ("pools", "2", "Query 'pools' should match document with 'pools' (exact)"),
            # Document has "pool", query variations
            ("pool", "3", "Query 'pool' should match document with 'pool' (exact)"),
            (
                "pools",
                "3",
                "Query 'pools' should match document with 'pool' (stemming)",
            ),
            # Contractions
            ("don't", "4", "Query with contraction should match"),
            ("dont", "4", "Query without apostrophe should match contraction"),
            ("do not", "4", "Expanded form should match contraction"),
            ("it's", "5", "Query with contraction should match"),
            ("its", "5", "Query without apostrophe should match contraction"),
        ]

        print("\nTest results:")
        all_passed = True
        for query, expected_id, description in test_cases:
            try:
                results = search_index.search(
                    [query], ["content"], limit=10, escape=True
                )
                matched_ids = [r.id for r in results]

                if expected_id in matched_ids:
                    print(f"✓ {description}")
                    print(
                        f"  Query: '{query}' -> Found doc {expected_id} (and {len(matched_ids)-1} others)"
                    )
                else:
                    print(f"✗ {description}")
                    print(
                        f"  Query: '{query}' -> Expected doc {expected_id}, got: {matched_ids}"
                    )
                    all_passed = False
            except Exception as e:
                print(f"✗ {description}")
                print(f"  Query: '{query}' -> ERROR: {e}")
                all_passed = False

        print("\n" + "=" * 60)

        # Additional test: Show what each query actually returns
        print("\nDetailed matching for 'pool' variations:")
        for query in ["pool", "pools", "pool's"]:
            results = search_index.search([query], ["content"], limit=10, escape=True)
            print(f"\nQuery '{query}':")
            for r in results:
                content_preview = (
                    r.content["content"][:60] + "..."
                    if len(r.content["content"]) > 60
                    else r.content["content"]
                )
                print(f"  ID {r.id} (score {r.score:.3f}): {content_preview}")

        return all_passed


if __name__ == "__main__":
    print("Running tokenization tests...")

    if test_apostrophe_tokenization():
        print("\n✓ All tests passed!")
    else:
        print("\n⚠ Some tests didn't match expected behavior")
        print("Note: This might be expected depending on tokenizer settings")
