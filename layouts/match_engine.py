import streamlit as st
from core.rag_engine import build_vectorstore
from core.llm_engine import build_matcher
from core.matcher import calculate_match_score
import time
import pickle
import os
import core.rag_merger as rag_merger


def show_old():

    full_start = time.time()

    st.title("AI Match Engine")

    student = st.session_state.get("student_profile")
    print(student)

    if not student:
        st.warning("Create student profile first")
        return

    start = time.time()

    if 'vectorstore.pkl' in os.listdir():
        with open('vectorstore.pkl', 'rb') as f:
            vectorstore = pickle.load(f)
    else:
        vectorstore = build_vectorstore("data/uploads/company_file.pdf", k=10)
        with open('vectorstore.pkl', 'wb') as f:
            pickle.dump(vectorstore, f)

    end = time.time()

    print(f"Vectorstore build time: {end - start} seconds")

    if not vectorstore:
        st.error("Upload company PDF first")
        return

    results = vectorstore.similarity_search(str(student), k=10)
    # for r in results:
    #     print("-----------------------------------")
    #     print(r.page_content)

    matcher = build_matcher()
    outputs = [matcher(
        student_profile=str(student),
        job_context=r.page_content) for r in results
    ]

    outputs = sorted(outputs, key=lambda x: x.fit_score, reverse=True)[:5]

    for idx, res in enumerate(outputs):
        st.markdown("---")
        st.write(f"Job Match {idx + 1}")
        st.subheader(f"Job Title: {res.job_title}")
        st.metric("Fit Score", res.fit_score)
        st.write(res.reasoning)

    full_end = time.time()
    print(f"Total match engine time: {full_end - full_start} seconds")


def show():

    full_start = time.time()

    st.title("AI Match Engine")

    student = st.session_state.get("student_profile")
    print(student)

    if not student:
        st.warning("Create student profile first")
        return

    rag = rag_merger.RAG()

    with st.spinner("Finding your best job matches..."):
        response = rag(student_profile=str(student))

    st.session_state["company_jobs"] = response.ranked_fits
    output = sorted(response.ranked_fits,
                    key=lambda x: x.fit_score, reverse=True)[:5]

    for idx, fit in enumerate(output):
        st.markdown("---")
        st.write(f"Job Match {idx + 1}")
        st.subheader(f"Job Title: {fit.job_title}")
        st.metric("Fit Score", fit.fit_score)
        st.write(fit.reasoning)

    full_end = time.time()
    print(f"Total match engine time: {full_end - full_start} seconds")
