#!/usr/bin/env python3
"""
Utilities for turning Markdown (e.g. PDF-to-Markdown output) into JSONL chunks for RAG.

Core steps
----------
1. Optionally strip Markdown image links.
2. Split on every header line (`#`, `##`, …) so each header starts a new chunk.
3. Merge “tiny” chunks (default < 500 chars) into the *following* chunk.
4. Write one JSONL object per chunk under the key `"text"`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List, Literal, Pattern, Tuple

import pandas as pd

from .common import coalesce_small_chunks

# ---------- regexes ---------------------------------------------------------

_IMG = re.compile(r"!\[[^\]]*]\([^)]*\)")  # ![alt](url)
_HDR = re.compile(r"^\s*#{1,6}\s")  # lines starting with 1-6 “# ”
# contiguous table block (lines beginning with "|")
_TABLE_RE = re.compile(r"(?:^[ \t]*\|[^\n]*\n?)+", re.MULTILINE)
_MD_LINK_RE: Pattern[str] = re.compile(
    r"\[((?:[^\[\]]|\[[^\]]*\])*)\]\(((?:[^()]|\([^)]*\))*)\)",  # ① link text   ② URL
    re.IGNORECASE,
)
_SECTION_START_RE = re.compile(
    r"^\s*#{1,6}\s*"
    r"(?:"
    r"(?:Chapter|Section|Division|Article|Part|Appendix)\b"
    r"|\d+(?:\.\d+)+"
    r"|§"
    r"|\([A-Za-z0-9]+\)"
    r"|\[[A-Za-z0-9]+\]"
    r"|[A-Za-z0-9]+\)"
    r")"
    r".*$",
    re.IGNORECASE | re.MULTILINE,
)
_NUM_ALPHA_LIST_RE = re.compile(r"^(?:\d+|[A-Za-z]|[IVXLCDM]+)[.)]\s+", re.MULTILINE)
_BULLET = re.compile(
    r"^([ \t]*)(?:[-+*]|\d+[.)]|[A-Za-z][.)]|[IVXLCDM]+\.[ \t]|\([A-Za-z]+\))[ \t]+"
)
_DIVIDER_RE = re.compile(r"^\s*([-=])\1{4,}\s*$")
_TAG_PAIR_RE = re.compile(
    r"<(?P<tag>[A-Za-z][^\s/>]*)[^>]*?>.*?</(?P=tag)\s*>",
    re.DOTALL | re.IGNORECASE,
)
_TAG_SINGLE_RE = re.compile(r"<[^>]+?>", re.IGNORECASE)
_DATA_URI_RE = re.compile(
    r"""
    (                   # whole match
        !?\[            # opening `[` (with optional leading `!` for images)
        [^\]]*          #   – anything except `]` (alt-text or link text)
        \]              # closing `]`
        \(              # opening `(`
        \s*data:image   # URL that starts with `data:image`
        [^)]*           #   – the rest of the data-URI
        \)              # closing `)`
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def strip_data_uri_images(md: str) -> str:
    """Remove inline images or links whose URL starts with 'data:image'.

    Parameters
    ----------
    md : str
        The original Markdown string.

    Returns
    -------
    str
        Markdown with offending images/links excised.
    """
    return _DATA_URI_RE.sub("", md)


# ---------- basic transforms -----------------------------------------------


def strip_html_and_contents(text: str) -> str:
    """
    Strip all HTML tags *and everything inside them*.
    Re-runs the paired-tag pattern until no more matches remain,
    so nested elements are removed safely.
    """
    while True:
        new_text, n = _TAG_PAIR_RE.subn("", text)
        if n == 0:  # no more paired tags found
            break
        text = new_text  # iterate to catch inner nests

    # clean up any single/self-closing tags that remain
    return _TAG_SINGLE_RE.sub("", text)


def strip_prelude(md: str, pattern: str, padding_lines: int = 0) -> str:
    """
    Remove all lines from the beginning until one matches 'pattern'.
    Add back 'padding_lines' removed.
    """
    lines = md.splitlines()
    start = -1
    for idx, line in enumerate(lines):
        if pattern in line:
            start = idx
            break

    start -= padding_lines

    return "\n".join(lines[start:])


def strip_postlude(md: str, pattern: str, padding_lines: int = 0):
    lines = md.splitlines()
    end = 0
    for idx, line in reversed(list(enumerate(lines))):
        if pattern in line:
            end = idx
            break

    end += padding_lines

    return "\n".join(lines[:end])


def split_on_dividers(markdown: str) -> List[str]:
    """
    Split *markdown* into chunks separated by divider lines.

    A divider is a line consisting solely of '=' or '-' repeated ≥ 5 times,
    optionally surrounded by whitespace.  Divider lines themselves are not
    included in the output.

    Returns a list of chunk strings in their original order.
    """
    chunks: List[str] = []
    current: List[str] = []

    for line in markdown.splitlines():
        if _DIVIDER_RE.match(line):
            if current:  # finish the current chunk
                chunks.append("\n".join(current).rstrip())
                current = []
        else:
            current.append(line)

    if current:  # trailing chunk, if any
        chunks.append("\n".join(current).rstrip())

    return chunks


def link_percentage(chunk: str) -> float:
    """
    Return the percentage of characters in *chunk* that belong to Markdown
    inline links of the form [text](url).

    The calculation uses the total character length of all matched links
    divided by the total length of the chunk.  Whitespace and all other
    characters are included in the denominator.  An empty chunk yields 0.0.
    """
    if not chunk:
        return 0.0

    link_chars = sum(len(m.group(0)) for m in _MD_LINK_RE.finditer(chunk))
    return link_chars / len(chunk)


def remove_image_links(md: str) -> str:
    """Strip every Markdown image link."""
    return _IMG.sub("", md)


def is_section_heading(line: str) -> bool:
    """Return True if *line* marks the start of a numbered/labelled section."""
    return bool(_SECTION_START_RE.match(line))


def strip_links_with_substring(text: str, substring: str) -> str:
    """
    Remove any *inline* Markdown links whose target URL contains ``url_substring``.

    The link’s visible text is left in place, but the surrounding brackets and the
    URL (and its parentheses) are discarded.
    """

    def _replacer(m: re.Match[str]) -> str:
        return m.group(1) if substring in m.group(2) else m.group(0)

    return _MD_LINK_RE.sub(_replacer, text)


def remove_lines_with_substring(text: str, substring: str) -> str:
    return "\n".join(line for line in text.splitlines() if substring not in line)


def fix_newlines(text: str) -> str:
    # remove any number of newlines >2 and replace with 2 newlines
    pattern = re.compile(r"\n{3,}")
    return pattern.sub("\n\n", text)


def remove_large_tables(text: str, max_cells: int = 400) -> str:
    """
    Strip Markdown tables whose total number of cells exceeds *max_cells*.

    Parameters
    ----------
    text : str
        The Markdown / plain-text document.
    max_cells : int, optional
        Maximum cell count to keep.  Tables with more cells are removed.
        Default is 400.

    Returns
    -------
    str
        The cleaned document.
    """

    def _table_replacer(m: re.Match[str]) -> str:
        block = m.group(0)
        # Count cells: for each row, the number of '|' minus 1
        cells = sum(row.count("|") - 1 for row in block.rstrip("\n").splitlines())
        return "" if cells > max_cells else block

    return _TABLE_RE.sub(_table_replacer, text)


def extract_first_link_text(text: str) -> str:
    """Return the text inside the first Markdown link in *text*, or '' if none."""
    m = _MD_LINK_RE.search(text)
    return m.group(1) if m else ""


def _find_bullets(lines: List[str]) -> List[Tuple[int, int]]:
    """Return (line_number, indent_width) for every list-item line."""
    out: list[Tuple[int, int]] = []
    for i, ln in enumerate(lines):
        m = _BULLET.match(ln)
        if m:
            indent = len(m.group(1).expandtabs(4))
            out.append((i, indent))
    return out


def _split_on_indent(
    lines: List[str], bullets: List[Tuple[int, int]], max_chars: int
) -> List[str]:
    """
    Recursively cut on bullet lines.  'bullets' holds (line, indent) pairs
    for *this* slice only (not for the whole doc).
    """
    if not bullets:
        return ["\n".join(lines).rstrip()]

    min_indent = min(ind for _, ind in bullets)
    starts = [ln for ln, ind in bullets if ind == min_indent]

    chunks = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(lines)
        block = lines[s:e]
        text = "\n".join(block).rstrip()

        if len(text) > max_chars:
            # bullets strictly *inside* this slice
            sub_bullets = [
                (ln - s, ind) for ln, ind in bullets if s < ln < e and ind > min_indent
            ]
            if sub_bullets:
                chunks.extend(_split_on_indent(block, sub_bullets, max_chars))
                continue
        chunks.append(text)
    return chunks


def split_lists_indent(md: str, max_chars: int = 8_000) -> List[str]:
    """
    Split Markdown by list items using ONLY indentation.
    Result: every chunk ≤ max_chars unless there is no deeper level left.
    """
    lines = md.splitlines()
    bullets = _find_bullets(lines)
    return _split_on_indent(lines, bullets, max_chars)


SplitHeuristic = Literal[
    "headings", "sections", "lists", "links", "bold", "italic", "brute"
]


def split_into_chunks(
    md: str,
    how: SplitHeuristic = "sections",
) -> List[str]:
    """
    Split so that *each* Markdown header begins a new chunk.
    The header line itself stays with the chunk it starts.
    """
    if how == "lists":
        return split_lists_indent(md)

    lines = md.splitlines()
    out: List[str] = []
    cur: List[str] = []
    cur_length = 0
    MAX_LEN = 5_000  # only for brute

    for line in lines:
        if how == "sections" and is_section_heading(line) and cur:
            out.append("\n".join(cur).strip())
            cur = [line]
            cur_length = len(line)
        elif how == "headings" and _HDR.match(line) and cur:
            out.append("\n".join(cur).strip())
            cur = [line]
            cur_length = len(line)
        elif how == "links" and _MD_LINK_RE.match(line) and cur:
            out.append("\n".join(cur).strip())
            cur = [line]
            cur_length = len(line)
        elif how == "bold" and line.strip().startswith("**"):
            out.append("\n".join(cur).strip())
            cur = [line]
            cur_length = len(line)
        elif how == "italic" and line.strip().startswith("*"):
            out.append("\n".join(cur).strip())
            cur = [line]
            cur_length = len(line)
        elif how == "brute" and cur_length > MAX_LEN:
            out.append("\n".join(cur).strip())
            cur = [line]
            cur_length = len(line)
        else:
            cur.append(line)
            cur_length += len(line)

    if cur:
        out.append("\n".join(cur).strip())

    return [c for c in out if c]  # drop empties


def _make_title(old: str | None, new: str | None):
    if not old and not new:
        return "[UNTITLED SECTION]"
    elif old and not new:
        return old
    elif new and not old:
        return new
    return f"{old} - {new}"


def title_from_first_heading(old: str | None, chunk: str) -> str:
    first = chunk.splitlines()[0].lstrip("# ").strip()
    return _make_title(old, first)


def title_from_first_bold(old: str | None, chunk: str) -> str:
    try:
        first = chunk.split("**")[1]
        return _make_title(old, first.strip())
    except IndexError:
        return title_from_first_sentence(old, chunk)


def title_from_first_italic(old: str | None, chunk: str) -> str:
    try:
        first = chunk.split("*")[1]
        return _make_title(old, first.strip())
    except IndexError:
        return title_from_first_sentence(old, chunk)


def title_from_first_sentence(old: str | None, chunk: str) -> str:
    first = chunk.strip().splitlines()[0].split(". ")[0].strip()
    return _make_title(old, first)


def title_from_first_line(old: str | None, chunk: str) -> str:
    line = chunk.strip().splitlines()[0].strip("# ")
    if len(line) < 100 and len(line) > 10:
        return _make_title(old, line)
    else:
        return title_from_first_sentence(old, chunk)


def title_from_first_link(old: str | None, chunk: str) -> str:
    """
    If the chunk contains a Markdown link, append its link-text
    (the part inside the square brackets) to the title.
    """
    m = _MD_LINK_RE.search(chunk)
    if m:
        text = m.group(1).strip()
        return _make_title(old, text)
    return _make_title(old, None)


# ---------- cascading split ----------------------------------------

HOW_TO_TITLE_FN = {
    "headings": title_from_first_heading,
    "sections": title_from_first_line,
    "lists": title_from_first_line,
    "links": title_from_first_link,
    "bold": title_from_first_bold,
    "italic": title_from_first_italic,
    "brute": title_from_first_sentence,
}


def cascading_split(
    df: pd.DataFrame,
    how: list[SplitHeuristic],
    max_length: int = 8_000,
    coalesce_min: int = 225,
):
    assert "content" in df.columns and "title" in df.columns, "df missing title/content"
    working = df.copy()
    for step in how:
        # do the splitting
        working["content"] = working["content"].apply(
            lambda x: [x]
            if len(x) <= max_length
            else coalesce_small_chunks(
                split_into_chunks(x, how=step),  # type: ignore
                coalesce_min,
            )
        )
        working["num_subsections"] = working["content"].apply(len)
        working = working.explode("content", ignore_index=True)

        # update titles if a rule was provided and we actually split
        title_fn = HOW_TO_TITLE_FN[step]
        working["title"] = working.apply(
            lambda row: row["title"]
            if row["num_subsections"] == 1
            else title_fn(row["title"], row["content"]),
            axis=1,
        )

    working["content_length"] = working["content"].apply(len)
    return working


# ---------- pipeline & file helpers ----------------------------------------


def process(md: str, *, remove_images: bool = True, min_size: int = 500) -> List[str]:
    """Run the full pipeline and return the final chunks."""
    if remove_images:
        md = remove_image_links(md)
    chunks = split_into_chunks(md)
    return coalesce_small_chunks(chunks, min_size=min_size)


def markdown_to_jsonl(
    src: Path,
    dst: Path,
    *,
    remove_images: bool = True,
    min_size: int = 500,
) -> None:
    """Convert *src* Markdown file to JSONL at *dst*."""
    chunks = process(
        src.read_text(encoding="utf-8"), remove_images=remove_images, min_size=min_size
    )
    with dst.open("w", encoding="utf-8") as fh:
        for c in chunks:
            json.dump({"text": c}, fh, ensure_ascii=False)
            fh.write("\n")


# ---------- CLI ------------------------------------------------------------


def _cli() -> None:
    ap = argparse.ArgumentParser(description="Ingest Markdown and output JSONL chunks.")
    ap.add_argument("input_md", type=Path, help="Source Markdown file")
    ap.add_argument("output_jsonl", type=Path, help="Destination JSONL file")
    ap.add_argument(
        "--keep-images", action="store_true", help="Do NOT strip image links"
    )
    ap.add_argument(
        "--min-size", type=int, default=500, help="Minimum chunk size in characters"
    )
    args = ap.parse_args()

    markdown_to_jsonl(
        args.input_md,
        args.output_jsonl,
        remove_images=not args.keep_images,
        min_size=args.min_size,
    )


if __name__ == "__main__":
    _cli()
