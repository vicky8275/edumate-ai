import streamlit as st
from app import render_student_dashboard
from admin_dashboard import render_admin_dashboard
from pages.chatbot_page import render_chatbot_page # Import the new chatbot page function

# Entry point for EduMate
if __name__ == "__main__":
    st.set_page_config(
        page_title="EduMate - Academic Assistant",
        layout="wide",
        # Set initial page to Student Dashboard
        initial_sidebar_state="expanded"
    )

    # Custom styling to remove Streamlit's default page navigation
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* This hides the default Streamlit pages in the sidebar */
            .st-emotion-cache-1jm6ylc {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("EduMate Navigation")
    
    # Manually define your navigation options
    page = st.sidebar.radio(
        "Go to",
        ["Student Dashboard", "Doubt Solver Chatbot", "Admin Dashboard"],
        index=0 # Set default selected page
    )

    if page == "Student Dashboard":
        render_student_dashboard()
    elif page == "Doubt Solver Chatbot":
        render_chatbot_page()
    elif page == "Admin Dashboard":
        render_admin_dashboard()