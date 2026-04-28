import streamlit as st
import pandas as pd


def show():

    st.title("Analytics")
    profile = st.session_state.get("student_profile")
    profile_df = pd.DataFrame([profile]) if profile else pd.DataFrame()

    if st.session_state.get("student_profile"):
        st.dataframe(profile_df)  # Display the student profile as a DataFrame
    else:
        st.info("No data yet")
