from typing import Literal
import threading
import dspy
from dotenv import load_dotenv
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import dspy
from pypdf import PdfReader
import torch
import pickle
import os
import streamlit as st


INFERENCE_TIMEOUT = 30  # seconds before switching to fallback model

primary_lm = dspy.LM(
    model='ollama_chat/mistral',
    api_base="http://127.0.0.1:11434",
    api_key='',
    cache=True,
)

fallback_lm = dspy.LM(
    model='ollama_chat/gemma4:31b-cloud',
    api_base="http://127.0.0.1:11434",
    api_key='',
    cache=True,
)


def _timed_call(fn, timeout, *args, **kwargs):
    result_box = [None]
    exc_box = [None]

    def _run():
        try:
            result_box[0] = fn(*args, **kwargs)
        except Exception as e:
            exc_box[0] = e

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout)

    if t.is_alive():
        return None, TimeoutError(f"Inference exceeded {timeout}s")
    if exc_box[0]:
        return None, exc_box[0]
    return result_box[0], None


def initialize():
    load_dotenv()

    device = "mps" if torch.backends.mps.is_available() else "cpu"

    pdf_data, _ = _load_pdf_text("data/uploads/company_file.pdf")

    corpus = []
    for page_text, page_num in pdf_data:
        for chunk in _split_text(page_text, 700, 200):
            corpus.append(chunk)

    if not os.path.exists('vectorstore.pkl'):
        st.warning(
            "Building vectorstore for the first time. This may take a moment...")

        st_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2", device=device)
        print('Model loaded')

        with open('vectorstore.pkl', 'wb') as f:
            pickle.dump(st_model, f)
    else:
        with open('vectorstore.pkl', 'rb') as f:
            st_model = pickle.load(f)
        print('Model loaded from cache')

    embedder = dspy.Embedder(st_model.encode, batch_size=64)
    print('Embedder created')

    search = dspy.retrievers.Embeddings(
        corpus=corpus,
        embedder=embedder,
        k=10,
    )

    return search


def _load_pdf_text(pdf_path: str):
    """Return list of (page_text, page_number) tuples."""
    reader = PdfReader(pdf_path)
    pages = []
    page_info = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append((text, i + 1))
            page_info.append(text)
    return pages, page_info


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


class JobFit(BaseModel):
    job_title: str
    fit_score: float
    skills_alignment_score: float
    culture_alignment_score: float
    personality_alignment_score: float
    character_alignment_score: float
    reasoning: str
    required_skills: list[str] = []


class RagResponse(dspy.Signature):
    student_profile = dspy.InputField()
    job_context = dspy.InputField(
        description='Relevant passages from the company job descriptions.')
    ranked_fits: list[JobFit] = dspy.OutputField(
        description=(
            'Top 5 job fits for the student, ranked in descending order by fit_score. '
            'Each entry must include job_title (concise, directly from context), '
            'fit_score (0 to 100 float), and reasoning (personal, second-person, specific '
            'to the student profile and job). Explain why the student is a good fit or not for the job, highlighting specific aspects of the student profile that align with or do not meet the requirements of the job context. Also use terms like you instead of the student name to make it more personal.'
            'You are also to include sub-scores for skills_alignment_score, culture_alignment_score, personality_alignment_score, and character_alignment_score that contribute to the overall fit_score. You are to determine how well that aspect of the student profile matches the job context and assign a score from 0 to 100 for each, which should be reflected in the reasoning.'
            'Finally, extract a list of required skills from the job context and include it in the required_skills field for each job fit.'
        )
    )


class RAG(dspy.Module):

    def __init__(self):
        self.respond = dspy.ChainOfThought(RagResponse)

    def _infer(self, student_profile, job_context, lm=None):
        with dspy.context(lm=lm or primary_lm):
            return self.respond(student_profile=student_profile, job_context=job_context)

    def forward(self, student_profile: str):
        search = initialize()
        ctx_passages = search(student_profile).passages
        job_context = "\n\n".join([f"- {p}" for p in ctx_passages])

        result, err = _timed_call(
            self._infer,
            INFERENCE_TIMEOUT,
            student_profile,
            job_context,
            lm=primary_lm,
        )

        if err:
            st.warning(
                "Mistral is taking too long — switching to Gemma4 (31B)...")
            result = self._infer(student_profile, job_context, lm=fallback_lm)

        return result


rag = RAG()


def main():
    student_profile = "{'name': 'Imadara Oku', 'age': 22, 'email': 'yourname@topfaith.edu.ng', 'phone': '+234', 'university': 'Topfaith University', 'degree': 'B.Eng Computer Engineering', 'grad_year': '500 Level / 2026', 'preferred_role': 'Embedded Systems Engineer, IoT Developer', 'cgpa': 4.8, 'skills': {'Python': 'Advanced', 'C++': 'Beginner'}, 'culture': ['Fast-paced', 'Startup vibe'], 'personality': ['Quick learner', 'Independent', 'Innovative risk-taker'], 'character': ['Proactive']}"
    pred = rag(student_profile=student_profile)

    print("-----DSPY History-----")
    print(dspy.inspect_history())

    print("-----Top 5 Job Fits (Ranked)-----")
    for i, fit in enumerate(pred.ranked_fits, start=1):
        print(f"\n#{i} {fit.job_title}  |  Fit Score: {fit.fit_score:.1f}%")
        print(f"    {fit.reasoning}")


if __name__ == "__main__":
    import time

    start = time.time()
    main()
    end = time.time()

    print(f"Total RAG execution time: {end - start} seconds")
