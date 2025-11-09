from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from lenlp import normalizer
from rapidfuzz import fuzz, process
from tqdm.auto import tqdm


@dataclass
class SearchResult:
    id: str
    score: float
    content: dict


class SearchIndex(ABC):
    @abstractmethod
    def build_index(
        self,
        records: list[dict],
        deduplicate_strategy: Literal["exact", "fuzzy", None],
        deduplicate_by: str | None = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def search(
        self, queries: list[str], fields: list[str], limit: int = 8, escape: bool = True
    ) -> list[SearchResult]:
        raise NotImplementedError


def deduplicate_exact(records: list[dict], deduplicate_by: str) -> list[dict]:
    seen = set()
    deduplicated = []
    for record in tqdm(records):
        key = normalizer.normalize(record[deduplicate_by])
        if key not in seen:
            deduplicated.append(record)
            seen.add(key)
    print(
        f"Deduplication removed {len(records) - len(deduplicated)} of {len(records)} records."
    )
    return deduplicated


def deduplicate_fuzzy(
    records: list[dict], deduplicate_by: str, cutoff: float = 95
) -> list[dict]:
    result = []
    normalized_seen = []

    for record in records:
        key = normalizer.normalize(record[deduplicate_by])
        if normalized_seen:
            max_sim = process.extract(
                query=key,
                choices=normalized_seen,
                scorer=fuzz.ratio,
            )[0][1]
            if max_sim > cutoff:
                continue
        result.append(record)
        normalized_seen.append(key)

    print(
        f"Deduplication removed {len(records) - len(result)} of {len(records)} records."
    )
    return result
