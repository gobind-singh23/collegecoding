# rankings.py
import streamlit as st

st.set_page_config(page_title="Rankings", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "rankings"

st.title("Rankings")

if st.button("Go to Home"):
    st.session_state.page = "home"
    st.experimental_rerun()

ranking_type = st.radio("Select Ranking Type", ["College vs College", "User vs User"], horizontal=True)

st.sidebar.header("Filters")

if ranking_type == "College vs College":
    st.sidebar.write("College Filters here (e.g., Max Rating, Last 10 Contests)")
    st.write("Displaying College vs College rankings...")

elif ranking_type == "User vs User":
    st.sidebar.write("User Filters here (e.g., Rating, Tags, Div)")
    st.write("Displaying User vs User rankings...")
