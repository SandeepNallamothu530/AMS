import streamlit as st
import logging
from src.config import Config
from src.document_processor import DocumentProcessor
from src.text_processor import TextProcessor
# from src.conversation_handler import ConversationHandler
from src.ui_components import UIComponents

logger = logging.getLogger(__name__)

class AMSBotApp:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.text_processor = TextProcessor()
        self.ui_components = UIComponents()
    
    def run(self):
        """Main application run method."""
        # Setup UI
        self.ui_components.setup_page()
        self.ui_components.initialize_session_state()
        
        # Render UI components
        uploaded_files, process_btn, clear_btn = self.ui_components.render_sidebar()
        user_question = self.ui_components.render_main_chat()
        
        # Handle user input
        if user_question:
            self.ui_components.handle_user_input(
                user_question, 
                st.session_state.conversation_handler
            )
        
        # Handle process button
        if process_btn:
            self._handle_document_processing(uploaded_files)
        
        # Handle clear button
        if clear_btn:
            self.ui_components.clear_session_data()
    
    def _handle_document_processing(self, uploaded_files):
        """Handle document processing workflow."""
        if not uploaded_files:
            self.ui_components.display_status("warning", "Please upload at least one document!")
            return
        
        # Validate files
        is_valid, validation_message = self.document_processor.validate_files(uploaded_files)
        if not is_valid:
            self.ui_components.display_status("error", f"File validation failed: {validation_message}")
            return
        
        with st.spinner("Processing documents..."):
            try:
                # Extract text from documents
                file_texts = self.document_processor.get_text_from_documents(
                    uploaded_files, 
                    status_callback=self.ui_components.display_status
                )
                
                if not file_texts or not any(text for _, text in file_texts):
                    self.ui_components.display_status("error", "No text could be extracted from the uploaded files!")
                    return
                
                # Create text chunks
                text_chunks = []
                for file_name, text in file_texts:
                    chunks = self.text_processor.get_text_chunks(text)
                    if chunks:
                        text_chunks.extend([(file_name, chunk) for chunk in chunks])
                
                if not text_chunks:
                    self.ui_components.display_status("error", "Could not create text chunks from the documents!")
                    return

                self.ui_components.display_status("info", f"Created {len(text_chunks)} text chunks")

                # Create vector store
                vectorstore = self.text_processor.get_vectorstore(text_chunks)
                
                if not vectorstore:
                    self.ui_components.display_status("error", "Failed to create vector store!")
                    return

                # Create conversation chain
                conversation_chain = st.session_state.conversation_handler.get_conversation_chain(vectorstore)
                
                if conversation_chain:
                    st.session_state.processed_files = [f.name for f in uploaded_files]
                    self.ui_components.display_status("success", "✅ Documents processed successfully")
                    self.ui_components.display_status("info", "You can now ask questions about your documents!")
                else:
                    self.ui_components.display_status("error", "Failed to create conversation chain!")
                    
            except Exception as e:
                logger.error(f"Error in document processing: {e}")
                self.ui_components.display_status("error", f"An error occurred while processing documents: {e}")

def main():
    """Main function to run the application."""
    app = AMSBotApp()
    app.run()

if __name__ == '__main__':
    main()