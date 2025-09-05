import streamlit as st
from data_manager import add_subject, get_all_subjects, delete_subject
from datetime import datetime

def render_admin_page(user_id):
    """
    Renders the admin dashboard for managing user-specific subjects.
    """
    # CRITICAL: st.set_page_config() REMOVED FROM HERE. It is now only in main.py.

    # REMOVED: st.title("⚙️ Admin Dashboard (Your Subjects)")
    # REMOVED: st.subheader(f"Manage Subjects for User: `{user_id}`")

    st.markdown("---")
    st.header("Add New Subject to Your Roadmap")

    with st.form("new_subject_form", clear_on_submit=True):
        subject_name = st.text_input("Subject Name (e.g., 'Physics', 'Calculus')")
        topics_input = st.text_area("Topics (comma-separated, e.g., 'Kinematics, Dynamics, Thermodynamics')")
        
        submitted = st.form_submit_button("Add Subject")

        if submitted and subject_name:
            topics_list = [topic.strip() for topic in topics_input.split(',') if topic.strip()]
            result = add_subject(user_id, subject_name, topics_list)
            if result["success"]:
                st.success(f"Subject '{subject_name}' added successfully!")
                st.rerun()
            else:
                st.error(f"Failed to add subject: {result['error']}")
        elif submitted:
            st.warning("Please enter a Subject Name.")
    
    st.markdown("---")
    st.header("Your Current Subjects")

    user_subjects = get_all_subjects(user_id)

    if user_subjects:
        for i, subject in enumerate(user_subjects):
            with st.container(border=True):
                st.markdown(f"#### {subject['name']}")
                if subject['topics']:
                    st.write("Topics:")
                    for topic in subject['topics']:
                        st.markdown(f"- {topic}")
                else:
                    st.info("No topics added for this subject yet.")
                
                if st.button(f"Delete Subject: {subject['name']}", key=f"delete_subject_{subject['id']}_{i}"):
                    result = delete_subject(user_id, subject['id'])
                    if result["success"]:
                        st.success(f"Subject '{subject['name']}' deleted successfully.")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete subject: {result['error']}")
    else:
        st.info("You currently have no subjects added to your roadmap. Add one above!")
