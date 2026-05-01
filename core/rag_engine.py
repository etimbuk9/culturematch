import os
import re
from dataclasses import dataclass
from typing import Optional

import faiss
import numpy as np
import dspy
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------------------------
# Lightweight document container — mirrors LangChain's Document.page_content
# interface so match_engine.py works unchanged.
# ---------------------------------------------------------------------------

@dataclass
class Document:
    page_content: str
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ---------------------------------------------------------------------------
# PDF loading & chunking (no LangChain)
# ---------------------------------------------------------------------------

def _load_pdf_text(pdf_path: str) -> list[tuple[str, int]]:
    """Return list of (page_text, page_number) tuples."""
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append((text, i + 1))
    return pages


def _split_text(
    text: str,
    chunk_size: int = 700,
    chunk_overlap: int = 200,
) -> list[str]:
    """
    Recursive character splitter — replicates LangChain's
    RecursiveCharacterTextSplitter behaviour without the dependency.
    Splits on paragraphs → sentences → words in that priority order.
    """
    separators = ["\n\n", "\n", ". ", " ", ""]
    chunks: list[str] = []

    def _split(s: str, seps: list[str]) -> list[str]:
        if not seps:
            return [s]
        sep = seps[0]
        parts = s.split(sep) if sep else list(s)
        result, current = [], ""
        for part in parts:
            candidate = (current + sep + part).lstrip(sep) if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current:
                    result.append(current)
                # part itself may be too long — recurse with next separator
                if len(part) > chunk_size:
                    result.extend(_split(part, seps[1:]))
                    current = ""
                else:
                    current = part
        if current:
            result.append(current)
        return result

    raw_chunks = _split(text, separators)

    # Apply overlap: each chunk starts chunk_overlap chars before the
    # previous chunk ended.
    i = 0
    while i < len(raw_chunks):
        chunk = raw_chunks[i]
        # Extend chunk until chunk_size is reached
        j = i + 1
        while j < len(raw_chunks) and len(chunk) + len(raw_chunks[j]) + 1 <= chunk_size:
            chunk += " " + raw_chunks[j]
            j += 1
        chunks.append(chunk.strip())
        # Advance, but step back by overlap amount
        overlap_chars = 0
        k = j - 1
        while k >= i and overlap_chars < chunk_overlap:
            overlap_chars += len(raw_chunks[k])
            k -= 1
        i = max(i + 1, k + 2)

    return [c for c in chunks if c]


# ---------------------------------------------------------------------------
# DSPy Retriever backed by a native FAISS index
# ---------------------------------------------------------------------------

class FAISSRetriever(dspy.Retrieve):
    """
    A DSPy Retrieve module backed by a native FAISS flat L2 index.

    Usage (DSPy pipeline):
        retriever = FAISSRetriever(index, corpus, model, k=5)
        passages = retriever("student looking for a data analyst role")

    Usage (direct, compatible with match_engine.py):
        results = retriever.similarity_search(query, k=10)
        for r in results:
            print(r.page_content)
    """

    def __init__(
        self,
        index: faiss.Index,
        corpus: list[Document],
        model: SentenceTransformer,
        k: int = 5,
    ):
        super().__init__(k=k)
        self.index = index
        self.corpus = corpus
        self.model = model

    # --- DSPy Retrieve interface -------------------------------------------

    def forward(self, query: str, k: Optional[int] = None) -> dspy.Prediction:
        docs = self.similarity_search(query, k=k or self.k)
        passages = [d.page_content for d in docs]
        return dspy.Prediction(passages=passages)

    # --- LangChain-compatible interface (used by match_engine.py) ----------

    def similarity_search(self, query: str, k: int = 5) -> list[Document]:
        q_vec = self.model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(q_vec)
        _, indices = self.index.search(q_vec, k)
        return [self.corpus[i] for i in indices[0] if i < len(self.corpus)]


# ---------------------------------------------------------------------------
# Public factory — drop-in replacement for the original build_vectorstore()
# ---------------------------------------------------------------------------

def build_vectorstore(
    pdf_path: str,
    chunk_size: int = 700,
    chunk_overlap: int = 200,
    embed_model_name: str = "all-MiniLM-L6-v2",
    k: int = 5,
) -> Optional[FAISSRetriever]:
    """
    Load a PDF, chunk it, embed with a SentenceTransformer, index with FAISS,
    and return a FAISSRetriever that is both a dspy.Retrieve module and exposes
    similarity_search() for direct use.

    Returns None if the PDF does not exist (same behaviour as before).
    """
    if not os.path.exists(pdf_path):
        return None

    # 1. Load & chunk
    pages = _load_pdf_text(pdf_path)
    corpus: list[Document] = []
    for page_text, page_num in pages:
        for chunk in _split_text(page_text, chunk_size, chunk_overlap):
            corpus.append(Document(
                page_content=chunk,
                metadata={"page": page_num, "source": pdf_path},
            ))

    if not corpus:
        return None

    # 2. Embed
    model = SentenceTransformer(embed_model_name)
    texts = [doc.page_content for doc in corpus]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False).astype("float32")
    faiss.normalize_L2(embeddings)          # cosine similarity via inner product

    # 3. Build FAISS index (IndexFlatIP = exact cosine after L2 normalisation)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    return FAISSRetriever(index=index, corpus=corpus, model=model, k=k)
