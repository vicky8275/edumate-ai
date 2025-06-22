# pages/login_page.py
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

    st.markdown("<h1 style='text-align: center;'>EduMate 🎓</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Your Smart Academic Assistant</h2>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login to Your Account")
        with st.form("login_form", clear_on_submit=False):
            login_username = st.text_input("Username", key="login_username_input")
            login_password = st.text_input("Password", type="password", key="login_password_input")
            
            login_submitted = st.form_submit_button("Log In")

            if login_submitted:
                if login_username and login_password:
                    result = login_user_local(login_username, login_password)
                    if result["success"]:
                        st.session_state.is_logged_in = True
                        st.session_state.user_id = result["user_id"]
                        st.session_state.is_guest = False # Not a guest, but a local authenticated user
                        st.success("Logged in successfully! Redirecting...")
                        st.session_state.current_page = "Dashboard"
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['error']}")
                else:
                    st.warning("Please enter both username and password.")

    with col2:
        st.subheader("New User? Sign Up!")
        with st.form("signup_form", clear_on_submit=True):
            signup_username = st.text_input("Choose a Username", key="signup_username_input")
            signup_password = st.text_input("Choose a Password", type="password", key="signup_password_input")
            signup_confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password_input")

            signup_submitted = st.form_submit_button("Sign Up")

            if signup_submitted:
                if signup_username and signup_password and signup_confirm_password:
                    if signup_password == signup_confirm_password:
                        result = signup_user_local(signup_username, signup_password)
                        if result["success"]:
                            st.success(f"Account for '{signup_username}' created successfully! Please log in.")
                            # Optional: automatically log them in after signup
                            # st.session_state.is_logged_in = True
                            # st.session_state.user_id = result["user_id"]
                            # st.session_state.current_page = "Dashboard"
                            # st.rerun()
                        else:
                            st.error(f"Sign up failed: {result['error']}")
                    else:
                        st.error("Passwords do not match.")
                else:
                    st.warning("Please fill in all sign-up fields.")

    st.markdown("---")
    st.info("Your data is saved locally on this device. Sign up or log in to manage your personalized academic journey!")

