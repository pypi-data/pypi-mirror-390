#!/usr/bin/env python3

import sys

sys.path.append("src")

from full_text_search.ingest.ingest_html import split_by_class

print("Testing split_by_class with full Fairfield.html file...")

with open(
    "/Users/benjamin/Desktop/repos/full-text-search/data/Fairfield.html", "r"
) as f:
    html_content = f.read()

print(f"Original HTML file size: {len(html_content):,} characters")

# Split by class="Cite"
chunks = split_by_class(html_content, ["Cite"])

print(f"Found {len(chunks)} chunks when splitting by class='Cite'")

# Show some stats about the chunks
chunk_sizes = [len(chunk) for chunk in chunks]
print(
    f"Chunk sizes: min={min(chunk_sizes)}, max={max(chunk_sizes)}, avg={sum(chunk_sizes)//len(chunk_sizes)}"
)

# Show first few lines of first few chunks
for i, chunk in enumerate(chunks[:5]):
    print(f"\n--- Chunk {i+1} ({len(chunk)} chars) ---")
    lines = chunk.split("\n")[:3]
    for line in lines:
        print(line[:80])
    if len(lines) >= 3:
        print("...")

if len(chunks) > 5:
    print(f"\n... and {len(chunks) - 5} more chunks")
