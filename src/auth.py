import streamlit as st
import os
from src.config import Config

class Auth:
    """Authentication handler class"""
    
    USERNAME = "NDBS@Admin"
    PASSWORD = "Admin@bs.nttdata.com"
    
    @staticmethod
    def initialize_session_state():
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "username" not in st.session_state:
            st.session_state.username = None
    
    @staticmethod
    def login(username: str, password: str) -> bool:
        if username == Auth.USERNAME and password == Auth.PASSWORD:
            st.session_state.authenticated = True
            st.session_state.username = username
            return True
        return False
    
    @staticmethod
    def logout():
        st.session_state.authenticated = False
        st.session_state.username = None
    
    @staticmethod
    def render_login_page():
        # Configure page layout
        st.set_page_config(
            page_title="Login",
            initial_sidebar_state="collapsed"
        )

        # Create three columns for centering
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Display logo
            if os.path.exists(Config.LOGO_PATH):
                st.image(Config.LOGO_PATH, width=300, use_container_width=False)
            
            # Add some spacing
            st.write("#")  # adds vertical space
            
            # Title
            st.title("Welcome Back")
            st.write("Please sign in to continue")
            
            # Login Form
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    key="username_input"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="password_input"
                )
                
                # Add some space before the button
                st.write("")
                
                submitted = st.form_submit_button(
                    "Sign In",
                    type="primary",
                    use_container_width=True
                )

                if submitted:
                    if username and password:
                        if Auth.login(username, password):
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
                    else:
                        st.warning("⚠️ Please enter both username and password")
            
            # Forgot password help text
            with st.expander("Forgot Password?"):
                st.info("Please contact your administrator to reset your password.")

        st.markdown('</div></div>', unsafe_allow_html=True)

    @staticmethod
    def check_authentication():
        Auth.initialize_session_state()
        if not st.session_state.authenticated:
            Auth.render_login_page()
            st.stop()
        return True
