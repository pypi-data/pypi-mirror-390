#!/usr/bin/env python3
"""Test script for include_fields and exclude_fields functionality."""

import tempfile
from pathlib import Path

from src.full_text_search.index import TantivySearch


def test_include_fields():
    """Test that only included fields are searchable."""
    print("\n=== Testing include_fields ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"

        # Create index with only 'title' as searchable
        search_index = TantivySearch(str(index_path), include_fields=["title"])

        # Build index with multiple fields
        records = [
            {
                "id": "1",
                "title": "Python Programming",
                "content": "Learn Python basics",
                "metadata": "some metadata",
            },
            {
                "id": "2",
                "title": "Java Guide",
                "content": "Learn Java programming",
                "metadata": "more metadata",
            },
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Should work: searching on 'title'
        try:
            results = search_index.search(["Python"], ["title"], limit=5)
            print(f"✓ Searching 'title' field succeeded: {len(results)} results")
            assert len(results) > 0
        except Exception as e:
            print(f"✗ Searching 'title' field failed: {e}")
            return False

        # Should fail: searching on 'content' (not in include_fields)
        try:
            results = search_index.search(["basics"], ["content"], limit=5)
            print("✗ Searching 'content' field should have failed but didn't")
            return False
        except ValueError as e:
            print(f"✓ Searching 'content' field correctly raised error: {e}")

        # Should fail: searching on 'metadata' (not in include_fields)
        try:
            results = search_index.search(["metadata"], ["metadata"], limit=5)
            print("✗ Searching 'metadata' field should have failed but didn't")
            return False
        except ValueError as e:
            print(f"✓ Searching 'metadata' field correctly raised error: {e}")

    return True


def test_exclude_fields():
    """Test that excluded fields are not searchable."""
    print("\n=== Testing exclude_fields ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"

        # Create index with 'metadata' excluded
        search_index = TantivySearch(str(index_path), exclude_fields=["metadata"])

        # Build index with multiple fields
        records = [
            {
                "id": "1",
                "title": "Python Programming",
                "content": "Learn Python basics",
                "metadata": "some metadata",
            },
            {
                "id": "2",
                "title": "Java Guide",
                "content": "Learn Java programming",
                "metadata": "more metadata",
            },
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Should work: searching on 'title'
        try:
            results = search_index.search(["Python"], ["title"], limit=5)
            print(f"✓ Searching 'title' field succeeded: {len(results)} results")
        except Exception as e:
            print(f"✗ Searching 'title' field failed: {e}")
            return False

        # Should work: searching on 'content'
        try:
            results = search_index.search(["basics"], ["content"], limit=5)
            print(f"✓ Searching 'content' field succeeded: {len(results)} results")
        except Exception as e:
            print(f"✗ Searching 'content' field failed: {e}")
            return False

        # Should fail: searching on 'metadata' (excluded)
        try:
            results = search_index.search(["metadata"], ["metadata"], limit=5)
            print("✗ Searching 'metadata' field should have failed but didn't")
            return False
        except ValueError as e:
            print(f"✓ Searching 'metadata' field correctly raised error: {e}")

    return True


def test_include_and_exclude():
    """Test that include_fields - exclude_fields works correctly."""
    print("\n=== Testing include_fields + exclude_fields ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"

        # Include title, content, author but exclude author
        # Result: only title and content searchable
        search_index = TantivySearch(
            str(index_path),
            include_fields=["title", "content", "author"],
            exclude_fields=["author"],
        )

        records = [
            {
                "id": "1",
                "title": "Python Book",
                "content": "About Python",
                "author": "John Doe",
                "metadata": "misc",
            },
            {
                "id": "2",
                "title": "Java Book",
                "content": "About Java",
                "author": "Jane Doe",
                "metadata": "misc",
            },
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Should work: title and content
        try:
            results = search_index.search(["Python"], ["title", "content"], limit=5)
            print(
                f"✓ Searching 'title' and 'content' succeeded: {len(results)} results"
            )
        except Exception as e:
            print(f"✗ Searching 'title' and 'content' failed: {e}")
            return False

        # Should fail: author (excluded)
        try:
            results = search_index.search(["John"], ["author"], limit=5)
            print("✗ Searching 'author' field should have failed but didn't")
            return False
        except ValueError as e:
            print(f"✓ Searching 'author' field correctly raised error: {e}")

        # Should fail: metadata (not in include_fields)
        try:
            results = search_index.search(["misc"], ["metadata"], limit=5)
            print("✗ Searching 'metadata' field should have failed but didn't")
            return False
        except ValueError as e:
            print(f"✓ Searching 'metadata' field correctly raised error: {e}")

    return True


def test_no_restrictions():
    """Test that with no include/exclude, all fields are searchable (default behavior)."""
    print("\n=== Testing no restrictions (default behavior) ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        index_path = Path(tmpdir) / "test_index"

        # Create index with no restrictions
        search_index = TantivySearch(str(index_path))

        records = [
            {
                "id": "1",
                "title": "Python Book",
                "content": "About Python",
                "metadata": "misc",
            },
        ]

        search_index.build_index(records, deduplicate_strategy=None)

        # Should work: all fields
        for field in ["title", "content", "metadata"]:
            try:
                results = search_index.search(["test"], [field], limit=5)

                print(
                    f"✓ Searching '{field}' succeeded (no restrictions),",
                    len(results),
                    "results",
                )
            except Exception as e:
                print(f"✗ Searching '{field}' failed: {e}")
                return False

    return True


if __name__ == "__main__":
    print("Running field filtering tests...")

    all_passed = True
    all_passed &= test_include_fields()
    all_passed &= test_exclude_fields()
    all_passed &= test_include_and_exclude()
    all_passed &= test_no_restrictions()

    if all_passed:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
        exit(1)
