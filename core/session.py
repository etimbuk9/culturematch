import streamlit as st
import pandas as pd


def init_session():
    if "student_profile" not in st.session_state:
        st.session_state.student_profile = None

    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []

    if "skill_levels" not in st.session_state:
        st.session_state.skill_levels = {}

    if "show_remaining_jobs" not in st.session_state:
        st.session_state.show_remaining_jobs = False

    if "company_name" not in st.session_state:
        st.session_state.company_name = None

    if "company_jobs" not in st.session_state:
        st.session_state.company_jobs = []

    if "context" not in st.session_state:
        st.session_state.context = []


def load_master_data():
    return {
        "skills": [
            "Python", "C++", "Embedded C", "VHDL", "Verilog", "FPGA", "IoT",
            "RTOS", "ARM", "Digital Design", "Machine Learning", "Deep Learning",
            "Networking", "React", "Docker", "Linux", "Kubernetes", "AWS", "Azure"
        ],
        "culture": [
            "Fast-paced", "Startup vibe", "Research-heavy", "Corporate structured",
            "Collaborative", "Remote-first", "Office-centric", "Agile sprints"
        ],
        "personality": [
            "Independent", "Team-oriented", "Detail-focused", "Big-picture thinker",
            "Quick learner", "Patient & methodical", "Innovative risk-taker"
        ],
        "character": [
            "Creative", "Disciplined", "Adaptable", "Reliable", "Proactive",
            "Empathetic", "Resilient"
        ],
        "degrees": [
            "B.Eng Computer Engineering",
            "B.Eng Electrical/Electronics Engineering",
            "B.Sc Computer Science",
            "B.Eng Software Engineering",
            "B.Tech Information Technology",
            "Other (please specify)"
        ]
    }

# def load_master_data(file_path='master_list.xlsx'):
#     """Loads dropdown options from Excel."""
#     try:
#         df_dict = pd.read_excel(file_path, sheet_name=None)
#         return {
#             "skills": df_dict.get('skills', pd.DataFrame())['Skill'].dropna().tolist(),
#             "culture": df_dict.get('culture', pd.DataFrame())['Culture'].dropna().tolist(),
#             "personality": df_dict.get('personality', pd.DataFrame())['Personality'].dropna().tolist(),
#             "character": df_dict.get('character', pd.DataFrame())['Character'].dropna().tolist(),
#             "degrees": df_dict.get('degrees', pd.DataFrame())['Degree'].dropna().tolist()
#         }
#     except:
#         return {"skills": [], "culture": [], "personality": [], "character": [], "degrees": []}
