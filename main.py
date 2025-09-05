# main.py
import streamlit as st
import os
import json

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CRITICAL FIX: st.set_page_config() MUST BE THE FIRST STREAMLIT COMMAND ---
# Configure app-wide settings here. These apply to all pages managed by main.py.
st.set_page_config(
    page_title="EduMate AI",
    page_icon="🎓",
    layout="wide", # Use wide layout for the overall app
    initial_sidebar_state="expanded" # Sidebar expanded by default
)
# --- END CRITICAL FIX ---


# Import other pages
from _pages import login_page
from app import render_student_dashboard
from _pages import chatbot_page
from _pages import admin_page
from _pages import roadmap_page
from _pages import agents_tools_page # NEW: Import the unified agents tools page

# --- Session State Initialization ---
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'is_guest' not in st.session_state: # This will always be False for local authenticated users
    st.session_state.is_guest = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Login" # Start on the login page
if 'chatbot_messages' not in st.session_state: # Ensure chat history is initialized
    st.session_state.chatbot_messages = []
# app_id is still used for naming convention in data_manager (though not strictly necessary without Firebase)
if 'app_id' not in st.session_state: 
    st.session_state.app_id = os.getenv("__app_id", "default-app-id")

# Initialize quiz history (needed by TrackerAgent and QuizAgent)
if 'quiz_history' not in st.session_state:
    st.session_state.quiz_history = []
# Initialize for PlannerAgent
if 'current_study_plan' not in st.session_state:
    st.session_state.current_study_plan = None
if 'plan_duration' not in st.session_state:
    st.session_state.plan_duration = None


# --- Main Application Logic ---

# Sidebar for navigation
st.sidebar.title("EduMate Navigation")

# Only show sidebar content if logged in
if st.session_state.is_logged_in:
    # Display current user info in sidebar
    user_display_id = st.session_state.user_id
    st.sidebar.markdown(f"**Logged In As:** User `{user_display_id}`")

    # Navigation buttons (SIMPLIFIED LABELS)
    if st.sidebar.button("🎓 Dashboard", key="nav_dashboard"):
        st.session_state.current_page = "Dashboard"
    if st.sidebar.button("🗺️ Roadmap", key="nav_roadmap"):
        st.session_state.current_page = "Roadmap"
    if st.sidebar.button("🤖 Chatbot", key="nav_chatbot"):
        st.session_state.current_page = "Chatbot"
    if st.sidebar.button("🛠️ AI Tools", key="nav_agents_tools"): # NEW: Unified AI Tools button
        st.session_state.current_page = "AITools"
    if st.sidebar.button("⚙️ Admin", key="nav_admin"):
        st.session_state.current_page = "Admin"
    
    # Logout functionality for local session
    if st.sidebar.button("🚪 Logout", key="nav_logout"):
        st.session_state.is_logged_in = False
        st.session_state.user_id = None
        st.session_state.is_guest = False
        st.session_state.current_page = "Login"
        st.session_state.urgent_reminder_displayed = False 
        st.session_state.chatbot_messages = [] 
        st.session_state.quiz_history = [] 
        st.session_state.current_study_plan = None 
        st.session_state.plan_duration = None 
        st.success("You have been logged out. 👋")
        st.rerun()

    # Render the selected page, passing user_id
    if st.session_state.current_page == "Dashboard":
        render_student_dashboard(st.session_state.user_id, st.session_state.is_guest, st.session_state.app_id)
    elif st.session_state.current_page == "Roadmap":
        roadmap_page.render_roadmap_page(st.session_state.user_id)
    elif st.session_state.current_page == "AITools": # NEW: Render Unified Agents Tools Page
        agents_tools_page.render_agents_tools_page(st.session_state.user_id)
    elif st.session_state.current_page == "Chatbot":
        chatbot_page.render_chatbot_page(st.session_state.user_id)
    elif st.session_state.current_page == "Admin":
        admin_page.render_admin_page(st.session_state.user_id)
else:
    # Render login page if not logged in
    login_page.render_login_page()
