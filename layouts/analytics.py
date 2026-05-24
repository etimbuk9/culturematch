from collections import Counter
import streamlit as st
import plotly.graph_objects as go

from core.rag_merger import JobFit


def show():
    st.title("🎯 Talent-Company Match Analytics")

    profile = st.session_state.get("student_profile")
    matches: list = st.session_state.get("company_jobs")

    if not profile or not matches:
        st.warning(
            "No live match data found. Please complete your profile and run the Match Engine first.")

        if st.checkbox("Show Demo Analytics (Demonstration Mode)"):
            demo = get_demo_data()
            tab1, tab2 = st.tabs(
                ["📋 Individual Analysis", "📊 Cross-Job Comparison"])
            with tab1:
                render_visuals(demo, is_demo=True)
            with tab2:
                render_comparison(demo, is_demo=True)
        return

    tab1, tab2 = st.tabs(
        ["📋 Individual Analysis", "📊 Cross-Job Comparison"])
    with tab1:
        render_visuals(matches)
    with tab2:
        render_comparison(matches)


def render_visuals(matches_data, is_demo=False):
    st.markdown("""
    <style>
    .job-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 4px;
        color: white;
    }
    .job-title { font-size: 1.5rem; font-weight: 700; margin: 0; letter-spacing: -0.3px; }
    .score-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        margin-top: 10px;
    }
    .pill-high { background: rgba(0,204,150,0.2); color: #00CC96; border: 1px solid #00CC96; }
    .pill-mid  { background: rgba(255,165,0,0.2);  color: #FFA500; border: 1px solid #FFA500; }
    .pill-low  { background: rgba(239,85,59,0.2);  color: #EF553B; border: 1px solid #EF553B; }

    .sub-card {
        border-radius: 12px;
        padding: 16px 12px;
        text-align: center;
        border-top: 4px solid;
        background: #f8f9fc;
    }
    .sub-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.9px;
        color: #777;
        margin-bottom: 6px;
    }
    .sub-value { font-size: 1.7rem; font-weight: 700; }

    .insight-card {
        background: linear-gradient(135deg, #f0f4ff, #eaf0fe);
        border-radius: 14px;
        padding: 22px 24px;
        border-left: 5px solid #636EFA;
        height: 100%;
        box-sizing: border-box;
    }
    .insight-eyebrow {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #636EFA;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .insight-text { color: #2c2c3e; line-height: 1.65; font-size: 0.93rem; }

    .section-eyebrow {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        color: #999;
        margin: 24px 0 6px;
    }

    .skill-chip {
        display: inline-block;
        padding: 5px 13px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 3px 4px 3px 0;
    }
    .chip-match { background: rgba(0,204,150,0.12); color: #00916e; border: 1px solid rgba(0,204,150,0.35); }
    .chip-gap   { background: rgba(255,165,0,0.12);  color: #b97400; border: 1px solid rgba(255,165,0,0.35); }
    .chip-empty { color: #aaa; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

    if is_demo:
        st.info("💡 Currently viewing Demonstration Data.")

    job_options = [m.job_title for m in matches_data]
    selected_job = st.selectbox("Select a role to analyse:", job_options)
    current_match = next(m for m in matches_data if m.job_title == selected_job)

    score = float(current_match.fit_score)
    pill_cls = "pill-high" if score >= 70 else ("pill-mid" if score >= 50 else "pill-low")
    match_label = "Strong Match" if score >= 70 else ("Moderate Match" if score >= 50 else "Weak Match")

    # Header banner
    st.markdown(f"""
    <div class="job-header">
        <div class="job-title">{current_match.job_title}</div>
        <span class="score-pill {pill_cls}">{score:.1f} &nbsp;·&nbsp; {match_label}</span>
    </div>
    """, unsafe_allow_html=True)

    # Sub-score tiles
    sub_scores = [
        ("Skills",       current_match.skills_alignment_score,       "#636EFA"),
        ("Culture",      current_match.culture_alignment_score,      "#EF553B"),
        ("Personality",  current_match.personality_alignment_score,  "#00CC96"),
        ("Character",    current_match.character_alignment_score,    "#AB63FA"),
    ]
    cols = st.columns(4)
    for col, (label, val, color) in zip(cols, sub_scores):
        with col:
            st.markdown(f"""
            <div class="sub-card" style="border-color:{color};">
                <div class="sub-label">{label}</div>
                <div class="sub-value" style="color:{color};">{val:.0f}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gauge + AI insight side by side
    col_g, col_i = st.columns([1, 2])

    with col_g:
        bar_color = "#00CC96" if score >= 70 else ("#FFA500" if score >= 50 else "#EF553B")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': '#ccc'},
                'bar': {'color': bar_color, 'thickness': 0.28},
                'bgcolor': 'rgba(0,0,0,0)',
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 50],  'color': 'rgba(239,85,59,0.07)'},
                    {'range': [50, 70], 'color': 'rgba(255,165,0,0.07)'},
                    {'range': [70, 100],'color': 'rgba(0,204,150,0.07)'},
                ],
            },
            number={'font': {'size': 40, 'color': '#222'}}
        ))
        fig_gauge.update_layout(
            height=230,
            margin=dict(l=16, r=16, t=36, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_i:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-eyebrow">🤖 &nbsp;AI Insight</div>
            <div class="insight-text">{current_match.reasoning}</div>
        </div>
        """, unsafe_allow_html=True)

    # Radar chart
    st.markdown('<div class="section-eyebrow">📊 &nbsp;Multi-Dimensional Alignment</div>',
                unsafe_allow_html=True)

    categories = ['Technical Skills', 'Company Culture', 'Personality', 'Character']
    alignment_values = [
        current_match.skills_alignment_score,
        current_match.culture_alignment_score,
        current_match.personality_alignment_score,
        current_match.character_alignment_score,
    ]
    fig_radar = go.Figure(data=go.Scatterpolar(
        r=alignment_values,
        theta=categories,
        fill='toself',
        name='Alignment',
        line_color='#636EFA',
        fillcolor='rgba(99,110,250,0.12)',
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(0,0,0,0.08)'),
            angularaxis=dict(gridcolor='rgba(0,0,0,0.08)'),
            bgcolor='rgba(248,249,252,0.6)',
        ),
        showlegend=False,
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # Skill gap
    st.markdown('<div class="section-eyebrow">🔍 &nbsp;Skill Gap Analysis</div>',
                unsafe_allow_html=True)

    student_profile = st.session_state.get("student_profile", {})
    student_skills = set(student_profile.get("skills", {}).keys())
    job_skills = set(current_match.required_skills)
    matched = student_skills.intersection(job_skills)
    gaps = job_skills - student_skills

    col_m, col_g2 = st.columns(2)

    with col_m:
        st.markdown("**✅ Strengths**")
        if matched:
            st.markdown(
                "".join(f'<span class="skill-chip chip-match">{s}</span>' for s in sorted(matched)),
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<span class="chip-empty">No exact skill matches found.</span>',
                        unsafe_allow_html=True)

    with col_g2:
        st.markdown("**⚠️ Growth Areas**")
        if gaps:
            st.markdown(
                "".join(f'<span class="skill-chip chip-gap">{g}</span>' for g in sorted(gaps)),
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<span class="chip-empty">You meet all technical requirements.</span>',
                        unsafe_allow_html=True)


def render_comparison(matches_data, is_demo=False):
    if is_demo:
        st.info("💡 Currently viewing Demonstration Data.")

    titles = [m.job_title for m in matches_data]
    fit_scores = [m.fit_score for m in matches_data]
    skills_scores = [m.skills_alignment_score for m in matches_data]
    culture_scores = [m.culture_alignment_score for m in matches_data]
    personality_scores = [m.personality_alignment_score for m in matches_data]
    character_scores = [m.character_alignment_score for m in matches_data]

    # --- PANEL A: Overall Fit Score Ranking ---
    st.subheader("🏆 Overall Fit Score Ranking")

    sorted_pairs = sorted(zip(fit_scores, titles), reverse=True)
    s_scores, s_titles = zip(*sorted_pairs)
    bar_colors = [
        "#00CC96" if s >= 70 else ("#FFA500" if s >= 50 else "#EF553B")
        for s in s_scores
    ]

    fig_rank = go.Figure(go.Bar(
        x=list(s_scores),
        y=list(s_titles),
        orientation='h',
        marker_color=bar_colors,
        text=[f"{s:.1f}" for s in s_scores],
        textposition='outside',
    ))
    fig_rank.update_layout(
        xaxis=dict(range=[0, 110], title="Fit Score"),
        yaxis=dict(autorange="reversed"),
        height=max(200, 60 * len(titles)),
        margin=dict(l=10, r=40, t=20, b=40),
        showlegend=False,
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    st.divider()

    # --- PANEL B: Heatmap ---
    st.subheader("🔬 Dimension Deep-Dive")
    dimensions = ["Skills", "Culture", "Personality", "Character"]
    z = [
        skills_scores,
        culture_scores,
        personality_scores,
        character_scores,
    ]
    fig_heat = go.Figure(go.Heatmap(
        z=z,
        x=titles,
        y=dimensions,
        colorscale='RdYlGn',
        zmin=40, zmax=100,
        text=[[f"{v:.0f}" for v in row] for row in z],
        texttemplate="%{text}",
        showscale=True,
    ))
    fig_heat.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=60),
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()

    # --- PANELS E & F: Bubble + Skill Frequency ---
    st.subheader("🎯 Skills & Culture Trade-off  |  📚 Skill Demand")
    col_e, col_f = st.columns(2)

    with col_e:
        st.markdown("**Skills vs Culture Bubble Chart**")
        bubble_sizes = [max(10, s * 0.6) for s in fit_scores]
        fig_bubble = go.Figure(go.Scatter(
            x=skills_scores,
            y=culture_scores,
            mode='markers+text',
            text=[t.split()[0] for t in titles],
            textposition='top center',
            marker=dict(
                size=bubble_sizes,
                color=fit_scores,
                colorscale='RdYlGn',
                colorbar=dict(title="Fit"),
                showscale=True,
                line=dict(width=1, color='white'),
            ),
            hovertext=[
                f"{t}<br>Fit: {f:.1f}<br>Skills: {sk:.1f}<br>Culture: {c:.1f}"
                for t, f, sk, c in zip(titles, fit_scores, skills_scores, culture_scores)
            ],
            hoverinfo='text',
        ))
        fig_bubble.update_layout(
            xaxis=dict(title="Skills Alignment", range=[0, 105]),
            yaxis=dict(title="Culture Alignment", range=[0, 105]),
            height=360,
            margin=dict(l=10, r=10, t=10, b=40),
        )
        st.plotly_chart(fig_bubble, use_container_width=True)

    with col_f:
        st.markdown("**Most In-Demand Skills Across All Roles**")
        all_skills = [s for m in matches_data for s in m.required_skills]
        if all_skills:
            counts = Counter(all_skills).most_common(15)
            skill_names, skill_counts = zip(*counts)
            fig_freq = go.Figure(go.Bar(
                x=list(skill_counts),
                y=list(skill_names),
                orientation='h',
                marker_color='#636EFA',
                text=list(skill_counts),
                textposition='outside',
            ))
            fig_freq.update_layout(
                height=360,
                margin=dict(l=10, r=40, t=10, b=20),
                xaxis=dict(title="Roles Requiring This Skill"),
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            )
            st.plotly_chart(fig_freq, use_container_width=True)
        else:
            st.write("No required skills data available.")


def get_demo_data():
    return [
        JobFit(
            job_title="Embedded Systems Engineer",
            fit_score=82.5,
            skills_alignment_score=90.0,
            culture_alignment_score=70.0,
            personality_alignment_score=75.0,
            character_alignment_score=85.0,
            reasoning="You are a strong match because of your VHDL expertise and proactive character traits.",
            required_skills=["VHDL", "C++", "RTOS", "FPGA", "Python"],
        ),
        JobFit(
            job_title="IoT Developer",
            fit_score=76.0,
            skills_alignment_score=80.0,
            culture_alignment_score=78.0,
            personality_alignment_score=70.0,
            character_alignment_score=74.0,
            reasoning="Your Python and networking knowledge make you a solid fit for IoT development.",
            required_skills=["Python", "MQTT", "C++", "Linux", "REST APIs"],
        ),
        JobFit(
            job_title="Firmware Engineer",
            fit_score=68.0,
            skills_alignment_score=72.0,
            culture_alignment_score=60.0,
            personality_alignment_score=65.0,
            character_alignment_score=70.0,
            reasoning="You have relevant C++ experience but may need to develop deeper RTOS knowledge.",
            required_skills=["C", "C++", "RTOS", "Debugging", "Git"],
        ),
        JobFit(
            job_title="Hardware Design Engineer",
            fit_score=55.0,
            skills_alignment_score=50.0,
            culture_alignment_score=60.0,
            personality_alignment_score=58.0,
            character_alignment_score=52.0,
            reasoning="This role requires deeper analogue circuit expertise than your current profile shows.",
            required_skills=["VHDL", "Verilog", "PCB Design", "SPICE", "FPGA"],
        ),
        JobFit(
            job_title="Robotics Software Engineer",
            fit_score=71.0,
            skills_alignment_score=68.0,
            culture_alignment_score=80.0,
            personality_alignment_score=73.0,
            character_alignment_score=65.0,
            reasoning="Your innovative risk-taker personality is a great cultural fit for the robotics team.",
            required_skills=["Python", "ROS", "C++", "Computer Vision", "Linux"],
        ),
    ]
