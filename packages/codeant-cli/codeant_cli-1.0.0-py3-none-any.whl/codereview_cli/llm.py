# codereview_cli/llm.py
import os, re, json, asyncio, time
from pathlib import Path
from typing import List, Dict, Iterable, Generator, Callable, Optional

import tiktoken
from openai import OpenAI

from codereview_cli.prompts import SYSTEM_PROMPT as _IGNORE  # keep import for consistency

# ──────────────────────────────────────────────────────────────────────────────
# System prompt: your structured, JSON-only reviewer
REVIEW_SYSTEM = """You are a senior software engineer performing an in-depth code review.

Return STRICT JSON ONLY (no prose, no markdown), exactly:
{
  "summary": "brief paragraph summarizing the overall code quality, architecture, and potential risks",
  "findings": [
    {
      "file": "relative/path",
      "severity": "HIGH|MEDIUM|LOW|NIT",
      "title": "short and descriptive issue title",
      "details": "clear explanation of what the issue is, why it matters, and how it impacts correctness, performance, security, or maintainability",
      "lines": [start, end]
    }
  ],
  "suggestions": [
    "specific technical or design improvement — e.g. refactoring recommendation, applying a design pattern, using a more appropriate data structure, optimizing an algorithm, improving exception handling, or simplifying logic"
  ]
}

Guidelines for analysis:
- Focus on correctness, security, performance, scalability, readability, and maintainability.
- Identify code smells, anti-patterns, unhandled edge cases, race conditions, or hard-coded configurations.
- For suggestions:
  - Propose concrete refactoring ideas (e.g., extract method, dependency inversion, modularization).
  - Recommend design patterns when relevant (e.g., Strategy, Factory, Observer, Singleton, Command).
  - Suggest modern language features or standard library utilities that improve clarity or safety.
  - Recommend testability improvements (unit tests, mocking strategies).
  - Propose better error handling or logging practices.
  - Mention opportunities for code simplification or reducing cognitive complexity.
- Limit to the **top 10 most impactful findings per chunk**.
- Each detail or suggestion should be concise (<150 words) but technically actionable.
"""

def build_user_prompt(chunk: str) -> str:
    return (
        "Files are delimited by headers like:\n"
        "### File: relative/path\n\n"
        "Review ONLY the code in this message.\n\n" + chunk
    )

# ──────────────────────────────────────────────────────────────────────────────
# Chunking (token-aware) for in-memory payload: [{"path","content"}]
FILE_HEADER = "### File: {rel}\n"

def _chunk_stream_from_payload(
    payload_files: List[Dict],
    encode: Callable[[str], List[int]],
    max_tokens_per_chunk: int,
    prompt_overhead: int,
) -> Generator[str, None, None]:
    """Yield token-capped chunks with file headers, splitting long lines if needed."""
    budget = max_tokens_per_chunk - prompt_overhead
    if budget <= 0:
        raise ValueError("max_tokens_per_chunk must be > prompt_overhead")

    parts: List[str] = []
    tok_count = 0

    def flush():
        nonlocal parts, tok_count
        if parts:
            yield "".join(parts)
            parts, tok_count = [], 0

    for f in payload_files:
        rel = Path(f["path"]).as_posix()
        content = f.get("content", "")
        header = FILE_HEADER.format(rel=rel)
        ht = len(encode(header))
        if tok_count + ht + prompt_overhead > max_tokens_per_chunk:
            yield from flush()
        parts.append(header); tok_count += ht

        # line-wise processing with long-line splitting
        for line in content.splitlines(keepends=True):
            lt = len(encode(line))
            if lt > budget:
                i, step = 0, max(256, len(line)//8 or 256)
                while i < len(line):
                    piece = line[i:i+step]
                    while len(encode(piece)) > budget and len(piece) > 32:
                        piece = piece[: len(piece)//2]
                    pt = len(encode(piece))
                    if tok_count + pt + prompt_overhead > max_tokens_per_chunk:
                        yield from flush()
                        cont = f"(…continued {Path(rel).name} …)\n"
                        parts.append(cont); tok_count += len(encode(cont))
                    parts.append(piece); tok_count += pt
                    i += len(piece)
                continue

            if tok_count + lt + prompt_overhead > max_tokens_per_chunk:
                yield from flush()
                cont = f"(…continued {Path(rel).name} …)\n"
                parts.append(cont); tok_count += len(encode(cont))

            parts.append(line); tok_count += lt

        sep = "\n"
        if tok_count + len(encode(sep)) + prompt_overhead > max_tokens_per_chunk:
            yield from flush()
        parts.append(sep); tok_count += len(encode(sep))

    yield from flush()

# ──────────────────────────────────────────────────────────────────────────────
# OpenAI calls + concurrent execution

def _call_openai(client: OpenAI, model: str, system: str, user_prompt: str) -> str:
    """JSON-object enforced; returns raw string content."""
    resp = client.chat.completions.create(
        model=model,
        temperature=0.0,
        max_tokens=1500,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content or ""

async def _review_worker(idx: int, chunk: str, client: OpenAI, model: str, outputs: Dict[int, str], debug: bool):
    prompt = build_user_prompt(chunk)
    txt = await asyncio.to_thread(_call_openai, client, model, REVIEW_SYSTEM, prompt)
    outputs[idx] = txt
    if debug:
        Path(f".codereview_debug_chunk_{idx}.json").write_text(txt, encoding="utf-8")

def _review_chunks_concurrently(
    chunk_iter: Iterable[str], *, client: OpenAI, model: str, concurrency: int, debug: bool
) -> List[str]:
    outputs: Dict[int, str] = {}

    async def runner():
        sem = asyncio.Semaphore(concurrency)
        tasks = []
        for i, ch in enumerate(chunk_iter, start=1):
            async def run_one(ii=i, cch=ch):
                async with sem:
                    await _review_worker(ii, cch, client, model, outputs, debug)
            tasks.append(asyncio.create_task(run_one()))
        await asyncio.gather(*tasks)
        # return in original order
        return [outputs[i] for i in range(1, len(outputs) + 1)]

    return asyncio.run(runner())

# ──────────────────────────────────────────────────────────────────────────────
# Aggregation + normalization

FILE_HEADER_RE = re.compile(r"^###\s*File:\s*(.+)$", re.MULTILINE)

def _try_parse_json(s: str) -> Optional[dict]:
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r"\{[\s\S]*\}$", s)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
        return None

def _aggregate(outputs: List[str], chunks: List[str]) -> Dict:
    agg = {"summary_notes": [], "suggestions": [], "findings_by_file": {}, "unparsed": []}
    for i, (out, ch) in enumerate(zip(outputs, chunks), start=1):
        data = _try_parse_json(out)
        if not data:
            agg["unparsed"].append({"chunk_index": i})
            continue
        if isinstance(data.get("summary"), str):
            agg["summary_notes"].append(data["summary"])
        if isinstance(data.get("suggestions"), list):
            agg["suggestions"].extend(map(str, data["suggestions"]))

        files_in_chunk = FILE_HEADER_RE.findall(ch)
        for f in data.get("findings", []):
            fp = (f.get("file") or "").strip() or (files_in_chunk[0] if files_in_chunk else "UNKNOWN")
            entry = {
                "severity": str(f.get("severity", "LOW")).upper(),
                "title": str(f.get("title", "Issue")),
                "details": str(f.get("details", "")),
                "lines": f.get("lines"),
            }
            agg["findings_by_file"].setdefault(fp, []).append(entry)

    # de-dup per file (title, details)
    for fp, lst in list(agg["findings_by_file"].items()):
        seen = {}
        for it in lst:
            key = (it["title"].strip(), it["details"].strip())
            if key not in seen:
                seen[key] = it
        agg["findings_by_file"][fp] = list(seen.values())
    return agg

# ──────────────────────────────────────────────────────────────────────────────
# Public entry: used by review.run_review()

def analyze_files_with_llm(
    files: List[Dict],
    model: str,
    *,
    max_tokens_per_chunk: int = 60000,
    prompt_overhead: int = 1200,
    concurrency: int = 4,
    debug: bool = False,
) -> List[Dict]:
    """
    files: [{"path": str, "content": str}]
    returns normalized findings for report.py:
      [{"file","line","severity","issue","suggestion"}]
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Please set OPENAI_API_KEY in your environment.")

    # tokenizer
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    encode = enc.encode

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Create chunk iterator directly from in-memory payload
    chunk_iter = _chunk_stream_from_payload(files, encode, max_tokens_per_chunk, prompt_overhead)

    # Run model concurrently over chunks
    outputs = _review_chunks_concurrently(
        chunk_iter, client=client, model=model, concurrency=concurrency, debug=debug
    )

    # For aggregation we need the exact chunks again (cheap to regenerate)
    chunks_for_agg = list(_chunk_stream_from_payload(files, encode, max_tokens_per_chunk, prompt_overhead))
    agg = _aggregate(outputs, chunks_for_agg)

    # Map to our CLI's normalized list
    findings: List[Dict] = []
    for fp, items in agg["findings_by_file"].items():
        for it in items:
            lines = it.get("lines") or []
            line = int(lines[0]) if isinstance(lines, list) and lines else 1
            sev = it.get("severity", "LOW").upper()
            issue = it.get("title", "Issue")
            # Put the long explanation into 'suggestion' so PR comment is actionable
            suggestion = it.get("details", "Consider refactoring.")
            findings.append({
                "file": fp,
                "line": line,
                "severity": "LOW" if sev == "NIT" else sev,
                "issue": issue,
                "suggestion": suggestion
            })

    # Optional: keep NIT separate? For now NIT -> LOW to keep gating simple.
    # De-dup final list by (file,line,issue)
    seen = set()
    unique = []
    for f in findings:
        key = (f["file"], f["line"], f["issue"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique
