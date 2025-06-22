# app.py (Student Dashboard)
import streamlit as st
from data_manager import get_tasks, add_task, mark_task_completed, delete_task, get_all_subjects, delete_subject
from productivity_tools import pomodoro_timer
from langgraph_flow import run_agent as get_urgent_reminders
from datetime import datetime

def render_student_dashboard(user_id, is_guest, app_id): # is_guest and app_id are unused here now
    """
    Renders the student dashboard with personalized tasks and syllabus.
    """
    # CRITICAL: st.set_page_config() REMOVED FROM HERE. It is now only in main.py.

    # REMOVED: st.title(f"Welcome to EduMate, User {user_id}! 🎉")
    # REMOVED: st.subheader("Your Personalized Academic Hub")

    # --- Urgent Reminders Section ---
    st.markdown("---")
    st.header("🔔 Urgent Reminders")
    
    # Placeholder for urgent reminders from LLM
    if 'urgent_reminder_displayed' not in st.session_state:
        st.session_state.urgent_reminder_displayed = False

    if not st.session_state.urgent_reminder_displayed:
        with st.spinner("Checking for urgent reminders..."):
            urgent_query = "Are there any urgent tasks or important academic reminders based on my current tasks and subjects? If so, prioritize the most urgent ones."
            
            try:
                reminder_text = get_urgent_reminders(urgent_query) 
                if reminder_text and "no urgent tasks" not in reminder_text.lower():
                    st.warning(f"**Heads up!** {reminder_text}")
                else:
                    st.success("No urgent reminders at the moment. You're doing great! ✨")
                st.session_state.urgent_reminder_displayed = True
            except Exception as e:
                st.error(f"Could not retrieve urgent reminders: {e}")
                st.session_state.urgent_reminder_displayed = True # Prevent repeated attempts

    # --- Tasks Management Section ---
    st.markdown("---")
    st.header("✅ Your Tasks")

    tasks = get_tasks(user_id)
    st.session_state.tasks = tasks

    col_add_task, col_filters = st.columns([2, 1])

    with col_add_task:
        st.subheader("Add a New Task")
        
        # --- Subject Selection (Moved OUTSIDE the form for reactivity) ---
        available_subjects_list = get_all_subjects(user_id)
        available_subjects_map = {s['name']: s for s in available_subjects_list}
        subject_names = ["(None)"] + sorted(list(available_subjects_map.keys()))
        
        # Initialize session state for the selected subject if not present
        if 'add_task_selected_subject_name' not in st.session_state:
            st.session_state.add_task_selected_subject_name = "(None)"

        # The subject selectbox itself
        st.session_state.add_task_selected_subject_name = st.selectbox(
            "Link to Subject (Optional)",
            subject_names,
            key="global_task_subject_select" # Changed key to indicate it's outside the form scope
        )

        # --- Form for Task Details and Topic Selection ---
        with st.form("new_task_form", clear_on_submit=True):
            task_description = st.text_input("Task Description")
            due_date = st.date_input("Due Date", min_value=datetime.today())
            
            # Determine available topics based on the subject selected *outside* the form
            available_topics = ["(None)"]
            if st.session_state.add_task_selected_subject_name != "(None)":
                selected_subject_obj = available_subjects_map.get(st.session_state.add_task_selected_subject_name)
                if selected_subject_obj and selected_subject_obj['topics']:
                    available_topics.extend(selected_subject_obj['topics'])
                available_topics = sorted(list(set(available_topics))) # Ensure unique and sort

            selected_topic_name = st.selectbox(
                "Link to Topic (Optional)",
                available_topics,
                key="task_topic_select" # This key is specific to the form
            )

            submitted = st.form_submit_button("Add Task")
            if submitted and task_description and due_date:
                # Set subject and topic to None if "(None)" is selected
                final_subject_name = st.session_state.add_task_selected_subject_name if st.session_state.add_task_selected_subject_name != "(None)" else None
                final_topic_name = selected_topic_name if selected_topic_name != "(None)" else None

                result = add_task(user_id, task_description, due_date.strftime("%Y-%m-%d"), 
                                  subject_name=final_subject_name, topic_name=final_topic_name)
                if result["success"]:
                    st.success("Task added successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to add task: {result['error']}")
            elif submitted:
                st.warning("Please fill in task description and due date.")

    with col_filters:
        st.subheader("Task Filters")
        task_filter = st.radio(
            "Show:",
            ("All Tasks", "Pending Tasks", "Completed Tasks"),
            key="task_filter"
        )

    st.markdown("---")

    filtered_tasks = []
    if task_filter == "Pending Tasks":
        filtered_tasks = [t for t in tasks if not t.get('completed', False)]
    elif task_filter == "Completed Tasks":
        filtered_tasks = [t for t in tasks if t.get('completed', False)]
    else:
        filtered_tasks = tasks

    if filtered_tasks:
        for i, task in enumerate(filtered_tasks):
            col_task, col_status, col_actions = st.columns([4, 2, 2])
            
            with col_task:
                display_text = f"**{task['task']}** (Due: {task['due_date']})"
                if task.get('subject_name') and task.get('topic_name'):
                    display_text += f" (Subject: {task['subject_name']}, Topic: {task['topic_name']})"
                elif task.get('subject_name'):
                    display_text += f" (Subject: {task['subject_name']})"

                if task.get('completed', False):
                    st.markdown(f"~~{display_text}~~")
                else:
                    st.markdown(display_text)

            with col_status:
                status_icon = "✅" if task.get('completed', False) else "⏳"
                st.write(f"{status_icon} {'Completed' if task.get('completed', False) else 'Pending'}")

            with col_actions:
                if not task.get('completed', False):
                    if st.button("Mark Completed", key=f"complete_{task['id']}_{i}"):
                        result = mark_task_completed(user_id, task['id'])
                        if result["success"]:
                            st.success(f"Task '{task['task']}' marked completed!")
                            st.rerun()
                        else:
                            st.error(f"Failed to mark task completed: {result['error']}")
                if st.button("Delete", key=f"delete_{task['id']}_{i}"):
                    result = delete_task(user_id, task['id'])
                    if result["success"]:
                        st.info(f"Task '{task['task']}' deleted.")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete task: {result['error']}")
        st.markdown("---")
    else:
        st.info(f"No {task_filter.lower()} found for you. Keep up the great work! ✨")

    # --- Syllabus/Subjects Section (User-Specific) ---
    st.markdown("---")
    st.header("📚 Your Academic Roadmap")
    st.write("This is your personalized syllabus. You can add subjects and topics relevant to your studies!")

    user_subjects = get_all_subjects(user_id)

    if user_subjects:
        for subject in user_subjects:
            with st.expander(f"**{subject['name']}**"):
                if subject['topics']:
                    st.write("Topics:")
                    for topic in subject['topics']:
                        st.markdown(f"- {topic}")
                else:
                    st.info("No topics added for this subject yet.")
                if st.button(f"Delete '{subject['name']}' Subject", key=f"delete_subject_{subject['id']}"):
                    result = delete_subject(user_id, subject['id'])
                    if result["success"]:
                        st.success(f"Subject '{subject['name']}' deleted successfully.")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete subject: {result['error']}")
    else:
        st.info("You haven't added any subjects to your roadmap yet. Visit the Admin Dashboard to add some!")

    # --- Productivity Tools Section ---
    st.markdown("---")
    st.header("⏰ Productivity Tools")
    st.subheader("Pomodoro Timer")
    pomodoro_timer()
