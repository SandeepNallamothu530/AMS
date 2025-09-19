import os
import streamlit as st
from PIL import Image
from UI.htmlTemplates import css, bot_template, user_template
from src.config import Config
from src.conversation_handler import ConversationHandler
from src.auth import authenticate_user, create_user, get_password_by_email
import logging

logger = logging.getLogger(__name__)

class UIComponents:
    """Class to handle UI components and interactions."""
    
    @staticmethod
    def setup_page():
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title=Config.APP_TITLE,
            page_icon=Config.APP_ICON,
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.write(css, unsafe_allow_html=True)
    
    @staticmethod
    def initialize_session_state():
        """Initialize Streamlit session state variables."""
        
        # Initialize application state
        if "conversation_handler" not in st.session_state:
            st.session_state.conversation_handler = ConversationHandler()
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = None
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = []
        if "prompt_template" not in st.session_state:
            st.session_state.prompt_template = Config.get_prompt_template()
        if "use_external_prompt" not in st.session_state:
            st.session_state.use_external_prompt = False
        
        # Default page to login
        if "page" not in st.session_state:
            st.session_state.page = "login"
        
        # Login state - simplified
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False
        if "user_email" not in st.session_state:
            st.session_state.user_email = None
    
    @staticmethod
    def safe_rerun():
        """Safely trigger a rerun if supported by the installed Streamlit version."""
        try:
            st.experimental_rerun()
        except AttributeError:
            try:
                st.rerun()
            except AttributeError:
                # Fallback for very old versions
                pass
    
    @staticmethod
    def render_login_page():
        """Render the main login page with register and forgot password options."""
        st.markdown("<h1 style='text-align: center;'>🤖 AMS Bot Login</h1>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Login Form
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            email = st.text_input("📧 Email", placeholder="Enter your email address")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            login_submitted = st.form_submit_button("🚀 Login", type="primary", use_container_width=True)
            
            if login_submitted:
                if not email or not password:
                    st.error("Please fill in both email and password")
                else:
                    ok, message = authenticate_user(email, password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.success("Login successful! Redirecting...")
                        UIComponents.safe_rerun()
                    else:
                        st.error(message)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📝 Create New Account", use_container_width=True):
                st.session_state.page = "register"
                UIComponents.safe_rerun()
        
        with col2:
            if st.button("🔑 Forgot Password?", use_container_width=True):
                st.session_state.page = "forgot_password"
                UIComponents.safe_rerun()
    
    @staticmethod
    def render_register_page():
        """Render the registration page."""
        st.markdown("<h1 style='text-align: center;'>📝 Create New Account</h1>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        with st.form("register_form"):
            st.subheader("Register Your Account")
            email = st.text_input("📧 Email", placeholder="Enter your email address")
            password = st.text_input("🔒 Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button("✅ Create Account", type="primary", use_container_width=True)
            
            if submit_button:
                if not email or not password or not confirm_password:
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 4:
                    st.error("Password must be at least 4 characters long")
                elif "@" not in email or "." not in email:
                    st.error("Please enter a valid email address")
                else:
                    ok, msg = create_user(email, password)
                    if ok:
                        st.success("✅ " + msg)
                        st.info("You can now login with your credentials")
                        st.session_state.page = "login"
                        UIComponents.safe_rerun()
                    else:
                        st.error("❌ " + msg)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "login"
            UIComponents.safe_rerun()
    
    @staticmethod
    def render_forgot_password_page():
        """Render the forgot password page."""
        st.markdown("<h1 style='text-align: center;'>🔑 Forgot Password</h1>", unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        with st.form("forgot_password_form"):
            st.subheader("Retrieve Your Password")
            st.info("Enter your email address to retrieve your password")
            email = st.text_input("📧 Email", placeholder="Enter your registered email address")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button("🔍 Get Password", type="primary", use_container_width=True)
            
            if submit_button:
                if not email:
                    st.error("Please enter your email address")
                else:
                    ok, result = get_password_by_email(email)
                    if ok:
                        st.success(f"✅ Your password is: **{result}**")
                        st.info("You can now use this password to login")
                    else:
                        st.error("❌ Email not found in our records")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("← Back to Login", use_container_width=True):
            st.session_state.page = "login"
            UIComponents.safe_rerun()
    
    @staticmethod
    def render_sidebar():
        """Render the sidebar with file upload, controls, and prompt template toggle."""
        with st.sidebar:
            # User info at the top
            st.markdown(f"👋 **Welcome:** {st.session_state.user_email}")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_email = None
                st.session_state.page = "login"
                UIComponents.safe_rerun()
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Add logo
            if os.path.exists(Config.LOGO_PATH):
                logo_img = Image.open(Config.LOGO_PATH)
                st.image(logo_img, width=350)
            else:
                st.warning("Logo image not found.")
            
            uploaded_files = st.file_uploader(
                "Upload your documents",
                accept_multiple_files=True,
                type=["pdf", "docx", "txt",'xlsx', 'xls'],
                help="Max file size: 10MB. PDFs processed with PyPDF2"
            )

            # Add toggle for switching prompt template
            external_toggle = st.toggle(
                "Use External Prompt",
                value=st.session_state.use_external_prompt,
                help="Toggle to use external prompt template for responses"
            )
            if external_toggle != st.session_state.use_external_prompt:
                st.session_state.use_external_prompt = external_toggle
                UIComponents.switch_prompt_template(external_toggle)

            col1, col2 = st.columns(2)
            with col1:
                process_btn = st.button("🚀 Process", type="primary", use_container_width=True)
            with col2:
                clear_btn = False
                if st.session_state.processed_files:
                    clear_btn = st.button("🗑️ Clear", type="secondary", use_container_width=True)
            
            return uploaded_files, process_btn, clear_btn
    
    @staticmethod
    def switch_prompt_template(use_external: bool):
        """Switch prompt template based on toggle state and update conversation chain."""
        try:
            # Store the current conversation chain and memory
            current_memory = st.session_state.conversation_handler.memory
            current_vectorstore = None
            if st.session_state.conversation_handler.conversation_chain:
                current_vectorstore = st.session_state.conversation_handler.conversation_chain.retriever.vectorstore
            
            # Update prompt template in session state based on toggle
            st.session_state.prompt_template = (
                Config.get_prompt_template_ext_src() if use_external else Config.get_prompt_template()
            )
            
            # Update conversation handler's prompt template
            st.session_state.conversation_handler.prompt_template = st.session_state.prompt_template
            
            # Recreate conversation chain with the new prompt template if vectorstore exists
            if current_vectorstore:
                new_conversation_chain = st.session_state.conversation_handler.get_conversation_chain(current_vectorstore)
                if new_conversation_chain:
                    # Restore the previous memory to maintain conversation continuity
                    st.session_state.conversation_handler.memory = current_memory
                    st.session_state.conversation_handler.conversation_chain = new_conversation_chain
                    st.success(f"✅ Switched to {'external' if use_external else 'default'} prompt template")
                else:
                    st.error(f"Failed to recreate conversation chain with {'external' if use_external else 'default'} prompt template")
            else:
                st.success(f"✅ Switched to {'external' if use_external else 'default'} prompt template. Process documents to apply changes.")
        except AttributeError as e:
            st.error(f"Error switching prompt template: {e}. Please ensure the prompt templates are correctly defined.")
            logger.error(f"AttributeError in switch_prompt_template: {e}")
        except Exception as e:
            st.error(f"Unexpected error switching prompt template: {e}")
            logger.error(f"Unexpected error in switch_prompt_template: {e}")

    @staticmethod
    def render_main_chat():
        """Render the main chat interface.""" 
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 2rem;'>{Config.APP_ICON} {Config.APP_TITLE}</h1>", unsafe_allow_html=True)
        
        # Chat interface
        chat_container = st.container()
        with chat_container:
            if st.session_state.chat_history:
                for i, message in enumerate(st.session_state.chat_history):
                    if i % 2 == 0:
                        st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                    else:
                        st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            
            # Show source documents if available
            if hasattr(st.session_state, 'last_source_documents') and st.session_state.last_source_documents:
                with st.expander("📄 Source Documents"):
                    for i, doc in enumerate(st.session_state.last_source_documents):
                        file_name = doc.metadata.get("file_name", f"Source {i+1}")
                        st.write(f"**Source {i+1} ({file_name}):**")
                        st.write(doc.page_content[:1000] + "..." if len(doc.page_content) > 1000 else doc.page_content)
                        st.write("---")

        # Chat input
        st.markdown("<div style='position: fixed; bottom: 0; width: 100%; padding: 1rem; background: #262730;'>", unsafe_allow_html=True)
        user_question = st.chat_input("Ask me anything about your documents...")
        st.markdown("</div>", unsafe_allow_html=True)
        
        return user_question
    
    @staticmethod
    def handle_user_input(user_question: str, conversation_handler: ConversationHandler):
        """Handle user input and display conversation."""
        if not conversation_handler.conversation_chain:
            st.warning("Please upload and process documents first!")
            return
        
        try:
            with st.spinner("Thinking..."):
                response = conversation_handler.process_user_input(user_question)
            
            if not response:
                st.error("Failed to get response from the conversation chain.")
                return
            
            # Update session state with new chat history
            st.session_state.chat_history = response['chat_history']
            
            # Store source documents in session state if needed
            if 'source_documents' in response and response['source_documents']:
                st.session_state.last_source_documents = response['source_documents']
            
            # Force rerun to display the updated chat immediately
            UIComponents.safe_rerun()
                        
        except Exception as e:
            st.error(f"Error processing your question: {e}")
    
    @staticmethod
    def display_status(status_type: str, message: str):
        """Display status messages."""
        if status_type == "success":
            st.success(message)
        elif status_type == "error":
            st.error(message)
        elif status_type == "warning":
            st.warning(message)
        elif status_type == "info":
            st.info(message)
    
    @staticmethod
    def clear_session_data():
        """Clear all session data."""
        st.session_state.conversation_handler.clear_memory()
        st.session_state.chat_history = None
        st.session_state.processed_files = []
        if 'last_source_documents' in st.session_state:
            del st.session_state.last_source_documents
        st.session_state.prompt_template = Config.get_prompt_template()  # Reset to default prompt template
        st.session_state.use_external_prompt = False  # Reset toggle to default
        st.success("✅ Cleared all data!")
        UIComponents.safe_rerun()
