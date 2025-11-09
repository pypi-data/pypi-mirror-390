import json
from urllib.parse import parse_qs, urlsplit


def get_url_params(url: str) -> dict:
    # In case the URL came in with escaped slashes like "https:\/\/..."
    url = url.replace(r"\/", "/")
    qs = urlsplit(url).query
    # keep_blank_values=True preserves empty params like title=&article=
    parsed = parse_qs(qs, keep_blank_values=True)
    # Flatten single-item lists (leave lists when a key appears multiple times)
    return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}


def coalesce_small_chunks(chunks: list[str], min_size: int = 125) -> list[str]:
    """
    Merge any chunk shorter than *min_size* into the *following* chunk.
    (If it’s the last chunk, it’s left as-is.)
    """
    if not chunks:
        return []

    merged: list[str] = []
    i = 0
    while i < len(chunks):
        # Start with current chunk
        accumulated = chunks[i]
        j = i + 1

        # Keep merging following chunks while current is too small and there are more chunks
        while len(accumulated) < min_size and j < len(chunks):
            accumulated = accumulated.rstrip() + "\n\n" + chunks[j].lstrip()
            j += 1

        merged.append(accumulated)
        i = j  # Move to next unprocessed chunk

    return merged


def save_texts_to_jsonl(chunks: list[str], out_path: str):
    with open(out_path, "w") as f:
        for chunk in chunks:
            f.write(json.dumps({"text": chunk}) + "\n")
