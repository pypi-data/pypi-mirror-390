import re
from typing import Callable

import pandas as pd

# Use Rust-powered converter (60-80x faster than markdownify)
try:
    from html_to_markdown import convert as markdownify
except ImportError:
    # Fallback to slower Python implementation
    from markdownify import markdownify

from .ingest_markdown import strip_data_uri_images


def read_and_dedup(file_path) -> pd.DataFrame:
    df = pd.read_json(
        file_path,
        lines=True,
        orient="records",
    )
    df = df.drop_duplicates(subset="url", keep="first")
    df: pd.DataFrame = df[  # type: ignore
        df["content"].apply(lambda x: isinstance(x, str) and len(x) > 0)
    ]
    df["content"] = df["content"].apply(html_to_markdown)
    df = df.drop_duplicates(subset="content", keep="first")

    return df


def remove_links(md: str) -> tuple[str, dict[str, str]]:
    """Remove link URLs from markdown, returning cleaned markdown and a mapping of link text to URLs."""
    link_mapping = {}

    def replace_link(match):
        link_text = match.group(1)
        link_url = match.group(2)
        link_mapping[link_text] = link_url
        return f"[{link_text}]()"

    # Match markdown links: [text](url)
    cleaned_md = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, md)

    return cleaned_md, link_mapping


def replace_links(md: str, link_mapping: dict[str, str]) -> str:
    """Replace empty link URLs with the original URLs from the mapping."""

    def restore_link(match):
        link_text = match.group(1)
        if link_text in link_mapping:
            return f"[{link_text}]({link_mapping[link_text]})"
        return match.group(0)  # Return original if no mapping found

    # Match markdown links with empty URLs: [text]()
    return re.sub(r"\[([^\]]+)\]\(\)", restore_link, md)


def remove_attributes(html_string: str):
    def remove_attrs(match):
        tag_name = match.group(1)
        return f"<{tag_name}>"

    pattern = r"<([^>\s]+)[^>]*>"
    return re.sub(pattern, remove_attrs, html_string)


def remove_lines(md: str, predicate: Callable[[str], bool]):
    """predicate identifies lines to REMOVE"""
    lines = md.splitlines()

    lines = [line for line in lines if not predicate(line)]

    return "\n".join(lines)


def remove_non_content_tags(html_string: str) -> str:
    """Remove HTML elements that won't contribute to markdown content using regex."""
    # Remove script tags and their contents
    html_string = re.sub(
        r"<script[^>]*>.*?</script>", "", html_string, flags=re.DOTALL | re.IGNORECASE
    )

    # Remove style tags and their contents
    html_string = re.sub(
        r"<style[^>]*>.*?</style>", "", html_string, flags=re.DOTALL | re.IGNORECASE
    )

    # Remove svg tags and their contents
    html_string = re.sub(
        r"<svg[^>]*>.*?</svg>", "", html_string, flags=re.DOTALL | re.IGNORECASE
    )

    # Remove iframe tags
    html_string = re.sub(
        r"<iframe[^>]*>.*?</iframe>", "", html_string, flags=re.DOTALL | re.IGNORECASE
    )

    # Remove noscript tags
    html_string = re.sub(
        r"<noscript[^>]*>.*?</noscript>",
        "",
        html_string,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Remove HTML comments
    html_string = re.sub(r"<!--.*?-->", "", html_string, flags=re.DOTALL)

    return html_string


def html_to_markdown(html_string: str):
    # Remove non-content elements first
    html_string = remove_non_content_tags(html_string)

    # Remove all HTML attributes to speed up markdownify
    html_string = remove_attributes(html_string)

    md = markdownify(html_string)

    # the replace stuff we don't want
    if "Back To TOC" in md:
        md = md.split("Back To TOC")[1]

    md = remove_lines(md, lambda line: line.startswith("Select Language"))
    md = remove_lines(
        md, lambda line: line.startswith("Powered by [![Google Translate]")
    )
    md = strip_data_uri_images(md)

    md = md.replace("![]()", "")

    md = md.replace("\n---\n", "\n")

    md = re.sub(r"\n{3,}", "\n\n", md)

    return md


PROMPT = (
    "Below is some Markdown/text saved from a webpage. "
    "Make your best attempt at removing any boilerplate, leaving only the text "
    "that you think is the main content area. Boilerplate includes navigation menus, "
    "copyright notices, privacy policy links, stuff like that. Everything but the main content. "
    "If there doesn't appear to be any main content or the page is empty / all boilerplace, "
    "you may return an empty string. Do not add any prelude or commentary, just return the cleaned page. "
    "IMPORTANT: Preserve all links in the format [text]() even if the parentheses are empty - the URLs "
    "have been removed to save tokens and will be restored later.\n\n"
)

# Rough estimate: 4 chars per token, leave room for response tokens
MAX_INPUT_CHARS = 30_000  # Conservative limit for input text


def chunk_text_by_lines(text: str, max_chars: int = MAX_INPUT_CHARS) -> list[str]:
    """Split text into chunks that don't exceed max_chars, never splitting in the middle of a line."""
    if len(text) <= max_chars:
        return [text]

    lines = text.splitlines(keepends=True)
    chunks = []
    current_chunk = ""

    for line in lines:
        # If adding this line would exceed the limit, start a new chunk
        if current_chunk and len(current_chunk) + len(line) > max_chars:
            chunks.append(current_chunk.rstrip())
            current_chunk = line
        else:
            current_chunk += line

    # Add the last chunk if it has content
    if current_chunk:
        chunks.append(current_chunk.rstrip())

    return chunks


def split_by_class(html: str, classes: list[str]):
    """Split HTML into markdown chunks based on elements with specified class names.

    Converts HTML to markdown while preserving class information as comments,
    then splits based on those class markers.

    Args:
        html: The HTML string to split
        classes: List of class names to split on

    Returns:
        List of markdown chunks
    """
    from bs4 import BeautifulSoup

    if not classes:
        return [html_to_markdown(html)]

    soup = BeautifulSoup(html, "html.parser")

    # Add class markers before target elements
    split_elements = soup.find_all(class_=classes)

    if not split_elements:
        return [html_to_markdown(html)]

    # Insert split markers before each target element
    for i, element in enumerate(split_elements):
        marker = soup.new_string(f"\n\n<!-- SPLIT_MARKER_CLASS_{i} -->\n")
        element.insert_before(marker)

    # Convert to markdown
    markdown = html_to_markdown(str(soup))

    # Split on the markers (handle escaped backslashes from markdownify)
    chunks = re.split(r"\n*<!--\s*SPLIT_MARKER_CLASS_\d+\s*-->\n*", markdown)

    # Also try with escaped backslashes in case markdownify escapes them
    if len(chunks) == 1:
        chunks = re.split(r"\n*<!--\s*SPLIT\\_MARKER\\_CLASS\\_\d+\s*-->\n*", markdown)

    # Remove empty chunks and clean up
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

    return chunks if chunks else [markdown]


async def remove_boilerplate(markdown: str):
    from lm_deluge import LLMClient

    markdown, mapping = remove_links(markdown)
    client = LLMClient("gpt-4.1-mini", max_new_tokens=10_000)
    res = await client.process_prompts_async([PROMPT + markdown], show_progress=False)

    return replace_links(res[0].completion, mapping)  # type: ignore


async def remove_boilerplate_batch(markdown: list[str]):
    from lm_deluge import LLMClient

    # Remove links from all documents and collect mappings
    cleaned_docs_and_mappings = [remove_links(md) for md in markdown]
    cleaned_docs, mappings = zip(*cleaned_docs_and_mappings)

    # Track which documents were chunked and how to reassemble them
    batch_requests = []
    doc_chunk_info = []  # List of (start_idx, num_chunks) for each original document

    for i, doc in enumerate(cleaned_docs):
        chunks = chunk_text_by_lines(doc)
        doc_chunk_info.append((len(batch_requests), len(chunks)))
        batch_requests.extend([(PROMPT + chunk) for chunk in chunks])

    client = LLMClient(
        "gpt-5-nano-high",
        max_requests_per_minute=1_000,
        max_tokens_per_minute=10_000_000,
        max_new_tokens=10_000,
        request_timeout=150,
    )
    res = await client.process_prompts_async(batch_requests)

    # Reassemble chunked documents
    results = []
    for i, (start_idx, num_chunks) in enumerate(doc_chunk_info):
        if num_chunks == 1:
            # Single chunk, use result directly
            cleaned_result = res[start_idx].completion  # type: ignore
        else:
            # Multiple chunks, concatenate them
            chunk_results = [res[start_idx + j].completion for j in range(num_chunks)]  # type: ignore
            cleaned_result = "\n\n".join(chunk_results)

        # Restore links using the corresponding mapping
        final_result = replace_links(cleaned_result, mappings[i])
        results.append(final_result)

    return results


async def read_html(html_string: str):
    return await remove_boilerplate(markdownify(html_string))
