import streamlit as st
import json
import time # Not strictly needed with SQLite but can be kept for future
from data_manager import get_all_subjects, add_subject # These now call local data_manager

DEFAULT_SYLLABUS_PATH = "data/syllabus.json"

# Removed db_instance from signature, only app_id is passed (dummy for consistency)
def render_admin_dashboard(app_id):
    st.header("Admin Dashboard - Manage Syllabus")

    st.subheader("Current Syllabus")
    subjects = get_all_subjects() # Call get_all_subjects without arguments (SQLite handled internally)

    if not subjects:
        st.write("No subjects available in database. The default syllabus might not have loaded or was cleared.")
        if st.button("Load Default Syllabus (from data/syllabus.json)", key="load_default_syllabus"):
            # This button can be used for manual re-load.
            # The initialize_db() in data_manager already calls load_default_syllabus_into_db()
            # if the subjects table is empty, so this is mostly for recovery/manual trigger.
            st.info("Attempting to load default syllabus from `data/syllabus.json`...")
            # Calling initialize_db again will trigger the load_default_syllabus_into_db() if subjects table is empty
            from data_manager import initialize_db # Import again to explicitly call
            initialize_db()
            st.success("Attempted to load default syllabus. Please refresh the page or restart the app to see changes if they weren't already loaded.")
            st.rerun() # Force a rerun to re-check subjects
    
    # Display subjects only if there are any
    for subject in subjects:
        with st.expander(f"**{subject.get('name', 'Unnamed Subject')}** (Due: {subject.get('due_date', 'N/A')})"):
            if subject.get('topics'):
                st.markdown("##### Topics:")
                for topic in subject['topics']:
                    st.markdown(f"- {topic}")
            else:
                st.markdown("No topics listed for this subject.")

    st.subheader("Add New Subject")
    subject_name = st.text_input("Subject Name", key="admin_subject_name")
    topics = st.text_input("Topics (comma-separated)", key="admin_topics")
    due_date = st.date_input("Due Date", key="admin_due_date")
    if st.button("Add Subject", key="admin_add_subject_button"):
        if subject_name and topics:
            topics_list = [topic.strip() for topic in topics.split(",") if topic.strip()]
            success = add_subject(subject_name.strip(), topics_list, str(due_date)) # Call add_subject without db_instance/app_id
            if success:
                st.success(f"Subject '{subject_name}' added successfully! 🎉")
                st.rerun() # Trigger a rerun to update the displayed list
            else:
                st.error("Failed to add subject. Please check console/terminal for errors. 😥")
        else:
            st.error("Please enter a subject name and at least one topic. 😅")
