import streamlit as st
from ui.components import load_css
from utilities.loaders import load_jobs_from_docx
from core.session import init_session

st.set_page_config(
    page_title="CultureMatch AI",
    page_icon="🎯",
    layout="wide"
)

load_css()

if "jobs_df" not in st.session_state:
    st.session_state.jobs_df = load_jobs_from_docx()

init_session()


st.sidebar.title("🎯 CultureMatch AI")

page = st.sidebar.radio("Navigation", [
    "Landing",
    "Student",
    "Company",
    "Match Engine",
    "Analytics"
])

if page == "Landing":
    from layouts.landing import show
    show()

elif page == "Student":
    from layouts.student import show
    show()

elif page == "Company":
    from layouts.company import show
    show()

elif page == "Match Engine":
    from layouts.match_engine import show
    show()

elif page == "Analytics":
    from layouts.analytics import show
    show()
