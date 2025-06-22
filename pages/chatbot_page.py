# pages/chatbot_page.py
import streamlit as st
import sys
import os

# Ensure the parent directory is in the sys.path for module imports
if os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) not in sys.path:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot_agent import get_chatbot_response # LLM agent
from data_manager import get_tasks, get_all_subjects # For passing context to LLM

# Initialize Streamlit session state for messages if not already present
if 'chatbot_messages' not in st.session_state:
    st.session_state.chatbot_messages = []

# Function to render the chatbot interface
def render_chatbot_page(user_id):
    """
    Renders the main chatbot interface, displaying chat history and allowing user input.
    """
    # CRITICAL: st.set_page_config() REMOVED FROM HERE. It is now only in main.py.

    st.title("🤖 EduMate Doubt Solver Chatbot")
    st.write("Ask me anything about your studies! I'm here to provide crystal-clear explanations. ✨")

    # Display chat messages from history
    for message in st.session_state.chatbot_messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])

    # User input for new messages
    user_query = st.chat_input("Ask EduMate...")

    if user_query:
        # Add user message to history
        st.session_state.chatbot_messages.append({"role": "user", "content": user_query})

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_query)

        # Get response from the chatbot agent
        with st.chat_message("assistant"):
            with st.spinner("EduMate is thinking..."):
                # Pass user_id to the chatbot_agent for context-aware responses
                # user_id is passed down from main.py's session state
                full_response = st.write_stream(get_chatbot_response(user_query, st.session_state.chatbot_messages, user_id=user_id))
        
        # Add assistant message to history
        st.session_state.chatbot_messages.append({"role": "assistant", "content": full_response})
