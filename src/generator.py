"""Grounded Groq answer generation for retrieved Groww source excerpts."""

from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

INSUFFICIENT_EVIDENCE_MESSAGE = "The information is not available in the indexed sources."
DEFAULT_MODEL = "openai/gpt-oss-20b"


class GenerationError(RuntimeError):
    """Raised when an answer cannot be generated safely."""


def source_records(hits: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Return deterministic source labels for the retrieved records."""
    sources: list[dict[str, str]] = []
    seen_urls: set[str] = set()

    for hit in hits:
        url = str(hit.get("source_url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append(
            {
                "label": f"S{len(sources) + 1}",
                "name": str(hit.get("source_name") or "Groww source").strip(),
                "url": url,
            }
        )
    return sources


def _build_context(hits: list[dict[str, Any]]) -> str:
    labels_by_url = {source["url"]: source["label"] for source in source_records(hits)}
    excerpts: list[str] = []

    for hit in hits:
        url = str(hit.get("source_url") or "").strip()
        text = str(hit.get("text") or "").strip()
        label = labels_by_url.get(url)
        if label and text:
            excerpts.append(f"[{label}]\n{text}")

    return "\n\n---\n\n".join(excerpts)


def generate_answer(query: str, hits: list[dict[str, Any]]) -> str:
    """Generate a concise answer grounded exclusively in retrieved text."""
    context = _build_context(hits)
    if not context:
        return INSUFFICIENT_EVIDENCE_MESSAGE

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise GenerationError("Groq is not configured in the process environment.")

    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
    system_prompt = (
        "You are a facts-only mutual-fund information assistant. Use only the "
        "source excerpts supplied by the user as factual evidence; do not use "
        "outside knowledge or infer missing facts. If the excerpts do not directly "
        f"answer the question, respond with exactly: {INSUFFICIENT_EVIDENCE_MESSAGE}\n\n"
        "Do not give personalized investment advice, recommendations, or fund "
        "comparisons. Do not make return or performance claims unless they are "
        "explicitly supported by the excerpts. Keep a supported answer to three "
        "sentences or fewer. Add one or more source labels to each factual sentence."
        "Use only the exact source labels provided in the context, such as "
        "[S1], [S2], [S3], or [S4]. Never invent a label or use a label "
        "that was not provided. If the excerpts do not support the answer, "
        "respond with exactly: " 
        f"{INSUFFICIENT_EVIDENCE_MESSAGE}\n\n"
        "Never create, modify, or output a URL."
    )
    user_prompt = f"Question:\n{query.strip()}\n\nSource excerpts:\n{context}"

    try:
        completion = Groq(api_key=api_key).chat.completions.create(
            model=model,
            temperature=0,
            max_tokens=300,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        answer = (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        print(f"Groq error: {type(exc).__name__}: {exc}")
        raise GenerationError("Groq request failed.") from exc

    if not answer:
        raise GenerationError("Groq returned an empty answer.")

    if answer != INSUFFICIENT_EVIDENCE_MESSAGE:
        allowed_labels = {f"[{source['label']}]" for source in source_records(hits)}
        cited_labels = set(re.findall(r"\[S\d+\]", answer))
        if not cited_labels or not cited_labels.issubset(allowed_labels):
            raise GenerationError("Groq returned invalid source labels.")
        if "http://" in answer.lower() or "https://" in answer.lower():
            raise GenerationError("Groq returned a URL instead of source labels.")
    return answer
