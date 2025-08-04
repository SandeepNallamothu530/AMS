import streamlit as st
import os
from src.config import Config

class Auth:
    """Authentication handler class"""
    
    # Store credentials (Note: In a production environment, never store plain text credentials in code)
    USERNAME = "NDBS@Admin"
    PASSWORD = "Admin@bs.nttdata.com"
    
    @staticmethod
    def initialize_session_state():
        """Initialize authentication-related session state variables."""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "username" not in st.session_state:
            st.session_state.username = None
    
    @staticmethod
    def login(username: str, password: str) -> bool:
        """Authenticate user with provided credentials."""
        if username == Auth.USERNAME and password == Auth.PASSWORD:
            st.session_state.authenticated = True
            st.session_state.username = username
            return True
        return False
    
    @staticmethod
    def logout():
        """Log out the current user."""
        st.session_state.authenticated = False
        st.session_state.username = None
    
    @staticmethod
    def render_login_page():
        """Render the login page."""
        
        # Hide Streamlit's default elements
        st.markdown("""
        <style>
            /* Hide Streamlit branding and menu */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* Remove padding from main container */
            .main .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
                padding-left: 1rem;
                padding-right: 1rem;
                max-width: none;
            }
            
            /* Full screen background */
            .stApp {
                background: white;
                min-height: 100vh;
            }
            
            /* Center the main content */
            section.main > div {
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                min-height: 100vh !important;
                padding: 2rem !important;
            }
            
            /* Login container styling */
            .login-container {
                max-width: 380px;
                width: 100%;
                padding: 3rem 2.5rem;
                border-radius: 20px;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.08);
                background: rgba(255, 255, 255, 1);
                border: 1px solid rgba(0, 0, 0, 0.08);
                position: relative;
                overflow: hidden;
            }
            
            /* Glassmorphism effect overlay */
            .login-wrapper::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(248, 250, 252, 0.5);
                pointer-events: none;
            }
            
            /* Header styling */
            .login-header {
                text-align: center;
                margin-bottom: 2.5rem;
                position: relative;
                z-index: 1;
            }
            
            .login-header h1 {
                color: #2c3e50;
                font-size: 2.2rem;
                font-weight: 300;
                letter-spacing: -0.5px;
                margin: 1rem 0 0 0;
            }
            
            /* Logo styling */
            div[data-testid="stImage"] {
                display: flex;
                justify-content: center;
                margin-bottom: 1.5rem;
                background: transparent !important;
                border: none !important;
            }
            
            div[data-testid="stImage"] > div {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
            }
            
            div[data-testid="stImage"] img {
                border: none !important;
                box-shadow: none !important;
                background: transparent !important;
            }
            
            /* Form elements styling */
            .stTextInput > div > div > input {
                padding: 1rem !important;
                border: 2px solid #e1e8ed !important;
                border-radius: 12px !important;
                font-size: 1rem !important;
                transition: all 0.3s ease !important;
                background: rgba(255, 255, 255, 0.9) !important;
                color: #2c3e50 !important;
            }
            
            .stTextInput > div > div > input:focus {
                border-color: #667eea !important;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
                background: rgba(255, 255, 255, 1) !important;
                outline: none !important;
            }
            
            .stTextInput > div > div > input::placeholder {
                color: #8892b0 !important;
            }
            
            /* Labels styling */
            .stTextInput > label {
                color: #4a5568 !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                margin-bottom: 0.5rem !important;
            }
            
            /* Button styling */
            .stButton > button {
                width: 100% !important;
                padding: 1rem 1.5rem !important;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 12px !important;
                font-size: 1.1rem !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                margin-top: 1.5rem !important;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
            }
            
            .stButton > button:active {
                transform: translateY(0) !important;
            }
            
            /* Success/Error messages */
            .stSuccess, .stError {
                margin-top: 1rem;
                border-radius: 8px;
                border: none;
            }
            
            .stSuccess > div {
                background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                color: white;
            }
            
            .stError > div {
                background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
                color: white;
            }
            
            /* Forgot password link */
            .forgot-password {
                text-align: center;
                margin-top: 2rem;
                position: relative;
                z-index: 1;
            }
            
            .forgot-password a {
                color: #667eea;
                text-decoration: none;
                font-size: 0.95rem;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            
            .forgot-password a:hover {
                color: #764ba2;
                text-decoration: underline;
            }
            
            /* Form container */
            div[data-testid="stForm"] {
                background: transparent;
                border: none;
                padding: 0;
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .login-container {
                    margin: 1rem;
                    padding: 2rem 1.5rem;
                    max-width: 340px;
                }
                
                .login-header h1 {
                    font-size: 1.8rem;
                }
            }
            
            /* Remove default streamlit spacing */
            div[data-testid="stVerticalBlock"] > div:has(.login-container) {
                gap: 0 !important;
            }
            
            /* Animation for container */
            .login-wrapper {
                animation: slideInUp 0.6s ease-out;
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Create centered container with custom CSS class
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        
        # Add logo if exists
        if os.path.exists(Config.LOGO_PATH):
            st.image(Config.LOGO_PATH, width=120)
        
        st.markdown('<h1 style="text-align: center; color: #2c3e50; font-size: 2.2rem; font-weight: 300; letter-spacing: -0.5px; margin: 1rem 0 2rem 0;">Login</h1>', unsafe_allow_html=True)
        
        # Login form
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
            
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if username and password:
                    if Auth.login(username, password):
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.error("⚠️ Please enter both username and password")
        
        # Forgot password link
        st.markdown("""
            <div class="forgot-password">
                <a href="#" onclick="alert('Contact your administrator for password reset')">
                    Forgot your password?
                </a>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def check_authentication():
        """Check if user is authenticated and redirect to login if not."""
        Auth.initialize_session_state()
        if not st.session_state.authenticated:
            Auth.render_login_page()
            st.stop()
        return True