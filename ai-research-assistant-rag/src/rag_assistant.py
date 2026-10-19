from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass(frozen=True)
class TextChunk:
    source: str
    chunk_id: int
    text: str


@dataclass(frozen=True)
class SearchResult:
    source_id: str
    source: str
    chunk_id: int
    score: float
    text: str


def chunk_text(text: str, chunk_size: int = 850, overlap: int = 120) -> list[str]:
    """Split text into overlapping chunks, preferring whitespace boundaries."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size.")
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start + int(chunk_size * 0.65), end)
            if boundary > start:
                end = boundary
        piece = cleaned[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _read_file(path: Path, base_dir: Path) -> list[tuple[str, str]]:
    relative = path.relative_to(base_dir).as_posix()
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF reading requires pypdf; install the root requirements.txt.") from exc
        pages = []
        for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append((f"{relative} · p. {page_number}", text))
        return pages
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return [(relative, text)] if text else []


def load_chunks(documents_dir: Path, chunk_size: int = 850, overlap: int = 120) -> list[TextChunk]:
    """Load supported documents and return chunks with traceable source labels."""
    if not documents_dir.exists():
        return []
    chunks: list[TextChunk] = []
    for path in sorted(documents_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            for source, text in _read_file(path, documents_dir):
                for chunk_id, piece in enumerate(chunk_text(text, chunk_size, overlap), start=1):
                    chunks.append(TextChunk(source=source, chunk_id=chunk_id, text=piece))
    return chunks


class ResearchAssistant:
    """Local TF-IDF retrieval with optional grounded OpenAI answer generation."""

    def __init__(self, documents_dir: Path, chunk_size: int = 850, overlap: int = 120):
        self.documents_dir = Path(documents_dir)
        self.chunks = load_chunks(self.documents_dir, chunk_size, overlap)
        self.vectorizer = None
        self.matrix = None
        if self.chunks:
            self.vectorizer = TfidfVectorizer(
                lowercase=True, stop_words="english", ngram_range=(1, 2), sublinear_tf=True
            )
            self.matrix = self.vectorizer.fit_transform([chunk.text for chunk in self.chunks])

    def retrieve(self, query: str, top_k: int = 4) -> list[SearchResult]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")
        if not query.strip() or not self.chunks or self.vectorizer is None or self.matrix is None:
            return []
        query_vector = self.vectorizer.transform([query])
        scores = (self.matrix @ query_vector.T).toarray().ravel()
        ranked = np.argsort(scores)[::-1]
        results: list[SearchResult] = []
        for index in ranked:
            score = float(scores[index])
            if score <= 0:
                continue
            chunk = self.chunks[int(index)]
            results.append(SearchResult(
                source_id=f"S{len(results) + 1}",
                source=chunk.source,
                chunk_id=chunk.chunk_id,
                score=score,
                text=chunk.text,
            ))
            if len(results) >= top_k:
                break
        return results

    @staticmethod
    def _extractive_answer(results: Iterable[SearchResult]) -> str:
        results = list(results)
        if not results:
            return (
                "I couldn't find a passage that clearly matches this question in the indexed documents. "
                "Try different wording or add a document that covers the topic."
            )
        lines = ["I found these passages in your indexed documents:"]
        for result in results[:3]:
            lines.append(f"- {result.text} [{result.source_id}]")
        lines.append(
            "This is a retrieval-based summary, not an independent fact check. "
            "Open the cited sources before relying on the answer."
        )
        return "\n\n".join(lines)

    @staticmethod
    def _openai_answer(query: str, results: list[SearchResult]) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI generation is optional. Install ai-research-assistant-rag/requirements-llm.txt."
            ) from exc
        context = "\n\n".join(
            f"[{item.source_id}] Source: {item.source}\n{item.text}" for item in results
        )
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=(
                "You are a careful research assistant. Answer only from the supplied source passages. "
                "Cite material claims with exact source labels such as [S1]. If the evidence is insufficient, "
                "say what is missing. Do not invent sources, quotations, data, or citations."
            ),
            input=f"Question: {query}\n\nSource passages:\n{context}",
        )
        return response.output_text.strip()

    def answer(self, query: str, top_k: int = 4, use_llm: bool | None = None) -> dict[str, object]:
        results = self.retrieve(query, top_k=top_k)
        should_use_llm = bool(os.getenv("OPENAI_API_KEY")) if use_llm is None else use_llm
        if not results:
            return {"answer": self._extractive_answer(results), "sources": results, "mode": "local retrieval"}
        if should_use_llm:
            answer = self._openai_answer(query, results)
            mode = "OpenAI + local retrieval"
        else:
            answer = self._extractive_answer(results)
            mode = "local extractive retrieval"
        return {"answer": answer, "sources": results, "mode": mode}
