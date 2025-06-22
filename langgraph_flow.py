# langgraph_flow.py
import streamlit as st
from data_manager import get_tasks # This now gets tasks from local SQLite
from datetime import datetime, timedelta

def run_agent(student_name="Student"):
    """
    Generates an urgent reminder message based on tasks due soon for the current user.
    Retrieves user_id from Streamlit's session state.
    """
    # Access user_id from st.session_state as it's set in main.py
    user_id = st.session_state.get('user_id')
    
    if not user_id:
        return "Reminder system not fully initialized. Please refresh the app."

    # Retrieve tasks for the current user from the data manager (which uses SQLite)
    tasks = get_tasks(user_id) # Pass only user_id

    today = datetime.now().date()
    urgent_tasks = []
    # Iterate through tasks to find those that are pending and due within the next 2 days
    for task in tasks:
        try:
            if not task.get("completed", False): # Only consider tasks that are not yet completed
                due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                # Check if due date is today or in the next two days
                if today <= due_date <= today + timedelta(days=2):
                    urgent_tasks.append(task)
        except ValueError:
            # Print an error for tasks with invalid date formats, but continue processing others
            print(f"WARNING: Skipping task due to invalid date format: {task}")
            continue

    if urgent_tasks:
        # Construct a friendly reminder message with urgent tasks listed
        reminder_text = f"Hello {student_name}! 👋 Just a friendly reminder that you have some crucial study tasks on the horizon to ensure your academic success this semester. Let's get them done! 🚀\n\n"
        for task in urgent_tasks:
            reminder_text += f"- Don't forget to complete '{task['task']}' by {task['due_date']}. Time to shine! ✨\n"

        reminder_text += "\nI have full confidence in your abilities – you’ve got this! 💪"
        return reminder_text
    else:
        # Message if no urgent tasks are found
        return f"Hello {student_name}! 🎉 You currently have no urgent tasks due in the next couple of days. Keep up the great work and enjoy your progress! 🌟"

