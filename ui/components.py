import streamlit as st

def load_css():
    with open("ui/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def card(title, content):
    st.markdown(f"""
    <div class="card">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def metrics(a, b, c):
    col1, col2, col3 = st.columns(3)
    col1.metric("Metric A", a)
    col2.metric("Metric B", b)
    col3.metric("Metric C", c)