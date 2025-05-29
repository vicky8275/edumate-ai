import streamlit as st
from data_manager import get_all_subjects, save_json  # Add save_json to imports

def render_admin_dashboard():
    st.header("Admin Dashboard - Manage Syllabus")
    subjects = get_all_subjects()

    st.subheader("Current Syllabus")
    if not subjects:
        st.write("No subjects available.")
    for subject in subjects:
        st.write(f"{subject['name']}: {', '.join(subject['topics'])} (Due: {subject['due_date']})")

    st.subheader("Add New Subject")
    subject_name = st.text_input("Subject Name")
    topics = st.text_input("Topics (comma-separated)")
    due_date = st.date_input("Due Date")
    if st.button("Add Subject"):
        if subject_name and topics:
            topics_list = [topic.strip() for topic in topics.split(",")]
            subjects.append({"name": subject_name, "topics": topics_list, "due_date": str(due_date)})
            save_json("data/syllabus.json", subjects)  # Now save_json is defined
            st.success("Subject added successfully!")
        else:
            st.error("Please enter a subject name and at least one topic.")