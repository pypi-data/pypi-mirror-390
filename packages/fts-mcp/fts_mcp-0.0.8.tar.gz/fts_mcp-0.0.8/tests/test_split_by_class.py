#!/usr/bin/env python3

import sys

sys.path.append("src")

from full_text_search.ingest.ingest_html import split_by_class

# Test with a small sample from the Fairfield HTML
test_html = """
<div>
    <h1>Chapter 5<br />CITY OF FAIRFIELD BUILDING AND HOUSING CODE</h1>
    <p class="Article">Article I. Administration.</p>
    
    <h3 class="Cite"><a id="a5x1x1">5.1.1</a> Application.</h3>
    <p class="P1">This chapter is applicable within the city limits of the City of Fairfield.</p>
    
    <h3 class="Cite"><a id="a5x1x2">5.1.2</a> Purpose and Authority.</h3>
    <p class="P1">The purpose of this article is to adopt by reference, the 2022 edition of the California Building Standards Code.</p>
    
    <h3 class="Cite"><a id="a5x1x3">5.1.3</a> Administration Chapter Adopted.</h3>
    <p class="P1">Chapter 1, division I and division II of the California Building Code (CBC), volume 1, 2022 edition, is hereby adopted.</p>
</div>
"""

print("Testing split_by_class with class='Cite'...")
chunks = split_by_class(test_html, ["Cite"])

print(f"\nFound {len(chunks)} chunks:")
for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk[:200] + "..." if len(chunk) > 200 else chunk)

# Test with actual Fairfield file (small portion)
print("\n" + "=" * 60)
print("Testing with actual Fairfield HTML file...")

with open(
    "/Users/benjamin/Desktop/repos/full-text-search/data/Fairfield.html", "r"
) as f:
    html_content = f.read()

# Take just a portion to test
start_idx = html_content.find('class="Cite"')
if start_idx != -1:
    # Find a reasonable end point (after a few Cite classes)
    cite_count = 0
    end_idx = start_idx
    while cite_count < 3 and end_idx < len(html_content):
        if 'class="Cite"' in html_content[end_idx : end_idx + 50]:
            cite_count += 1
        end_idx += 1

    # Extend to find a good stopping point (next tag)
    while end_idx < len(html_content) and html_content[end_idx] != "<":
        end_idx += 1

    # Go back to include some context before the first Cite
    context_start = max(0, start_idx - 500)
    test_portion = html_content[context_start : end_idx + 200]

    print(f"Testing with {len(test_portion)} characters from Fairfield.html")

    chunks = split_by_class(test_portion, ["Cite"])
    print(f"Found {len(chunks)} chunks from actual file:")

    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ({len(chunk)} chars) ---")
        # Show first few lines of each chunk
        lines = chunk.split("\n")[:5]
        for line in lines:
            print(line[:100])
        if len(lines) >= 5:
            print("...")
