# ast_blocks.py
# THIS DOES NOT WORK WELL ATM. DO NOT USE.
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, cast

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString


@dataclass
class Block:  # base class
    text: str


@dataclass
class Heading(Block):
    level: int  # 1-6


@dataclass
class Paragraph(Block):
    pass


class ListKind(Enum):
    DECIMAL = auto()
    LOWER_ALPHA = auto()
    UPPER_ALPHA = auto()
    LOWER_ROMAN = auto()
    UPPER_ROMAN = auto()


@dataclass
class ListItem(Block):
    depth: int
    ordinal: int
    kind: ListKind
    parens: bool  # “u-list-…-parenthesized”


STYLE_MAP = {
    # extend if you meet new ones
    "u-list-lower-alpha": ListKind.LOWER_ALPHA,
    "u-list-upper-alpha": ListKind.UPPER_ALPHA,
    "u-list-lower-roman": ListKind.LOWER_ROMAN,
    "u-list-upper-roman": ListKind.UPPER_ROMAN,
}


def _kind_from(tag: Tag) -> tuple[ListKind, bool]:
    # Tag.get – leave default as None, then normalise
    raw = tag.get("class")  # None | str | List[str]

    # bs4 guarantees that a “class” attr, if present, is a *list* of strings
    classes: List[str] = cast(List[str], raw) if isinstance(raw, list) else []

    kind = ListKind.DECIMAL  # fallback 1,2,3…
    parens = False

    for cls in classes:
        kind = STYLE_MAP.get(cls, kind)
        parens = parens or cls.endswith("parenthesized")

    return kind, parens


def html_to_blocks(html: str) -> List[Block]:
    soup = BeautifulSoup(html, "html.parser")
    blocks: list[Block] = []

    def walk(node: Tag | NavigableString, depth=0, counter=None):
        nonlocal blocks
        if isinstance(node, NavigableString):
            return  # ignore bare strings (they get captured by parent tags)

        # Headings ----------------------------------------------------------
        if node.name and node.name.startswith("h") and node.name[1:].isdigit():
            lvl = int(node.name[1:])
            blocks.append(Heading(node.get_text(" ", strip=True), lvl))
            return

        # Ordered / unordered lists -----------------------------------------
        if node.name in {"ol", "ul"}:
            kind, parens = _kind_from(node)
            for idx, li in enumerate(node.find_all("li", recursive=False), 1):
                text = li.get_text(" ", strip=True)
                blocks.append(ListItem(text, depth, idx, kind, parens))
                walk(cast(Tag, li), depth + 1)  # handle nested lists
            return

        # Paragraph-like -----------------------------------------------------
        if node.name in {"p", "div", "section"}:
            txt = node.get_text(" ", strip=True)
            if txt:
                blocks.append(Paragraph(txt))
        # Recurse
        for child in node.children:
            walk(cast(Tag, child), depth)

    walk(soup.body or soup)  # pages without <body> still work
    return blocks


def chunk_blocks(
    blocks: List[Block],
    max_chars: int = 8_000,
    heading_barrier: int = 3,  # don’t split inside h1-h3 sections
) -> List[List[Block]]:
    chunks, cur = [], []
    cur_len, cur_depth = 0, 0  # cur_depth == 0 means ‘safe to cut’

    for blk in blocks:
        # update depth for list items
        if isinstance(blk, ListItem):
            cur_depth = max(cur_depth, blk.depth + 1)
        elif isinstance(blk, Heading):
            # Heading always resets “safe cut” depth
            cur_depth = 0

        cur.append(blk)
        cur_len += len(blk.text)

        can_cut = (
            cur_len >= max_chars
            and cur_depth == 0
            and not (isinstance(blk, Heading) and blk.level <= heading_barrier)
        )
        if can_cut:
            chunks.append(cur)
            cur, cur_len = [], 0

    if cur:
        chunks.append(cur)
    return chunks


def to_marker(n: int, kind: ListKind) -> str:
    if kind == ListKind.DECIMAL:
        return str(n)
    if kind in {ListKind.LOWER_ALPHA, ListKind.UPPER_ALPHA}:
        s = chr(ord("a") + n - 1)  # naïve, good to 26
        return s if kind.name.startswith("LOWER") else s.upper()
    if kind in {ListKind.LOWER_ROMAN, ListKind.UPPER_ROMAN}:
        # simple roman 1-3999
        nums = zip(
            (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1),
            ("m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"),
        )
        res, k = "", n
        for val, sym in nums:
            while k >= val:
                res += sym
                k -= val
        return res if kind.name.startswith("LOWER") else res.upper()
    else:
        raise ValueError("unknown list kind: " + str(kind))


def render_to_markdown(chunk: list[Block]) -> str:
    out = []
    num_stack = []  # track list numbers per depth

    for blk in chunk:
        if isinstance(blk, Heading):
            out.append("#" * blk.level + " " + blk.text)
            num_stack.clear()  # new section, reset counters

        elif isinstance(blk, Paragraph):
            out.append(blk.text)

        elif isinstance(blk, ListItem):
            depth = blk.depth
            while len(num_stack) <= depth:
                num_stack.append(0)
            num_stack[depth] += 1
            num_stack[depth + 1 :] = []  # truncate deeper levels
            bullet = ".".join(map(str, num_stack[: depth + 1])) + "."
            out.append("    " * depth + f"{bullet} {blk.text}")

    return "\n".join(out) + "\n"
