import streamlit as st

def show():
    st.markdown("""
        <div style='text-align: center; padding: 80px 20px; background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; border-radius: 16px; margin-bottom: 40px;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 16px; font-weight: 700;'>CultureMatch</h1>
            <h3 style='font-size: 1.6rem; opacity: 0.95; max-width: 800px; margin: 0 auto 32px;'>
                Connecting exceptional talent with forward-thinking companies through skills, culture, and personality alignment.
            </h3>
            <div style='display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;'>
                <a href='#student' style='text-decoration: none;'>
                    <div style='background: white; color: #1e40af; padding: 16px 36px; border-radius: 50px; font-weight: bold; font-size: 1.1rem; box-shadow: 0 4px 14px rgba(0,0,0,0.15); transition: all 0.3s;'>
                        I'm a Student
                    </div>
                </a>
                <a href='#company' style='text-decoration: none;'>
                    <div style='background: #1e40af; color: white; padding: 16px 36px; border-radius: 50px; font-weight: bold; font-size: 1.1rem; box-shadow: 0 4px 14px rgba(0,0,0,0.2); transition: all 0.3s;'>
                        I'm a Company
                    </div>
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Two-column value proposition
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🎓 For Students")
        st.markdown("""
        - Build a rich profile showcasing your **skills**, **CGPA**, **culture fit**, and **personality**
        - Get matched with roles that truly align with who you are — not just your resume
        - Discover companies where you’ll thrive long-term
        - Stand out with detailed experience levels and traits
        """)
        st.button("→ Create Your Profile", type="primary", use_container_width=True, key="to_student")

    with col_right:
        st.markdown("### 🏢 For Companies")
        st.markdown("""
        - Post roles with precise requirements for **skills**, **culture**, **personality**, and **character**
        - Find candidates who match not only technically but also culturally and behaviorally
        - Reduce turnover by hiring people who fit your team’s DNA
        - Access a growing pool of high-potential talent
        """)
        st.button("→ Start Posting Jobs", type="primary", use_container_width=True, key="to_company")

    # Stats bar
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Active Students", "2,400+", "↑ 18% this month")
    col2.metric("Open Roles", "780+", "↑ 24% this month")
    col3.metric("Match Success Rate", "87%", "↑ 12% this year")

    # Footer-like call to action
    st.markdown(
        """
        <div style='text-align: center; padding: 60px 20px; background: #f8fafc; border-radius: 16px; margin-top: 60px;'>
            <h2 style='color: #1e40af; margin-bottom: 24px;'>Ready to find the perfect match?</h2>
            <p style='font-size: 1.2rem; color: #4b5563; max-width: 700px; margin: 0 auto 32px;'>
                Whether you're a student looking for your dream opportunity or a company seeking exceptional talent — CultureMatch is built for you.
            </p>
            <div style='display: flex; justify-content: center; gap: 24px; flex-wrap: wrap;'>
                <div style='background: #1e40af; color: white; padding: 16px 40px; border-radius: 50px; font-weight: bold; cursor: pointer;'>
                    Get Started — It's Free
                </div>
                <div style='border: 2px solid #1e40af; color: #1e40af; padding: 16px 40px; border-radius: 50px; font-weight: bold; cursor: pointer;'>
                    Learn How It Works
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )