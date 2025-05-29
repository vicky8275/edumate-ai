import streamlit as st
from chatbot_agent import get_chatbot_response # Now returns a generator
from admin_dashboard import render_admin_dashboard
from data_manager import get_all_subjects, add_task, get_tasks, mark_task_completed
from productivity_tools import pomodoro_timer # Import the pomodoro_timer function
from langgraph_flow import run_agent as get_urgent_reminders # Import the agent for reminders
from pages.chatbot_page import render_chatbot_page # Import the chatbot page renderer

def render_student_dashboard():
    st.header("EduMate - Student Dashboard 👋")
    
    # --- Urgent Reminder (Automatic Display) ---
    st.subheader("Your Daily Boost! 🌟")
    student_name = st.session_state.get("student_name", "Student")
    
    if "urgent_reminder_displayed" not in st.session_state:
        st.session_state.urgent_reminder_displayed = False

    if not st.session_state.urgent_reminder_displayed:
        with st.container(border=True):
            reminder_message = get_urgent_reminders(student_name)
            st.info(reminder_message)
        st.session_state.urgent_reminder_displayed = True

    st.markdown("---")

    # Academic Roadmap
    st.subheader("Your Academic Roadmap 🗺️")
    subjects = get_all_subjects()
    if subjects:
        for subject in subjects:
            st.write(f"- **{subject['name']}**: {', '.join(subject['topics'])} (Due: {subject['due_date']})")
    else:
        st.info("No subjects added to your roadmap yet! Head over to the Admin Dashboard to add some. 📚")

    # Task Tracker
    st.subheader("Your Study Tasks 📝")
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        task_name = st.text_input("New Task Name", key="new_task_input")
    with col2:
        due_date = st.date_input("Due Date", key="new_task_date")
    
    if st.button("Add Task ✅", key="add_task_button"):
        if task_name and task_name.strip(): # Added .strip() for robust validation
            add_task(task_name.strip(), due_date) # Save stripped name
            st.success(f"Task '{task_name.strip()}' added successfully! 🎉")
            st.session_state.urgent_reminder_displayed = False
            st.rerun()
        else:
            st.error("Please enter a task name. 😅")
    
    st.markdown("---")

    st.subheader("Tasks Pending & Completed ✨")
    tasks = get_tasks()
    
    if not tasks:
        st.info("You currently have no tasks! Time to add some study goals! 🎯")
    else:
        pending_tasks = [t for t in tasks if not t.get('completed', False)]
        completed_tasks = [t for t in tasks if t.get('completed', False)]

        if pending_tasks:
            st.markdown("##### Pending Tasks ⏳")
            for i, task in enumerate(tasks): 
                if not task.get('completed', False):
                    col_task, col_status = st.columns([0.7, 0.3])
                    with col_task:
                        st.markdown(f"**{task['task']}** (Due: {task['due_date']})")
                    with col_status:
                        if st.button(f"Mark as Done 💪", key=f"complete_task_{i}"):
                            if mark_task_completed(i):
                                st.success(f"Task '{task['task']}' marked as completed! Bravo! 🥳")
                                st.session_state.urgent_reminder_displayed = False
                                st.rerun()
            st.markdown("---")
        else:
            st.success("All your tasks are completed! You're doing amazing! ✨")

        if completed_tasks:
            st.markdown("##### Completed Tasks 🎉")
            for task in completed_tasks:
                st.markdown(f"<del>**{task['task']}** (Due: {task['due_date']})</del> - _Completed!_ 🏆", unsafe_allow_html=True)
            
    # Productivity Tools
    st.subheader("Focus & Productivity 🚀")
    pomodoro_timer()

def main():
    st.sidebar.title("EduMate Navigation 🧭")
    if "student_name" not in st.session_state:
        st.session_state.student_name = "Student"

    page = st.sidebar.radio("Go to", ["Student Dashboard", "Doubt Solver Chatbot", "Admin Dashboard"])

    if page == "Student Dashboard":
        render_student_dashboard()
    elif page == "Doubt Solver Chatbot":
        # Ensure the chatbot page is rendered correctly
        render_chatbot_page() 
    elif page == "Admin Dashboard":
        render_admin_dashboard()

if __name__ == "__main__":
    st.set_page_config(page_title="EduMate - Academic Assistant", layout="wide", initial_sidebar_state="expanded")
    st.markdown(
        """
        <style>
        .st-emotion-cache-1jm6ylc {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    main()