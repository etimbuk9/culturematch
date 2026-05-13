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

        draft = st.session_state.get("profile_draft", {})

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", draft.get("name", "Imadara Oku"))
            age = st.number_input("Age", min_value=18,
                                  max_value=40, value=draft.get("age", 22), step=1)
            email = st.text_input("Email Address", draft.get("email", "yourname@topfaith.edu.ng"))
            phone = st.text_input("Phone Number", draft.get("phone", "+234 "))
        with col2:
            university = st.text_input("University", draft.get("university", "Topfaith University"))

            saved_degree = draft.get("degree", "")
            degrees = master["degrees"]
            if saved_degree in degrees:
                deg_idx = degrees.index(saved_degree)
            else:
                deg_idx = degrees.index("Other (please specify)") if "Other (please specify)" in degrees else 0
            degree_choice = st.selectbox("Degree", degrees, index=deg_idx)
            if degree_choice == "Other (please specify)":
                specify_default = saved_degree if saved_degree not in degrees else ""
                degree = st.text_input("Specify degree", specify_default)
            else:
                degree = degree_choice

            grad_year = st.text_input(
                "Level / Expected Graduation Year", draft.get("grad_year", "500 Level / 2026"))
            preferred_role = st.text_input(
                "Preferred Job Role(s)", draft.get("preferred_role", "Embedded Systems Engineer, IoT Developer"))

        cgpa = st.number_input("CGPA", 0.0, 5.0, draft.get("cgpa", 4.60),
                               step=0.01, format="%.2f")

        st.markdown("---")
        st.subheader("Work Preferences & Traits")

        col_a, col_b = st.columns(2)
        with col_a:
            culture = st.multiselect(
                "Preferred Culture", master["culture"], default=draft.get("culture", ["Fast-paced"]))
            personality = st.multiselect(
                "Personality Style", master["personality"], default=draft.get("personality", ["Quick learner"]))
        with col_b:
            character = st.multiselect(
                "Character Traits", master["character"], default=draft.get("character", ["Proactive"]))

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
                saved_skills = {skill: st.session_state.skill_levels[skill] for skill in selected}
                st.session_state.skill_levels = saved_skills
                st.session_state.profile_draft = {}
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
                    "skills": saved_skills,
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
            st.session_state.profile_draft = p.copy()
            st.session_state.selected_skills = list(p["skills"].keys())
            st.session_state.skill_levels = p["skills"].copy()
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
