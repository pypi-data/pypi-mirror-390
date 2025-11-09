import re
import secrets
from pathlib import Path

from pypdf import PdfReader, PdfWriter

OCR_SYSTEM_PROMPT = """
Convert the document to markdown.
Return only the markdown with no explanation text. Do not include delimiters like ```markdown or ```html.

RULES:
  - You must include all information on the page. Do not exclude headers, footers, charts, infographics, or subtext.
  - Return tables in an HTML format.
  - Logos should be wrapped in brackets. Ex: <logo>Coca-Cola<logo>
  - Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY<watermark>
  - Page numbers should be wrapped in brackets. Ex: <page_number>14<page_number> or <page_number>9/22<page_number>
  - Prefer using ☐ and ☑ for check boxes.
  - Merge lines where appropriate, i.e. only insert newlines for the start of a new paragraph, not each time a new line starts.
""".strip()

SECTION_RE = re.compile(
    r"""^\s*(                 # optional leading space
        §\s*\d                # “§ 7-5-100” style
      | (Article|CHAPTER)\b   # “Article 1”, “CHAPTER 7-5”, …
      | [A-Z][A-Z0-9 ,\-]{4,} # long all-caps headings (“BUILDING CODE”)
    )""",
    re.VERBOSE,
)

ENUM_RE = re.compile(r"^\s*(\(?[a-zA-Z0-9]+\)|\d+\.)\s+")  # (a)  ,  1.  ,  (1) …

TERMINAL_PUNCT = (".", "!", "?", ":", ";")  # characters that usually end a logical line


def is_header(line: str) -> bool:
    """True if the line looks like a section/article/header that must stay separate."""
    return bool(SECTION_RE.match(line.strip()))


def is_enum_item(line: str) -> bool:
    """True if the line starts a numbered/lettered list item."""
    return bool(ENUM_RE.match(line.strip()))


def should_join(current: str, nxt: str) -> bool:
    """
    Decide whether `nxt` is a continuation of `current`.
    The rule errs on the side of NOT joining (low false-positive rate).
    """
    if not current.strip() or not nxt.strip():
        return False  # blank lines never join

    if current.rstrip().endswith(TERMINAL_PUNCT):
        return False  # sentence already complete

    if is_header(current) or is_header(nxt):
        return False  # keep headers separate

    if is_enum_item(nxt):
        return False  # list item starts a new logical line

    # If the next line starts with a letter or punctuation,
    # we consider it a continuation.
    if bool(re.match(r"^[\s,.;:)\]]*[A-Za-z]", nxt)):
        return True

    # continuation that starts with a digit *and* you just left the reader hanging with a comma
    if current.rstrip().endswith(",") and nxt.strip()[0].isdigit():
        return True

    return False


def repair_line_breaks(text: str) -> str:
    """
    Merge OCR-introduced hard line breaks while preserving:
    * section/article headings
    * numbered / lettered list items
    * any line already ending with clear terminal punctuation

    The algorithm is intentionally conservative: some extra breaks may remain,
    but erroneous merging (false positives) is minimized.
    """
    lines: list[str] = text.splitlines()
    if not lines:
        return text

    cleaned: list[str] = []
    buf = lines[0]

    for nxt in lines[1:]:
        if should_join(buf, nxt):
            buf += " " + nxt.lstrip()
        else:
            cleaned.append(buf)
            buf = nxt
    cleaned.append(buf)

    return "\n".join(cleaned)


def remove_no_alpha(text: str):
    kept = []
    lines = text.splitlines()
    for line in lines:
        # not blank but no alpha chars -- remove
        if line.strip() and not bool(re.search(r"[A-Za-z]", line)):
            continue
        kept.append(line)

    return "\n".join(kept)


def chunk_pdf(pdf_path: str, max_pages_per_chunk: int) -> list[str]:
    """
    Split a PDF into multiple smaller PDFs.

    Args
    ----
    pdf_path: str | Path
        Path to the source PDF.
    max_pages_per_chunk: int
        Maximum pages to include in each chunk.

    Returns
    -------
    List[Path]
        Absolute paths of the chunk files, stored in a
        temporary directory that lives for the life of the
        Python process (caller is responsible for cleanup).
    """
    base_path = pdf_path.removesuffix(".pdf")
    src_path = Path(pdf_path).expanduser().resolve()
    if max_pages_per_chunk < 1:
        raise ValueError("max_pages_per_chunk must be >= 1")

    reader = PdfReader(str(src_path))
    num_pages = len(reader.pages)

    # Make a temp dir that *won’t* auto-delete on exit; caller can remove it.
    chunk_paths: list[str] = []

    for chunk_idx, start in enumerate(range(0, num_pages, max_pages_per_chunk), 1):
        writer = PdfWriter()
        end = min(start + max_pages_per_chunk, num_pages)

        for page_num in range(start, end):
            writer.add_page(reader.pages[page_num])

        # Preserve basic metadata (optional)
        if reader.metadata:
            writer.add_metadata(reader.metadata)

        chunk_file = base_path + f"_chunk_{chunk_idx}.pdf"
        with open(chunk_file, "wb") as fh:
            writer.write(fh)

        chunk_paths.append(chunk_file)

    return chunk_paths


async def ocr_chunks(chunk_paths: list[str]) -> list[str | None]:
    from lm_deluge import Conversation, File, LLMClient, Message
    from lm_deluge.prompt import Text

    prompts = []
    for cp in chunk_paths:
        prompts.append(
            Conversation.system(
                "Your task is to convert PDF pages to text while preserving all relevant information."
            ).add(Message("user", parts=[File(cp), Text(OCR_SYSTEM_PROMPT)]))
        )

    client = LLMClient(
        "gemini-2.0-flash-gemini",
        max_tokens_per_minute=1_000_000,
        max_new_tokens=10_000,
    )

    resps = await client.process_prompts_async(prompts)

    return [r.completion if r else None for r in resps]  # type: ignore


async def ocr_pdf(
    pdf: str | bytes,  # if str, path, if bytes, bytes
    max_pages_per_chunk: int = 1,
    remove_patterns: list[str] | None = None,
) -> str:
    if remove_patterns is None:
        remove_patterns = []

    if isinstance(pdf, bytes):
        tmp_path = secrets.token_urlsafe(20) + ".pdf"
        with open(tmp_path, "wb") as f:
            f.write(pdf)
        pdf = tmp_path

    chunk_paths = chunk_pdf(pdf, max_pages_per_chunk)

    as_markdown = await ocr_chunks(chunk_paths)

    text = "\n".join([x for x in as_markdown if isinstance(x, str)])

    if remove_patterns:
        pat = re.compile("|".join(re.escape(p) for p in remove_patterns))
        text = "\n".join(line for line in text.splitlines() if not pat.search(line))

    text = repair_line_breaks(text)

    text = remove_no_alpha(text)

    return text
