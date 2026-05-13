import dspy
import streamlit as st


@st.cache_resource
def init_llm():
    global lm

    lm = dspy.LM(
        model="ollama_chat/mistral",
        # model="ollama_chat/gemma4:31b-cloud",
        api_base="http://localhost:11434",
    )
    dspy.settings.configure(lm=lm)
    st.session_state["lm"] = lm
    return lm


if "lm" not in st.session_state:
    init_llm()


class MatchSignature(dspy.Signature):
    student_profile = dspy.InputField()
    job_context = dspy.InputField()
    job_title = dspy.OutputField(
        description='This is the job title extracted from the job context. It should be concise and directly extracted from the job description provided in the job context.')
    fit_score: float = dspy.OutputField(
        description='This is the fit score calculated based on the student profile and job context. It ranges from 0% to 100%, where 0% indicates no fit and 100% indicates a perfect fit. The score should be calculated based on the relevance of the student profile to the job context, considering factors such as skills, experience, and qualifications.')
    reasoning: str = dspy.OutputField(
        description='This is the reasoning behind the fit score. Make it personal and specific to the student profile and job context. Explain why the student is a good fit or not for the job, highlighting specific aspects of the student profile that align with or do not meet the requirements of the job context. Also use terms like you instead of the student name to make it more personal.')


def build_matcher():
    return dspy.ChainOfThought(MatchSignature)
