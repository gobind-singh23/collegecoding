import streamlit as st
from college_map import _canonical_map
import os
import json
import pandas as pd
def load_all_data(data_folder="database"):
    all_data = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".json"):
            with open(os.path.join(data_folder, filename), "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    all_data.extend(data)  # or all_data.append(data) if it's a dict
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    return all_data


# Main app
def main():
    # Set page configuration
    data=load_all_data()
    st.set_page_config(
        page_title="CodeForces Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state for navigation
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    # Initialize session state for filters
    if "crazy_selected" not in st.session_state:
        st.session_state.crazy_selected = False
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.session_state.page = "home"
    if st.sidebar.button("Compare"):
        st.session_state.page = "compare"
    
    # Display selected page
    if st.session_state.page == "home":
        st.title("CodeForces Analytics Dashboard - Home Page")
        st.write("This is the home page. Content will be added later.")
        
    elif st.session_state.page == "compare":
        st.title("CodeForces Comparison Page")
        
        # Create two columns - sidebar for filters and main content for results
        filter_col, results_col = st.columns([1, 3])
        
        # Filters in the left column

        with filter_col:
            st.header("Filters")
            
            # Comparison type selection
            comparison_type = st.radio("Comparison Type", ["User vs User", "College vs College"])
            
            # College filter for User vs User comparison - now multiselect
            if comparison_type == "User vs User":
                # Mock college list - replace with actual data later
                college_options =list(_canonical_map.keys())
                college_options.append("All")
                selected_colleges = st.multiselect(
                    "Filter by Colleges",
                    options=college_options,
                    default=["All"]
                )
                
                # Logic to handle "All" selection
                if "All" in selected_colleges and len(selected_colleges) > 1:
                    # If "All" and other options are selected, remove the other options
                    selected_colleges = ["All"]
                    st.warning("When 'All' is selected, other college options are ignored.")
            
            # Crazy features - moved up to handle filter clearing
            st.subheader("Crazy Features")
            
            # Create callback for crazy feature selection
            def on_crazy_feature_change():
                # Set flag to clear other filters
                st.session_state.crazy_selected = True
            
            crazy_feature = st.selectbox(
                "Select Feature",
                options=[
                    "None",
                    "Top 10 in last N contests",
                    "Most active coder/college",
                    "Rising stars",
                    "Last contest speed",
                    "Tag based problem rankings"
                ],
                index=0,  # Default to "None"
                on_change=on_crazy_feature_change
            )
            
            # Check if a crazy feature is selected (not "None")
            is_crazy_selected = crazy_feature != "None"
            
            # Additional parameters based on selected crazy feature
            if crazy_feature == "Top 10 in last N contests":
                top_n_contests = st.number_input(
                    "Number of contests",
                    min_value=1,
                    max_value=50,
                    value=5,
                    step=1
                )
            
            elif crazy_feature == "Rising stars":
                time_period = st.selectbox(
                    "Time period",
                    options=["Last month", "Last 3 months", "Last 6 months", "Last year"]
                )
                
            elif crazy_feature == "Tag based problem rankings":
                tag_for_ranking = st.selectbox(
                    "Select tag for ranking",
                    options=["Greedy", "DP", "Graphs", "Sorting", "Math"]
                )
            
            # Only show other filters if no crazy feature is selected
            if not is_crazy_selected:
                # Formula filters
                st.subheader("Formula Filters")
                
                # Rating filter (single option)
                formula_option = st.selectbox(
                    "Formula",
                    options=["rating", "maxRating"]
                )
                
                # Tag filter
                tag_options = ["Greedy", "DP", "Graphs", "Sorting", "Math"]
                selected_tags = st.multiselect(
                    "Problem Tags",
                    options=tag_options,
                    default=[]
                )
                
                # Contest filters
                st.subheader("Contest Filters")
                
                # Last N contests
                last_n_contests = st.number_input(
                    "Last N Contests",
                    min_value=1,
                    max_value=200,
                    value=10,
                    step=1
                )
                
                # Only Div K with None option
                div_k_options = ["None", "1", "2", "3", "4"]
                div_k = st.selectbox(
                    "Only Div K",
                    options=div_k_options,
                    index=0  # Default to "None"
                )
            else:
                # If crazy feature is selected, hide other filters but initialize variables
                formula_option = "rating"
                selected_tags = []
                last_n_contests = 10
                div_k = "None"
            
            # Apply filters button
            apply_filters = st.button("Apply Filters")
        
        # Results display in the right column
        with results_col:
            st.header("Results")
            
            if comparison_type == "User vs User":
                st.subheader("User vs User Comparison")
                if selected_colleges !=["All"]:
                    # Filter data based on selected colleges
                    data = [user for user in data if user.get("college") in selected_colleges]
                if(formula_option=="rating"):
                    data=sorted(data, key=lambda u: u.get("rating", 0), reverse=True)      
                elif(formula_option=="maxRating"):
                    data=sorted(data, key=lambda u: u.get("maxRating", 0), reverse=True)           
                # st.write("User comparison results will appear here after filtering")
                # # Placeholder for demonstration
                # st.info("Selected Filters:")
                # st.write(f"- Colleges: {', '.join(selected_colleges)}")
                #  if is_crazy_selected:
                #     st.write(f"- Crazy Feature: {crazy_feature}")
                    
                #     # Display additional parameters for crazy features
                #     if crazy_feature == "Top 10 in last N contests":
                #         st.write(f"  - Number of contests: {top_n_contests}")
                #     elif crazy_feature == "Rising stars":
                #         st.write(f"  - Time period: {time_period}")
                #     elif crazy_feature == "Tag based problem rankings":
                #         st.write(f"  - Tag for ranking: {tag_for_ranking}")
                # else:
                #     st.write(f"- Formula: {formula_option}")
                #     st.write(f"- Tags: {', '.join(selected_tags) if selected_tags else 'None'}")
                #     st.write(f"- Last {last_n_contests} Contests")
                #     st.write(f"- Div: {div_k}")
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.subheader("College vs College Comparison")
                # st.write("College comparison results will appear here after filtering")
                
                # # Placeholder for demonstration
                # st.info("Selected Filters:")
                
                # if is_crazy_selected:
                #     st.write(f"- Crazy Feature: {crazy_feature}")
                    
                #     # Display additional parameters for crazy features
                #     if crazy_feature == "Top 10 in last N contests":
                #         st.write(f"  - Number of contests: {top_n_contests}")
                #     elif crazy_feature == "Rising stars":
                #         st.write(f"  - Time period: {time_period}")
                #     elif crazy_feature == "Tag based problem rankings":
                #         st.write(f"  - Tag for ranking: {tag_for_ranking}")
                # else:
                #     st.write(f"- Formula: {formula_option}")
                #     st.write(f"- Tags: {', '.join(selected_tags) if selected_tags else 'None'}")
                #     st.write(f"- Last {last_n_contests} Contests")
                #     st.write(f"- Div: {div_k}")

if __name__ == "__main__":
    main()