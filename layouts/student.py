import streamlit as st
from core.session import load_master_data
from core.matcher import calculate_match_score


master = load_master_data()


def show():

    st.title("Student Dashboard")

    if st.session_state.jobs_df.empty:
        st.error("No jobs could be loaded from jobs.docx.\nPlease check that the file exists and contains job data in tables.")
    else:
        st.caption(
            f"Loaded {len(st.session_state.jobs_df)} jobs from jobs.docx")

    if st.session_state.student_profile is None:
        st.subheader("Personal Information")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", "Imadara Oku")
            age = st.number_input("Age", min_value=18,
                                  max_value=40, value=22, step=1)
            email = st.text_input("Email Address", "yourname@topfaith.edu.ng")
            phone = st.text_input("Phone Number", "+234 ")
        with col2:
            university = st.text_input("University", "Topfaith University")
            degree_choice = st.selectbox("Degree", master["degrees"])
            degree = st.text_input(
                "Specify degree", "") if degree_choice == "Other (please specify)" else degree_choice
            grad_year = st.text_input(
                "Level / Expected Graduation Year", "500 Level / 2026")
            preferred_role = st.text_input(
                "Preferred Job Role(s)", "Embedded Systems Engineer, IoT Developer")

        cgpa = st.number_input("CGPA", 0.0, 5.0, 4.60,
                               step=0.01, format="%.2f")

        st.markdown("---")
        st.subheader("Work Preferences & Traits")

        col_a, col_b = st.columns(2)
        with col_a:
            culture = st.multiselect(
                "Preferred Culture", master["culture"], default=["Fast-paced"])
            personality = st.multiselect(
                "Personality Style", master["personality"], default=["Quick learner"])
        with col_b:
            character = st.multiselect(
                "Character Traits", master["character"], default=["Proactive"])

        st.markdown("---")
        st.subheader("Technical Skills")

        selected = st.multiselect(
            "Select skills you have experience with",
            options=master["skills"],
            default=st.session_state.selected_skills
        )
        st.session_state.selected_skills = selected

        if selected:
            st.markdown("##### Experience level for each selected skill")
            for skill in selected:
                default_level = st.session_state.skill_levels.get(
                    skill, "Intermediate")
                idx = ["Beginner", "Intermediate",
                       "Advanced", "Expert"].index(default_level)

                level = st.selectbox(
                    f"**{skill}**",
                    ["Beginner", "Intermediate", "Advanced", "Expert"],
                    index=idx,
                    key=f"level_{skill}"
                )
                st.session_state.skill_levels[skill] = level

        st.markdown("---")

        if st.button("Save Profile & Find Matches", type="primary", use_container_width=True):
            if not selected:
                st.error("Please select at least one skill")
            elif not st.session_state.skill_levels:
                st.error("Please set experience level for at least one skill")
            else:
                st.session_state.student_profile = {
                    "name": name.strip(),
                    "age": age,
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "university": university.strip(),
                    "degree": degree.strip(),
                    "grad_year": grad_year.strip(),
                    "preferred_role": preferred_role.strip(),
                    "cgpa": cgpa,
                    "skills": st.session_state.skill_levels.copy(),
                    "culture": culture,
                    "personality": personality,
                    "character": character
                }
                st.success("Profile saved!")
                st.rerun()

    else:
        p = st.session_state.student_profile

        st.success(
            f"Welcome back, **{p['name']}**  •  CGPA: **{p['cgpa']:.2f}**")
        st.caption(f"{p['degree']} • {p['university']} • {p['grad_year']}")

        if st.button("Edit Profile"):
            st.session_state.student_profile = None
            st.rerun()

        with st.expander("Your Profile", expanded=True):
            st.markdown(f"**Degree:** {p['degree']}")
            st.markdown(f"**Email:** {p['email']}")
            st.markdown(f"**Phone:** {p['phone']}")
            st.markdown(
                f"**Preferred Culture:** {', '.join(p.get('culture', [])) or '—'}")
            st.markdown(
                f"**Personality Style:** {', '.join(p.get('personality', [])) or '—'}")
            st.markdown(
                f"**Character Traits:** {', '.join(p.get('character', [])) or '—'}")
            st.markdown("**Skills:**")
            for s, lvl in p["skills"].items():
                st.markdown(f"• **{s}** → {lvl}")

        # if st.session_state.jobs_df.empty:
        #     st.error("No jobs loaded – check jobs.docx")
        # else:
        #     jobs_copy = st.session_state.jobs_df.copy()
        #     jobs_copy["match_score"] = jobs_copy.apply(
        #         lambda row: calculate_match_score(p, row), axis=1
        #     )
        #     sorted_jobs = jobs_copy.sort_values("match_score", ascending=False)

        #     st.subheader("Top 10 Matches")
        #     top_10 = sorted_jobs.head(10)
        #     for _, job in top_10.iterrows():
        #         with st.expander(f"{job['company']} – {job['role']}  ({job['match_score']}%)"):
        #             st.write("**Required skills:** " +
        #                      ", ".join(job.get("skills", [])))
        #             st.write("**Culture:** " +
        #                      ", ".join(job.get("culture", [])))
        #             st.write("**Personality:** " +
        #                      ", ".join(job.get("personality", [])))
        #             st.write("**Character:** " +
        #                      ", ".join(job.get("character", [])))

        #     remaining = sorted_jobs.iloc[10:]

        #     if not remaining.empty:
        #         button_text = "Hide remaining jobs" if st.session_state.show_remaining_jobs else f"See more jobs ({len(remaining)} more)"
        #         if st.button(button_text, type="secondary", use_container_width=True):
        #             st.session_state.show_remaining_jobs = not st.session_state.show_remaining_jobs
        #             st.rerun()

        #         if st.session_state.show_remaining_jobs:
        #             st.subheader(
        #                 f"All Remaining Roles ({len(remaining)} positions)")
        #             for _, job in remaining.iterrows():
        #                 with st.expander(f"{job['company']} – {job['role']}  ({job['match_score']}%)"):
        #                     st.write("**Required skills:** " +
        #                              ", ".join(job.get("skills", [])))
        #                     st.write("**Culture:** " +
        #                              ", ".join(job.get("culture", [])))
        #                     st.write("**Personality:** " +
        #                              ", ".join(job.get("personality", [])))
        #                     st.write("**Character:** " +
        #                              ", ".join(job.get("character", [])))
        #     else:
        #         st.caption("No additional jobs beyond the top 10.")
