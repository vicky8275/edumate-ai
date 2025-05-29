import streamlit as st
from chatbot_agent import get_chatbot_response # This function now returns a generator

def render_chatbot_page():
    st.header("EduMate - Doubt Solver Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for new user queries
    if user_query := st.chat_input("Ask EduMate anything..."):
        # Add user message to chat history immediately
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Get chatbot response as a generator
        with st.chat_message("assistant"):
            # Use st.write_stream to display the tokens as they arrive
            # We'll build the full response string to save to history
            full_response = st.write_stream(get_chatbot_response(user_query, st.session_state.messages))
        
        # Add the complete assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()