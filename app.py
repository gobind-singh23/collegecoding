import streamlit as st

# Set page config
st.set_page_config(page_title="CollegeCoding App", layout="wide")

# Sidebar for page selection
page = st.sidebar.radio("Select a page", ["Ask me anything...", "Analyzeee Dataaa"])

# Page 1: College Rankings
if page == "Ask me anything...":
    st.title("What do you want to know?")
    st.write("This page will display college vs college comparison.")

# Page 2: User Rankings
elif page == "Analyzeee Dataaa":
    st.title("Analyzeee Dataaa")
    st.write("This page will display user-wise rankings inside colleges.")
