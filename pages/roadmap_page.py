# pages/roadmap_page.py
import streamlit as st
from data_manager import get_all_subjects, get_tasks
from collections import defaultdict

def render_roadmap_page(user_id):
    """
    Renders the Academic Progress Roadmap, visualizing subject and topic progress.
    """
    # REMOVED: st.title("🗺️ Academic Progress Roadmap")
    # REMOVED: st.subheader(f"Your personalized learning journey for User: `{user_id}`")
    st.write("Track your subjects and topics here. Progress is automatically calculated based on your completed tasks that are linked to specific topics!")

    # Fetch subjects and tasks for the current user
    user_subjects = get_all_subjects(user_id)
    user_tasks = get_tasks(user_id)

    if not user_subjects:
        st.info("You haven't added any subjects to your roadmap yet. Visit the Admin Dashboard to add some!")
        return

    # Organize tasks by subject and topic for easy lookup
    topic_completion_status = defaultdict(lambda: defaultdict(bool)) # {subject_name: {topic_name: is_completed}}

    for task in user_tasks:
        if task.get('completed') and task.get('subject_name') and task.get('topic_name'):
            subject_name = task['subject_name']
            topic_name = task['topic_name']
            topic_completion_status[subject_name][topic_name] = True

    # Render the roadmap
    for subject in user_subjects:
        subject_name = subject['name']
        topics = subject.get('topics', [])

        completed_topics_count = 0
        
        # Determine how many topics within this subject have been "completed" via tasks
        for topic in topics:
            if topic_completion_status[subject_name][topic]:
                completed_topics_count += 1
        
        total_topics = len(topics)
        
        if total_topics > 0:
            progress_percentage = (completed_topics_count / total_topics) * 100
        else:
            progress_percentage = 0 # No topics means 0% progress, or can be 100% if considered 'done'

        st.markdown(f"### {subject_name}")
        
        if total_topics == 0:
            st.info(f"No topics defined for {subject_name} yet. Add some in the Admin Dashboard!")
            st.progress(0, text=f"No topics (0/0)")
        else:
            st.progress(int(progress_percentage), text=f"Progress: {completed_topics_count}/{total_topics} topics completed")

        with st.expander(f"View Topics for {subject_name}"):
            if topics:
                for topic in topics:
                    status_icon = "✅" if topic_completion_status[subject_name][topic] else "⏳"
                    st.markdown(f"- {status_icon} {topic}")
                if progress_percentage == 100 and total_topics > 0:
                    st.balloons() # Celebrate subject completion
            else:
                st.info("No topics defined for this subject.")
        
        st.markdown("---") # Separator for subjects
