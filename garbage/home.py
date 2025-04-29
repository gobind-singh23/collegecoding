import streamlit as st

st.set_page_config(page_title="Codeforces Analytics App", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "home"

st.title("Codeforces Analytics App")

if st.button("Go to Rankings"):
    st.session_state.page = "rankings"
    st.experimental_rerun()

st.write("Welcome to the Codeforces Analytics App!")