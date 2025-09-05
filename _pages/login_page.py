import streamlit as st
from data_manager import signup_user_local, login_user_local # Import new local auth functions

def render_login_page():
    """
    Renders the login and signup UI for local, hardcoded authentication.
    """
    # CRITICAL: st.set_page_config() REMOVED FROM HERE. It is now only in main.py.

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0d1117; /* Dark background */
            color: #c9d1d9; /* Light text */
            font-family: 'Inter', sans-serif;
        }
        .st-emotion-cache-nahz7x { /* This class is for the main content block */
            background-color: #161b22; /* Slightly lighter background for components */
            border-radius: 0.75rem;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: 600px; /* Wider for two columns */
            margin: 3rem auto;
        }
        .stButton button {
            background-color: #238636; /* GitHub green */
            color: white;
            border-radius: 0.5rem;
            border: none;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease-in-out, transform 0.1s ease-in-out;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }
        .stButton button:hover {
            background-color: #2ea043;
            transform: translateY(-1px);
        }
        .stButton button:active {
            transform: translateY(0);
        }
        .stTextInput label, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #c9d1d9;
        }
        .stTextInput div div input {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 0.5rem;
            color: #c9d1d9;
            padding: 0.5rem 1rem;
        }
        .stAlert {
            border-radius: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Welcome to EduMate AI")

    # Toggle between login and signup
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.show_signup:
        with st.form("signup_form"):
            st.subheader("Sign Up")
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button = st.form_submit_button("Sign Up")

            if signup_button:
                if not new_username or not new_password or not confirm_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    result = signup_user_local(new_username, new_password)
                    if result.get("success"):
                        st.success("Account created successfully! You can now log in.")
                        st.session_state.show_signup = False
                        st.rerun()
                    else:
                        st.error(result.get("error", "Signup failed."))
        st.markdown("Already have an account? [Login here](#)", unsafe_allow_html=True)
        if st.button("Go to Login", key="go_to_login"):
            st.session_state.show_signup = False
            st.rerun()
    else:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    user = login_user_local(username, password)
                    if user and user.get("success"):
                        st.session_state.is_logged_in = True
                        st.session_state.user_id = username
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error(user.get("error", "Invalid username or password"))
        st.markdown("Don't have an account? [Sign up here](#)", unsafe_allow_html=True)
        if st.button("Go to Sign Up", key="go_to_signup"):
            st.session_state.show_signup = True
            st.rerun()
