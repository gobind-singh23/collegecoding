import streamlit as st
from college_map import _canonical_map
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

def plot_rating_histogram(data):
    """
    data: list of user‐dicts with a 'rating' key
    """
    ratings = [u.get("rating", 0) for u in data]
    if not ratings:
        st.warning("No ratings to plot.")
        return

    fig, ax = plt.subplots()
    ax.hist(ratings, bins=20, color="#4c72b0", edgecolor="white")
    ax.set_title("Distribution of User Ratings")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Users")
    st.pyplot(fig)

def plot_max_rating_histogram(data):
    """
    data: list of user‐dicts with a 'rating' key
    """
    ratings = [u.get("maxRating", 0) for u in data]
    if not ratings:
        st.warning("No ratings to plot.")
        return

    fig, ax = plt.subplots()
    ax.hist(ratings, bins=20, color="#4c72b0", edgecolor="white")
    ax.set_title("Distribution of User Ratings")
    ax.set_xlabel("Max Rating")
    ax.set_ylabel("Number of Users")
    st.pyplot(fig)

def load_all_data(data_folder="database"):
    all_data = []
    for filename in os.listdir(data_folder):
        if filename.endswith(".json") and "users" in filename:
            filepath = os.path.join(data_folder, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    elif isinstance(data, dict):
                        all_data.append(data)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    return all_data

def load_tag_data(data_folder="database"):
    tag_file = os.path.join(data_folder, "coding_platform.tags.json")
    try:
        with open(tag_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading tag data: {e}")
        return []

def rank_users_by_selected_tags(user_data, tag_data, selected_tags):
    if not selected_tags:
        return user_data  # no tags selected, return original data

    # Create a map from userId to user for faster lookup
    user_map = {user.get("handle", ""): user for user in user_data}
    
    # Map for converting display tag names to database field names
    tag_name_map = {
        "brute force": "brute_force",
        "data structures": "data_structures",
        "binary search": "binary_search",
        "constructive algorithms": "constructive_algorithms",
        "dfs and similar": "dfs_and_similar",
        "dp": "dp",
        "greedy": "greedy",
        "implementation": "implementation",
        "math": "math",
        "sorting": "sorting"
    }
    
    # Calculate tag scores for each user
    for user in user_data:
        user["_matching_tag_count"] = 0  # Initialize tag count for all users
        # Initialize individual tag counts
        for tag in selected_tags:
            tag_lower = tag.lower()
            db_field = tag_name_map.get(tag_lower, tag_lower)
            user[f"_{db_field}_count"] = 0
    
    # Process tag data
    for tag_entry in tag_data:
        user_id = tag_entry.get("userId", "")
        if user_id in user_map:
            # Sum the count of problems solved for each selected tag
            tag_sum = 0
            for tag in selected_tags:
                # Convert tag name to database field name
                tag_lower = tag.lower()
                db_field = tag_name_map.get(tag_lower, tag_lower)
                
                # Get the count from the database entry
                tag_count = tag_entry.get(db_field, 0)
                tag_sum += tag_count
                
                # Store individual tag counts for display
                user_map[user_id][f"_{db_field}_count"] = tag_count
            
            user_map[user_id]["_matching_tag_count"] = tag_sum
    
    # Sort users by their tag scores in descending order
    return sorted(user_data, key=lambda u: u.get("_matching_tag_count", 0), reverse=True)

def main():
    # Load data
    user_data = load_all_data()
    tag_data = load_tag_data()

    # Streamlit page config
    st.set_page_config(
        page_title="CodeForces Analytics",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Hide error messages
    st.set_option('client.showErrorDetails', False)

    # Session state defaults
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "crazy_selected" not in st.session_state:
        st.session_state.crazy_selected = False

    # Sidebar navigation
    st.sidebar.title("Navigation")
    if st.sidebar.button("Home"):
        st.session_state.page = "home"
    if st.sidebar.button("Compare"):
        st.session_state.page = "compare"

    # Home page
    if st.session_state.page == "home":
        st.title("CodeForces Analytics Dashboard - Home Page")
        st.write("This is the home page. Content will be added later.")

    # Compare page
    elif st.session_state.page == "compare":
        st.title("CodeForces Comparison Page")
        filter_col, results_col = st.columns([1, 3])

        with filter_col:
            st.header("Filters")
            comparison_type = st.radio("Comparison Type", ["User vs User", "College vs College"])

            # User vs User specific filters
            if comparison_type == "User vs User":
                college_options = list(_canonical_map.keys()) + ["All"]
                selected_colleges = st.multiselect(
                    "Filter by Colleges",
                    options=college_options,
                    default=["All"]
                )
                # Enforce "All" exclusivity
                if "All" in selected_colleges and len(selected_colleges) > 1:
                    selected_colleges = ["All"]
                    st.warning("When 'All' is selected, other college options are ignored.")

                # Crazy features
                st.subheader("Retrieval Type")
                def on_crazy_feature_change():
                    st.session_state.crazy_selected = True

                crazy_feature = st.selectbox(
                    "Select Feature",
                    options=[
                        "None",
                        "Top 3 from each college",
                    ],
                    index=0,
                    on_change=on_crazy_feature_change
                )
                is_crazy_selected = crazy_feature != "None"

                # Formula & other filters (hidden if a crazy feature is selected)
                if not is_crazy_selected:
                    # First show tag options since they take precedence
                    st.subheader("Problem Tags")
                    tag_options = [
                        "Greedy", 
                        "DP", 
                        "Math", 
                        "Implementation", 
                        "Brute Force", 
                        "Data Structures", 
                        "Binary Search",
                        "Constructive Algorithms",
                        "DFS and Similar"
                    ]
                    selected_tags = st.multiselect("Select Tags", options=tag_options, default=[])
                    
                    if selected_tags:
                        st.info("When problem tags are selected, users are ranked by the number of problems solved in these categories. Other filters are not applicable.")
                        # Set default values for other filters that won't be shown
                        formula_option = "rating"
                        data_ordering_option = "Descending Order"
                        candidate_title_option = "All"  # Default value, won't be used
                    else:
                        # Only show these filters if no tags are selected
                        st.subheader("Formula Filters")
                        formula_option = st.selectbox("Formula", options=["rating", "maxRating"])
                        st.subheader("Data Ordering")
                        data_ordering_option = st.selectbox("Data Ordering", options=["Ascending Order","Descending Order"])
                        st.subheader("Candidate Title")
                        candidate_title_option = st.selectbox("Candidate Title", options=["All", "Newbie", "Pupil","Specialist","Expert","Candidate Master","Master","International Master","Grandmaster"])
                else:
                    # Defaults when crazy feature is active
                    formula_option = "rating"
                    selected_tags = []
                    data_ordering_option = "Descending Order"
                    candidate_title_option = "All"  # Set default
            
            # College vs College specific filters (simplified UI)
            else:
                selected_colleges = ["All"]  # Default value
                is_crazy_selected = False    # No crazy features
                selected_tags = []           # No tags
                candidate_title_option = "All"  # Set default
                
                # Simple formula filter with rating and maxRating options
                st.subheader("Formula Filters")
                formula_option = st.selectbox("Formula", options=["Avg Rating", "Max Rating"])
                
                # Add sort order option
                st.subheader("Sort Order")
                data_ordering_option = st.selectbox("Order", options=["Descending Order","Ascending Order"])

        with results_col:
            st.header("Results")

            if comparison_type == "User vs User":
                st.subheader("User vs User Comparison")

                # College filtering
                filtered_data = user_data
                if selected_colleges != ["All"]:
                    filtered_data = [u for u in filtered_data if u.get("college") in selected_colleges]

                # Map for converting display tag names to database field names
                tag_name_map = {
                    "brute force": "brute_force",
                    "data structures": "data_structures",
                    "binary search": "binary_search",
                    "constructive algorithms": "constructive_algorithms",
                    "dfs and similar": "dfs_and_similar",
                    "dp": "dp",
                    "greedy": "greedy",
                    "implementation": "implementation",
                    "math": "math",
                    "sorting": "sorting"
                }
                
                # Map for converting database field names to display names
                db_to_display = {
                    "brute_force": "Brute Force",
                    "data_structures": "Data Structures",
                    "binary_search": "Binary Search",
                    "constructive_algorithms": "Constructive Algorithms",
                    "dfs_and_similar": "DFS and Similar",
                    "dp": "DP",
                    "greedy": "Greedy",
                    "implementation": "Implementation",
                    "math": "Math",
                    "sorting": "Sorting"
                }

                try:
                    # Crazy features logic
                    if is_crazy_selected and crazy_feature == "Top 3 from each college":
                        # Convert filtered_data to DataFrame with consistent column names
                        df_data = [{
                            "Handle": u.get("handle", ""),
                            "College": u.get("college", "Unknown"),
                            "Rating": u.get("rating", 0),
                            "Max Rating": u.get("maxRating", 0)
                        } for u in filtered_data]
                        
                        # Create DataFrame
                        df = pd.DataFrame(df_data)
                        
                        # Sort by rating or maxRating based on the selected formula
                        sort_by = "Rating" if formula_option == "rating" else "Max Rating"
                        df = df.sort_values(by=sort_by, ascending=False)
                        
                        # Group by college and get top 3 from each
                        top_users_df = df.groupby("College").head(3).reset_index(drop=True)
                        
                        # Sort by college name to keep colleges together
                        top_users_df = top_users_df.sort_values(by="College")
                        
                        # Display the DataFrame
                        st.dataframe(top_users_df)
                    
                    # Standard ranking logic
                    elif selected_tags:
                        filtered_data = rank_users_by_selected_tags(filtered_data, tag_data, selected_tags)
                        
                        # Create a DataFrame with user information and tag counts
                        display_data = []
                        
                        for user in filtered_data:
                            user_info = {
                                "Handle": user.get("handle", ""),
                                "College": user.get("college", ""),
                                "Rating": user.get("rating", 0),
                                "Max Rating": user.get("maxRating", 0),
                                "Problems Solved": user.get("_matching_tag_count", 0)  # Sum of all selected tags
                            }
                            
                            # Add individual tag counts
                            for tag in selected_tags:
                                tag_lower = tag.lower()
                                db_field = tag_name_map.get(tag_lower, tag_lower)
                                display_name = db_to_display.get(db_field, tag)
                                user_info[f"{display_name} Problems"] = user.get(f"_{db_field}_count", 0)
                            
                            display_data.append(user_info)
                        
                        df = pd.DataFrame(display_data)
                        st.dataframe(df)
                    
                    elif formula_option == "rating" and data_ordering_option=="Descending Order":
                        if candidate_title_option == "All":
                            # Show all users sorted by rating in descending order
                            filtered_data = sorted(filtered_data, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0)
                            } for u in filtered_data])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(filtered_data)
                        
                        elif candidate_title_option=="Newbie":
                            newbies = [u for u in filtered_data if int(u.get("rating", 0)) <= 1199]
                            newbies = sorted(newbies, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Newbie"
                            } for u in newbies])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(newbies)

                        elif candidate_title_option=="Pupil":
                            pupils = [u for u in filtered_data if (int(u.get("rating", 0)) <= 1399 and int(u.get("rating", 0)) >= 1200)]
                            pupils = sorted(pupils, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Pupil"
                            } for u in pupils])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(pupils)

                        elif candidate_title_option=="Specialist":
                            specialist = [u for u in filtered_data if (int(u.get("rating", 0)) <= 1599 and int(u.get("rating", 0)) >= 1400)]
                            specialist = sorted(specialist, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Specialist"
                            } for u in specialist])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(specialist)

                        elif candidate_title_option=="Expert":
                            expert = [u for u in filtered_data if (int(u.get("rating", 0)) <= 1899 and int(u.get("rating", 0)) >= 1600)]
                            expert = sorted(expert, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Expert"
                            } for u in expert])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(expert)

                        elif candidate_title_option=="Candidate Master":
                            candidate_master = [u for u in filtered_data if (int(u.get("rating", 0)) <= 2100 and int(u.get("rating", 0)) >= 1900)]
                            candidate_master = sorted(candidate_master, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Candidate Master"
                            } for u in candidate_master])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(candidate_master)

                        elif candidate_title_option=="Master":
                            master = [u for u in filtered_data if (int(u.get("rating", 0)) <= 2299 and int(u.get("rating", 0)) >= 2100)]
                            master = sorted(master, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Master"
                            } for u in master])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(master)

                        elif candidate_title_option=="International Master":
                            international_master = [u for u in filtered_data if (int(u.get("rating", 0)) <= 2399 and int(u.get("rating", 0)) >= 2300)]
                            international_master = sorted(international_master, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"International Master"
                            } for u in international_master])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(international_master)

                        elif candidate_title_option=="Grandmaster":
                            grandmaster = [u for u in filtered_data if (int(u.get("rating", 0)) >= 2400)]
                            grandmaster = sorted(grandmaster, key=lambda u: u.get("rating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Grandmaster"
                            } for u in grandmaster])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(grandmaster)
                    
                    elif formula_option == "rating" and data_ordering_option=="Ascending Order":
                        if candidate_title_option == "All":
                            # Show all users sorted by rating in ascending order
                            filtered_data = sorted(filtered_data, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0)
                            } for u in filtered_data])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(filtered_data)
                                
                        elif candidate_title_option=="Newbie":
                            newbies = [u for u in filtered_data if int(u.get("rating", 0)) <= 1199]
                            newbies = sorted(newbies, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Newbie"
                            } for u in newbies])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(newbies)

                        elif candidate_title_option=="Pupil":
                            pupils = [u for u in filtered_data if (int(u.get("rating", 0)) <= 1399 and int(u.get("rating", 0)) >= 1200)]
                            pupils = sorted(pupils, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Pupil"
                            } for u in pupils])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(pupils)

                        elif candidate_title_option=="Specialist":
                            specialist = [u for u in filtered_data if (int(u.get("rating", 0)) <= 1599 and int(u.get("rating", 0)) >= 1400)]
                            specialist = sorted(specialist, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Specialist"
                            } for u in specialist])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(specialist)

                        elif candidate_title_option=="Expert":
                            expert = [u for u in filtered_data if (int(u.get("rating", 0)) <= 1899 and int(u.get("rating", 0)) >= 1600)]
                            expert = sorted(expert, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Expert"
                            } for u in expert])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(expert)

                        elif candidate_title_option=="Candidate Master":
                            candidate_master = [u for u in filtered_data if (int(u.get("rating", 0)) <= 2100 and int(u.get("rating", 0)) >= 1900)]
                            candidate_master = sorted(candidate_master, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Candidate Master"
                            } for u in candidate_master])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(candidate_master)

                        elif candidate_title_option=="Master":
                            master = [u for u in filtered_data if (int(u.get("rating", 0)) <= 2299 and int(u.get("rating", 0)) >= 2100)]
                            master = sorted(master, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Master"
                            } for u in master])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(master)

                        elif candidate_title_option=="International Master":
                            international_master = [u for u in filtered_data if (int(u.get("rating", 0)) <= 2399 and int(u.get("rating", 0)) >= 2300)]
                            international_master = sorted(international_master, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"International Master"
                            } for u in international_master])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(international_master)

                        elif candidate_title_option=="Grandmaster":
                            grandmaster = [u for u in filtered_data if (int(u.get("rating", 0)) >= 2400)]
                            grandmaster = sorted(grandmaster, key=lambda u: u.get("rating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Grandmaster"
                            } for u in grandmaster])
                            st.dataframe(df)
                            if st.button("Show Rating Distribution"):
                                plot_rating_histogram(grandmaster)
                    
                    elif formula_option == "maxRating" and data_ordering_option=="Descending Order":
                        if candidate_title_option == "All":
                            # Show all users sorted by maxRating in descending order
                            filtered_data = sorted(filtered_data, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0)
                            } for u in filtered_data])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(filtered_data)
                                
                        elif candidate_title_option=="Newbie":
                            newbies = [u for u in filtered_data if int(u.get("maxRating", 0)) <= 1199]
                            newbies = sorted(newbies, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Newbie"
                            } for u in newbies])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(newbies)

                        elif candidate_title_option=="Pupil":
                            pupils = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 1399 and int(u.get("maxRating", 0)) >= 1200)]
                            pupils = sorted(pupils, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Pupil"
                            } for u in pupils])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(pupils)

                        elif candidate_title_option=="Specialist":
                            specialist = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 1599 and int(u.get("maxRating", 0)) >= 1400)]
                            specialist = sorted(specialist, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Specialist"
                            } for u in specialist])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(specialist)

                        elif candidate_title_option=="Expert":
                            expert = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 1899 and int(u.get("maxRating", 0)) >= 1600)]
                            expert = sorted(expert, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Expert"
                            } for u in expert])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(expert)

                        elif candidate_title_option=="Candidate Master":
                            candidate_master = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 2100 and int(u.get("maxRating", 0)) >= 1900)]
                            candidate_master = sorted(candidate_master, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Candidate Master"
                            } for u in candidate_master])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(candidate_master)
                                
                        elif candidate_title_option=="Master":
                            master = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 2299 and int(u.get("maxRating", 0)) >= 2100)]
                            master = sorted(master, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Master"
                            } for u in master])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(master)

                        elif candidate_title_option=="International Master":
                            international_master = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 2399 and int(u.get("maxRating", 0)) >= 2300)]
                            international_master = sorted(international_master, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"International Master"
                            } for u in international_master])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(international_master)

                        elif candidate_title_option=="Grandmaster":
                            grandmaster = [u for u in filtered_data if (int(u.get("maxRating", 0)) >= 2400)]
                            grandmaster = sorted(grandmaster, key=lambda u: u.get("maxRating", 0), reverse=True)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Grandmaster"
                            } for u in grandmaster])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(grandmaster)
                    
                    elif formula_option == "maxRating" and data_ordering_option=="Ascending Order":
                        if candidate_title_option == "All":
                            # Show all users sorted by maxRating in ascending order
                            filtered_data = sorted(filtered_data, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0)
                            } for u in filtered_data])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(filtered_data)
                                
                        elif candidate_title_option=="Newbie":
                            newbies = [u for u in filtered_data if int(u.get("maxRating", 0)) <= 1199]
                            newbies = sorted(newbies, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Newbie"
                            } for u in newbies])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(newbies)

                        elif candidate_title_option=="Pupil":
                            pupils = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 1399 and int(u.get("maxRating", 0)) >= 1200)]
                            pupils = sorted(pupils, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Pupil"
                            } for u in pupils])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(pupils)

                        elif candidate_title_option=="Specialist":
                            specialist = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 1599 and int(u.get("maxRating", 0)) >= 1400)]
                            specialist = sorted(specialist, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Specialist"
                            } for u in specialist])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(specialist)

                        elif candidate_title_option=="Expert":
                            expert = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 1899 and int(u.get("maxRating", 0)) >= 1600)]
                            expert = sorted(expert, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Expert"
                            } for u in expert])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(expert)

                        elif candidate_title_option=="Candidate Master":
                            candidate_master = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 2100 and int(u.get("maxRating", 0)) >= 1900)]
                            candidate_master = sorted(candidate_master, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Candidate Master"
                            } for u in candidate_master])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(candidate_master)

                        elif candidate_title_option=="Master":
                            master = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 2299 and int(u.get("maxRating", 0)) >= 2100)]
                            master = sorted(master, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Master"
                            } for u in master])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(master)

                        elif candidate_title_option=="International Master":
                            international_master = [u for u in filtered_data if (int(u.get("maxRating", 0)) <= 2399 and int(u.get("maxRating", 0)) >= 2300)]
                            international_master = sorted(international_master, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"International Master"
                            } for u in international_master])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(international_master)

                        elif candidate_title_option=="Grandmaster":
                            grandmaster = [u for u in filtered_data if (int(u.get("maxRating", 0)) >= 2400)]
                            grandmaster = sorted(grandmaster, key=lambda u: u.get("maxRating", 0), reverse=False)
                            df = pd.DataFrame([{
                                "Handle": u.get("handle", ""),
                                "College": u.get("college", ""),
                                "Rating": u.get("rating", 0),
                                "Max Rating": u.get("maxRating", 0),
                                "Candidate Title":"Grandmaster"
                            } for u in grandmaster])
                            st.dataframe(df)
                            if st.button("Show Max Rating Distribution"):
                                plot_max_rating_histogram(grandmaster)
                
                except Exception as e:
                    st.error("An error occurred while processing the data. Please try different filters.")
                    print(f"Error: {e}")

            else:
                st.subheader("College vs College Comparison")
                
                try:
                    # Filter users
                    filtered_users = user_data
                    
                    # Group users by college and calculate statistics
                    college_stats = {}
                    
                    for user in filtered_users:
                        college = user.get("college", "Unknown")
                        if college not in college_stats:
                            college_stats[college] = {
                                "College": college,
                                "User Count": 0,
                                "Total Rating": 0,
                                "Avg Rating": 0,
                                "Max Rating": 0  # Track maximum rating in each college
                            }
                        
                        college_stats[college]["User Count"] += 1
                        college_stats[college]["Total Rating"] += user.get("rating", 0)
                        
                        # Track maximum rating for each college
                        user_max_rating = user.get("maxRating", 0)
                        if user_max_rating > college_stats[college]["Max Rating"]:
                            college_stats[college]["Max Rating"] = user_max_rating
                    
                    # Calculate averages
                    for college in college_stats:
                        if college_stats[college]["User Count"] > 0:
                            college_stats[college]["Avg Rating"] = college_stats[college]["Total Rating"] / college_stats[college]["User Count"]
                    
                    # Create DataFrame and sort based on formula option and order
                    college_df = pd.DataFrame(list(college_stats.values()))
                    ascending = (data_ordering_option == "Ascending Order")
                    
                    if formula_option == "Avg Rating":
                        college_df = college_df.sort_values("Avg Rating", ascending=ascending)
                    elif formula_option == "Max Rating":
                        college_df = college_df.sort_values("Max Rating", ascending=ascending)
                    
                    st.dataframe(college_df)
                
                except Exception as e:
                    st.error("An error occurred while processing college data. Please try different filters.")
                    print(f"Error: {e}")

if __name__ == "__main__":
    main()
