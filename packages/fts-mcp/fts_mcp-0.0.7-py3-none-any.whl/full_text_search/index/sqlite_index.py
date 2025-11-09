import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Literal

from ..common import SearchIndex, SearchResult, deduplicate_exact, deduplicate_fuzzy


class SQLiteIndex(SearchIndex):
    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.schema = None
        self.index = None

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.index_path)
        conn.row_factory = lambda c, r: {
            c[0]: r[idx] for idx, c in enumerate(c.description)
        }
        try:
            yield conn
        finally:
            conn.close()

    @staticmethod
    def _rank_fusion(results: list[dict], limit: int) -> list[SearchResult]:
        doc_scores = {}
        for result in results:
            rowid = result["rowid"]
            rank_score = result.pop("rank")  # Remove rank from content but use it
            if rowid not in doc_scores:
                doc_scores[rowid] = 0
            doc_scores[rowid] += 1 / (60 + rank_score)

        unique_results = {}
        for rowid in sorted(
            list(doc_scores.keys()), key=lambda x: doc_scores[x], reverse=True
        )[:limit]:
            for r in results:
                if r["rowid"] == rowid and rowid not in unique_results:
                    unique_results[rowid] = SearchResult(
                        id=rowid, score=doc_scores[rowid], content=r
                    )
                    break

        return list(unique_results.values())

    def build_index(
        self,
        records: list,
        deduplicate_strategy: Literal["exact", "fuzzy", None] = "fuzzy",
        deduplicate_by: str | None = None,
    ):
        # Deduplicate if needed
        if deduplicate_strategy == "exact":
            assert (
                deduplicate_by is not None
            ), "Deduplication by must be specified for exact deduplication"
            records = deduplicate_exact(records, deduplicate_by)
        elif deduplicate_strategy == "fuzzy":
            assert (
                deduplicate_by is not None
            ), "Deduplication by must be specified for fuzzy deduplication"
            records = deduplicate_fuzzy(records, deduplicate_by)

        if not records:
            raise RuntimeError("No records to insert")

        with self._get_conn() as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")

            keys = list(records[0].keys())
            keys_quoted = [f'"{k}"' for k in keys]

            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS records USING fts5(
                    {", ".join(keys_quoted)}
                )
            """)

            conn.executemany(
                f"INSERT INTO records ({','.join(keys_quoted)}) VALUES ({','.join(['?'] * len(keys))})",
                ([row[k] for k in keys] for row in records),
            )

    def search(
        self, queries: list[str], fields: list[str], limit: int = 8
    ) -> list[SearchResult]:
        with self._get_conn() as conn:
            results = []
            match_clause = " OR ".join(f"{field} MATCH ?" for field in fields)

            for query in queries:
                cursor = conn.execute(
                    f"SELECT rowid, *, rank FROM records WHERE {match_clause} ORDER BY rank LIMIT ?",
                    [query] * len(fields) + [limit],
                )
                results.extend(cursor.fetchall())

            return self._rank_fusion(results, limit)
