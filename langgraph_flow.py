import streamlit as st
from data_manager import get_tasks
from datetime import datetime, timedelta

def run_agent(student_name="Student"):
    tasks = get_tasks()
    today = datetime.now().date()
    urgent_tasks = []
    for task in tasks:
        try:
            if not task.get("completed", False): # Only consider pending tasks
                due_date = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                if today <= due_date <= today + timedelta(days=2):
                    urgent_tasks.append(task)
        except ValueError:
            print(f"Skipping task due to invalid date format: {task}")
            continue
            
    if urgent_tasks:
        reminder_text = f"Hello {student_name}! 👋 Just a friendly reminder that you have some crucial study tasks on the horizon to ensure your academic success this semester. Let's get them done! 🚀\n\n"
        for task in urgent_tasks:
            reminder_text += f"- Don't forget to complete '{task['task']}' by {task['due_date']}. Time to shine! ✨\n"
        
        reminder_text += "\nI have full confidence in your abilities – you’ve got this! 💪"
        return reminder_text
    else:
        return f"Hello {student_name}! 🎉 You currently have no urgent tasks due in the next couple of days. Keep up the great work and enjoy your progress! 🌟"