import streamlit as st
from core.session import load_master_data
from core.matcher import calculate_match_score
import pandas as pd
import os

# -----------------------------
# LOAD MASTER DATA
# -----------------------------
master = load_master_data() or {}

# -----------------------------
# FORCE CORRECT SESSION STATE TYPES
# -----------------------------
if "company_jobs" not in st.session_state or not isinstance(st.session_state.company_jobs, pd.DataFrame):
    st.session_state.company_jobs = pd.DataFrame()

if "jobs_df" not in st.session_state or not isinstance(st.session_state.jobs_df, pd.DataFrame):
    st.session_state.jobs_df = pd.DataFrame()

if "company_name" not in st.session_state:
    st.session_state.company_name = None

if "student_profile" not in st.session_state:
    st.session_state.student_profile = None


# -----------------------------
# MAIN FUNCTION
# -----------------------------
def show():
    st.title("Company Portal")

    # -----------------------------
    # FILE UPLOAD (SAFE)
    # -----------------------------
    uploaded = st.file_uploader("Upload Company PDF", type="pdf")

    if uploaded:
        os.makedirs("data/uploads", exist_ok=True)

        file_path = f"data/uploads/company_file.pdf"
        with open(file_path, "wb") as f:
            f.write(uploaded.getbuffer())

        st.success("Uploaded successfully")

    st.subheader("Manage Your Jobs & Explore Opportunities")

    # -----------------------------
    # LOGIN SECTION
    # -----------------------------
    if st.session_state.company_name is None:
        st.info("Enter your company name to manage jobs (demo mode – no password yet)")

        company_name = st.text_input(
            "Company Name",
            placeholder="e.g. Nexlify Dynamics"
        )

        if st.button("Continue as Company", type="primary"):
            if company_name.strip():
                st.session_state.company_name = company_name.strip()
                st.success(f"Welcome, **{st.session_state.company_name}**!")
                st.rerun()
            else:
                st.error("Company name is required")

    else:
        st.success(f"Logged in as: **{st.session_state.company_name}**")

        if st.button("Logout / Switch Company"):
            st.session_state.company_name = None
            st.rerun()

        tab_post, tab_my, tab_all = st.tabs([
            "📝 Post New Job",
            "📋 My Posted Jobs",
            "🌐 All Jobs (Other Companies)"
        ])

        # -----------------------------
        # POST JOB TAB
        # -----------------------------
        with tab_post:
            st.subheader("Create a New Job Opening")

            with st.form("post_job_form"):
                role = st.text_input(
                    "Job Role / Title*",
                    placeholder="e.g. Senior Python Developer"
                )

                skills = st.multiselect(
                    "Required Skills*",
                    options=master.get("skills", []),
                    placeholder="Select required skills..."
                )

                culture = st.multiselect(
                    "Preferred Culture",
                    options=master.get("culture", [])
                )

                personality = st.multiselect(
                    "Preferred Personality Traits",
                    options=master.get("personality", [])
                )

                character = st.multiselect(
                    "Preferred Character Traits",
                    options=master.get("character", [])
                )

                submitted = st.form_submit_button("Post Job", type="primary")

                if submitted:
                    if not role.strip():
                        st.error("Job role/title is required")

                    elif not skills:
                        st.error("At least one skill is required")

                    else:
                        new_job = {
                            "company": st.session_state.company_name,
                            "role": role.strip(),
                            "skills": skills,
                            "culture": culture,
                            "personality": personality,
                            "character": character
                        }

                        # SAFE CONCAT (always DataFrame now)
                        st.session_state.company_jobs = pd.concat(
                            [st.session_state.company_jobs,
                                pd.DataFrame([new_job])],
                            ignore_index=True
                        )

                        st.session_state.jobs_df = pd.concat(
                            [st.session_state.jobs_df,
                                pd.DataFrame([new_job])],
                            ignore_index=True
                        )

                        st.success(f"Job posted: **{role}**")
                        st.rerun()

        # -----------------------------
        # MY JOBS TAB
        # -----------------------------
        with tab_my:
            st.subheader("My Posted Jobs")

            if st.session_state.company_jobs.empty:
                st.info("You haven't posted any jobs yet.")
            else:
                for idx, job in st.session_state.company_jobs.iterrows():
                    with st.expander(f"{job['role']} – {job['company']}"):

                        st.markdown(f"**Skills:** {', '.join(job['skills'])}")
                        st.markdown(
                            f"**Culture:** {', '.join(job['culture'])}")
                        st.markdown(
                            f"**Personality:** {', '.join(job['personality'])}")
                        st.markdown(
                            f"**Character:** {', '.join(job['character'])}")

                        # SAFE MATCH CHECK
                        if st.session_state.get("student_profile"):
                            student = st.session_state.student_profile
                            score = calculate_match_score(student, job)
                            st.markdown(f"**Match Score:** **{score}%**")

                        if st.button("Delete", key=f"del_{idx}"):
                            st.session_state.company_jobs = (
                                st.session_state.company_jobs
                                .drop(idx)
                                .reset_index(drop=True)
                            )

                            st.success("Job deleted")
                            st.rerun()

        # -----------------------------
        # ALL JOBS TAB
        # -----------------------------
        with tab_all:
            st.subheader("All Jobs (from all companies)")

            if st.session_state.jobs_df.empty:
                st.info("No jobs posted yet.")
            else:
                view_df = st.session_state.jobs_df.copy()

                for col in ["skills", "culture", "personality", "character"]:
                    view_df[col] = view_df[col].apply(lambda x: ", ".join(x))

                st.dataframe(
                    view_df[["company", "role", "skills", "culture"]],
                    use_container_width=True
                )


# import streamlit as st
# from core.session import load_master_data
# from core.matcher import calculate_match_score
# import pandas as pd

# master = load_master_data()

# def show():
#     st.title("Company Portal")

#     uploaded = st.file_uploader("Upload Company PDF", type="pdf")

#     if uploaded:
#         with open("data/uploads/company.pdf", "wb") as f:
#             f.write(uploaded.getbuffer())

#         st.success("Uploaded successfully")


#     st.subheader("Manage Your Jobs & Explore Opportunities")

#     if st.session_state.company_name is None:
#         st.info("Enter your company name to manage jobs (demo mode – no password yet)")
#         company_name = st.text_input("Company Name", placeholder="e.g. Nexlify Dynamics")
#         if st.button("Continue as Company", type="primary"):
#             if company_name.strip():
#                 st.session_state.company_name = company_name.strip()
#                 st.success(f"Welcome, **{st.session_state.company_name}**!")
#                 st.rerun()
#             else:
#                 st.error("Company name is required")
#     else:
#         st.success(f"Logged in as: **{st.session_state.company_name}**")
#         if st.button("Logout / Switch Company"):
#             st.session_state.company_name = None
#             st.rerun()

#         tab_post, tab_my, tab_all = st.tabs([
#             "📝 Post New Job",
#             "📋 My Posted Jobs",
#             "🌐 All Jobs (Other Companies)"
#         ])

#         with tab_post:
#             st.subheader("Create a New Job Opening")

#             with st.form("post_job_form"):
#                 role = st.text_input("Job Role / Title*", placeholder="e.g. Senior Python Developer")

#                 skills = st.multiselect(
#                     "Required Skills*",
#                     options=master["skills"],
#                     default=[],
#                     placeholder="Select required skills..."
#                 )

#                 culture = st.multiselect(
#                     "Preferred Culture",
#                     options=master["culture"],
#                     default=[]
#                 )

#                 personality = st.multiselect(
#                     "Preferred Personality Traits",
#                     options=master["personality"],
#                     default=[]
#                 )

#                 character = st.multiselect(
#                     "Preferred Character Traits",
#                     options=master["character"],
#                     default=[]
#                 )

#                 submitted = st.form_submit_button("Post Job", type="primary")

#                 if submitted:
#                     if not role.strip():
#                         st.error("Job role/title is required")
#                     elif not skills:
#                         st.error("At least one skill is required")
#                     else:
#                         new_job = {
#                             "company": st.session_state.company_name,
#                             "role": role.strip(),
#                             "skills": skills,
#                             "culture": culture,
#                             "personality": personality,
#                             "character": character
#                         }

#                         st.session_state.company_jobs = pd.concat([
#                             st.session_state.company_jobs,
#                             pd.DataFrame([new_job])
#                         ], ignore_index=True)

#                         st.session_state.jobs_df = pd.concat([
#                             st.session_state.jobs_df,
#                             pd.DataFrame([new_job])
#                         ], ignore_index=True)

#                         st.success(f"Job posted: **{role}**")
#                         st.rerun()

#         with tab_my:
#             st.subheader("My Posted Jobs")

#             if st.session_state.company_jobs.empty:
#                 st.info("You haven't posted any jobs yet.")
#             else:
#                 for idx, job in st.session_state.company_jobs.iterrows():
#                     with st.expander(f"{job['role']} – {job['company']}"):
#                         st.markdown(f"**Skills:** {', '.join(job['skills'])}")
#                         st.markdown(f"**Culture:** {', '.join(job['culture'])}")
#                         st.markdown(f"**Personality:** {', '.join(job['personality'])}")
#                         st.markdown(f"**Character:** {', '.join(job['character'])}")

#                         if st.session_state.student_profile:
#                             student = st.session_state.student_profile
#                             score = calculate_match_score(student, job)
#                             st.markdown(f"**Match Score:** **{score}%**")

#                         if st.button("Delete", key=f"del_{idx}"):
#                             st.session_state.company_jobs = st.session_state.company_jobs.drop(idx)
#                             st.success("Job deleted")
#                             st.rerun()

#         with tab_all:
#             st.subheader("All Jobs (from all companies)")

#             if st.session_state.jobs_df.empty:
#                 st.info("No jobs posted yet.")
#             else:
#                 view_df = st.session_state.jobs_df.copy()
#                 for col in ["skills", "culture", "personality", "character"]:
#                     view_df[col] = view_df[col].apply(lambda x: ", ".join(x))
#                 st.dataframe(view_df[["company", "role", "skills", "culture"]], use_container_width=True)
