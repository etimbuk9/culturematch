import streamlit as st
from core.rag_engine import build_vectorstore
from core.llm_engine import build_matcher
from core.matcher import calculate_match_score


def show():

    st.title("AI Match Engine")

    student = st.session_state.get("student_profile")
    print(student)

    if not student:
        st.warning("Create student profile first")
        return

    vectorstore = build_vectorstore("data/uploads/company_jobs.pdf")

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

    # for idx, r in enumerate(results):

    #     res = matcher(
    #         student_profile=str(student),
    #         job_context=r.page_content
    #     )

    #     st.markdown("---")
    #     st.write(f"Job Match {idx + 1}")
    #     st.subheader(f"Job Title: {res.job_title}")
    #     st.metric("Fit Score", res.fit_score)
    #     st.write(res.reasoning)
