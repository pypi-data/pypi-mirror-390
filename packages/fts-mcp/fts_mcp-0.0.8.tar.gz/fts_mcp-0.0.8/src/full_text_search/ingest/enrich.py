# this file takes jsonl of texts and turns it into "enriched" jsonl with keywords and summaries and stuff
import json
import re
from pathlib import Path

import dotenv
import pandas as pd
from lm_deluge import Conversation, LLMClient
from lm_deluge.util.json import try_load_json
from lm_deluge.util.xml import get_tag
from pydantic import BaseModel


async def retitle(document_name: str, texts: list[str]):
    dotenv.load_dotenv()
    client = LLMClient(
        "gpt-5-nano-high",
        max_tokens_per_minute=10_000_000,
        max_new_tokens=10_000,
        request_timeout=75,
    )

    prompt = (
        f"Given the beginning of a {document_name}, provide a clean title for it. "
        f"The {document_name} may already have a title you can use; if so, you can just return that. "
        "If it has any important information like a bill/policy/plan number or other ID "
        "that would allow it to be referenced precisely, make sure to include that. "
        "Use title case, not all-caps. "
        f"Here is the start of the {document_name}:\n\n```\n<< SECTION >>\n```"
        "\n\nNow provide JUST your title inside <title></title> XML tags, no prelude or commentary needed."
    )

    prompts = [
        Conversation.user(prompt.replace("<< SECTION >>", text[:1000] + " [...]"))
        for text in texts
    ]

    resps = await client.process_prompts_async(prompts)
    titles = [
        get_tag(x.completion, "title") if x and x.completion else None for x in resps
    ]

    return titles


async def clean_title(document_name: str, titles: list[str]):
    dotenv.load_dotenv()
    client = LLMClient(
        "gpt-5-nano-high",
        max_tokens_per_minute=10_000_000,
        max_new_tokens=10_000,
        request_timeout=75,
    )

    prompt = (
        f"Given a messy title for a {document_name}, provide a clean title for it. "
        "If it has any important information like a bill/policy/plan number or other ID "
        "that would allow it to be referenced precisely, make sure to include that. "
        "Use title case, not all-caps. "
        f"Here is the messy title: << TITLE >>"
        "\n\nNow provide JUST your title inside <title></title> XML tags, no prelude or commentary needed."
    )

    prompts = [
        Conversation.user(prompt.replace("<< TITLE >>", title[:1000]))
        for title in titles
    ]

    resps = await client.process_prompts_async(prompts)
    titles = [  # type: ignore
        get_tag(x.completion, "title") if x and x.completion else None for x in resps
    ]

    return titles


def lax_json_parse(raw: str):
    # 1) isolate {...}
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found")
    s = raw[start : end + 1]

    # 2) normalize quotes & backticks
    s = (
        s.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("`", "")
    )

    # 3) escape newlines inside strings
    s = _escape_newlines_in_strings(s)

    # 4) drop trailing commas
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # 5) repair top-level arrays (missing commas / unterminated strings)
    # Note: only repairs outermost arrays since Python re doesn't support recursion
    s = re.sub(r"\[[^\[\]]*\]", lambda m: _repair_array(m.group(0)), s, flags=re.S)

    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return None


def _escape_newlines_in_strings(s: str) -> str:
    out, in_str, esc = [], False, False
    for ch in s:
        if esc:
            out.append(ch)
            esc = False
            continue
        if ch == "\\":
            out.append(ch)
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            out.append(ch)
            continue
        if in_str and ch in "\r\n":
            out.append("\\n")
            continue
        out.append(ch)
    return "".join(out)


def _repair_array(array_text: str) -> str:
    inner = array_text[1:-1]
    items, i, n = [], 0, len(inner)
    while i < n:
        while i < n and inner[i] in " \t\r\n,":
            i += 1
        if i >= n:
            break
        if inner[i] == '"':
            i += 1
            buf, esc, closed = [], False, False
            while i < n:
                ch = inner[i]
                i += 1
                if esc:
                    buf.append(ch)
                    esc = False
                    continue
                if ch == "\\":
                    buf.append(ch)
                    esc = True
                    continue
                if ch == '"':
                    closed = True
                    break
                if ch in "\r\n":
                    buf.append("\\n")
                    continue
                buf.append(ch)
            if not closed:
                while i < n and inner[i] not in ",]":
                    ch = inner[i]
                    i += 1
                    buf.append("\\n" if ch in "\r\n" else ch)
            s = (
                "".join(buf)
                .replace("\u201c", '"')
                .replace("\u201d", '"')
                .replace("\u2018", "'")
                .replace("\u2019", "'")
            )
            items.append('"' + s + '"')
        else:
            buf = []
            while i < n and inner[i] not in ",]":
                ch = inner[i]
                i += 1
                buf.append(" " if ch in "\r\n" else ch)
            t = "".join(buf).strip()
            if t:
                items.append(json.dumps(t))
    return "[" + ", ".join(items) + "]"


class Enrichment(BaseModel):
    keywords: list[str]
    description: str


async def filter_texts(
    document_name: str, criterion: str, texts: list[str]
) -> list[bool | None]:
    client = LLMClient(
        "gpt-4.1-mini",
        max_tokens_per_minute=20_000_000,
        max_requests_per_minute=8_000,
        max_new_tokens=10_000,
        request_timeout=90,
        # reasoning_effort="minimal",
        max_concurrent_requests=650,
    )

    prompt = (
        f"Given a section from the {document_name}, determine whether it is {criterion}. "
        "If yes, return <result>yes</result>, otherwise return <result>no</result>. "
        f"Here is the {document_name} section:\n\n```\n<< SECTION >>\n```"
        "\n\nNow provide your classification, no prelude or commentary needed."
    )
    resps = await client.process_prompts_async(
        [prompt.replace("<< SECTION >>", text) for text in texts]
    )
    labels = [
        get_tag(resp.completion, "result") if resp and resp.completion else None
        for resp in resps
    ]
    labels = [
        None if label is None else True if "yes" in label.lower() else False  # type: ignore
        for label in labels
    ]

    return labels


async def enrich_texts(document_name: str, texts: list[str]):
    dotenv.load_dotenv()
    client = LLMClient(
        "gpt-4.1-mini",
        max_tokens_per_minute=20_000_000,
        max_requests_per_minute=8_000,
        max_new_tokens=10_000,
        request_timeout=90,
        # reasoning_effort="minimal",
        max_concurrent_requests=650,
        json_mode=True,
    )

    prompt = (
        f"Given a section from the {document_name}, provide the following metadata as JSON, with "
        "`keywords` and `description` keys as follows:\n\n"
        " - `keywords` list[str]: A list of as many HIGH-QUALITY keywords/keyphrases as you can think of that someone "
        "might search for where the page/section would be relevant. The keywords/phrases do NOT have to occur exactly "
        "in the section, they can be semantic matches, synonyms, etc. ONLY include a keyword if the page/section "
        "you are given includes SUBSTANTIVE INFORMATION about that topic. If a page only has a LINK about that topic, "
        "that topic shouldn't be a keyword, since reading this page would not provide information about that topic. "
        "Keywords should be specific to the page/section, not "
        f"keywords that would apply to literally any page/section of the {document_name}.\n"
        " - `description` str: A summary/overview of what the section says, including any key requirements or rules. "
        "Be mindful of your tendency to make overlong summaries, and remember that the goal is to provide a SHORT "
        "overview of the section. A long summary is pointless because you may as well just read the original.\n\n"
        f"Here is the {document_name} section:\n\n```\n<< SECTION >>\n```"
        "\n\nNow provide your JSON response, no prelude or commentary needed."
    )

    prompts = [
        Conversation.user(prompt.replace("<< SECTION >>", text)) for text in texts
    ]

    resps = await client.process_prompts_async(prompts)
    # resps = await client.wait_for_batch_job(batch_ids, "openai")
    jsons = []
    for x in resps:
        if not x or not x.completion:
            jsons.append(None)
            continue
        # Try standard parser first
        loaded = try_load_json(x.completion)
        if loaded is not None:
            jsons.append(loaded)
        else:
            # Fall back to lax parser
            jsons.append(lax_json_parse(x.completion))

    # additional step -- validate the JSONS. if any doesn't validate
    # set it to None.
    for i, json_obj in enumerate(jsons):
        if json_obj is None:
            continue
        try:
            Enrichment.model_validate(json_obj)
        except Exception:
            jsons[i] = None

    return jsons


async def enrich_jsonl(document_name: str, in_file: Path | str, out_file: Path | str):
    df = pd.read_json(in_file, orient="records", lines=True)
    jsons = await enrich_texts(document_name, df["text"].to_list())
    normalized = pd.json_normalize(jsons)  # type: ignore

    combined = (
        pd.concat(
            [df.reset_index(drop=True), normalized.reset_index(drop=True)],
            ignore_index=True,
            axis=1,
        )
        .dropna()
        .reset_index(drop=True)
    )

    print("sample combined row:", combined.to_dict(orient="records")[0])
    combined.columns = ["text", "keywords", "summary"]
    combined["title"] = combined["text"].apply(lambda x: x.split("\n")[0])
    combined["id"] = combined.index.astype(str)
    combined = combined[["id", "title", "summary", "text", "keywords"]]
    combined["keywords"] = combined["keywords"].apply(lambda x: [k.lower() for k in x])  # type: ignore

    combined.to_json(str(out_file), orient="records", lines=True)
