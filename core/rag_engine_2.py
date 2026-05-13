import os
from dataclasses import dataclass
from typing import Optional

import faiss
import numpy as np
import dspy
from pypdf import PdfReader


# ---------------------------------------------------------------------------
# Lightweight document container
# ---------------------------------------------------------------------------

@dataclass
class Document:
    page_content: str
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


# ---------------------------------------------------------------------------
# PDF loading & chunking
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
    separators = ["\n\n", "\n", ". ", " ", ""]

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
                if len(part) > chunk_size:
                    result.extend(_split(part, seps[1:]))
                    current = ""
                else:
                    current = part
        if current:
            result.append(current)
        return result

    raw_chunks = _split(text, separators)

    chunks: list[str] = []
    i = 0
    while i < len(raw_chunks):
        chunk = raw_chunks[i]
        j = i + 1
        while j < len(raw_chunks) and len(chunk) + len(raw_chunks[j]) + 1 <= chunk_size:
            chunk += " " + raw_chunks[j]
            j += 1
        chunks.append(chunk.strip())
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
    A DSPy Retrieve module backed by a native FAISS flat IP index.

    Embeddings are produced via dspy.Embedder (litellm-backed), so no
    HuggingFace / sentence-transformers dependency is required.

    Non-DSPy attributes (index, corpus, embedder) are stored via
    object.__setattr__ to bypass dspy.Module's __setattr__ interceptor,
    which would otherwise swallow them into the module-tracking machinery
    and make them inaccessible as normal instance attributes.
    """

    def __init__(
        self,
        index: faiss.Index,
        corpus: list[Document],
        embedder: dspy.Embedder,
        k: int = 5,
    ):
        super().__init__(k=k)
        # Use object.__setattr__ so dspy.Module's __setattr__ does not
        # intercept these and hide them from normal attribute lookup.
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "corpus", corpus)
        object.__setattr__(self, "embedder", embedder)

    # --- DSPy Retrieve interface -------------------------------------------

    def forward(self, query: str, k: Optional[int] = None) -> dspy.Prediction:
        docs = self.similarity_search(query, k=k or self.k)
        passages = [d.page_content for d in docs]
        return dspy.Prediction(passages=passages)

    # --- Direct / match_engine.py-compatible interface ---------------------

    def similarity_search(self, query: str, k: int = 5) -> list[Document]:
        embedder = object.__getattribute__(self, "embedder")
        index = object.__getattribute__(self, "index")
        corpus = object.__getattribute__(self, "corpus")

        q_vec = np.array(embedder.encode([query]), dtype="float32")
        faiss.normalize_L2(q_vec)
        _, indices = index.search(q_vec, k)
        return [corpus[i] for i in indices[0] if i < len(corpus)]


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def build_vectorstore(
    pdf_path: str,
    chunk_size: int = 700,
    chunk_overlap: int = 200,
    embed_model: str = "openai/text-embedding-3-small",
    k: int = 5,
) -> Optional[FAISSRetriever]:
    """
    Load a PDF, chunk it, embed with dspy.Embedder, index with FAISS,
    and return a FAISSRetriever.

    embed_model accepts any litellm embedding model string:
        "openai/text-embedding-3-small"   # OpenAI (default)
        "cohere/embed-english-v3.0"       # Cohere
        "ollama/nomic-embed-text"         # local Ollama
        "azure/<your-deployment>"         # Azure OpenAI
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
    embedder = dspy.Embedder(embed_model)
    texts = [doc.page_content for doc in corpus]
    embeddings = np.array(embedder(texts), dtype="float32")
    faiss.normalize_L2(embeddings)

    # 3. Build FAISS index (IndexFlatIP = exact cosine after L2 normalisation)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    return FAISSRetriever(index=index, corpus=corpus, embedder=embedder, k=k)
