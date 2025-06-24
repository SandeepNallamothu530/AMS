import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class."""
    
    # File processing settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
    SUPPORTED_FILE_TYPES = [
        "application/pdf", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
        "text/plain"
    ]
    #======================================================================================================================
    # Text processing settings
    CHUNK_SIZE = 250
    CHUNK_OVERLAP = 100
    
    
    # Embedding Model settings
    EMBEDDING_MODEL = "text-embedding-3-large"


    #Azure OpenAI settings [LLM model]
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
    LLM_MODEL = "gpt-4o"
    max_tokens = 4096
    temperature = 1.0
    # top_p = 1.0
    
    #AZURE Cognitive Search settings [vector store]
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
    #=======================================================================================================================
    # UI settings
    LOGO_PATH = "assets/image.png"
    APP_TITLE = "AMS BOT"
    APP_ICON = "💬"
    
    # @staticmethod
    # def get_groq_api_key():
    #     """Get GROQ API key from environment variables."""
    #     api_key = os.getenv("GROQ_API_KEY")
    #     if not api_key:
    #         logger.error("GROQ_API_KEY not found in environment variables!")
    #     return api_key
    
    @staticmethod
    def get_prompt_template():
        """Get the conversation prompt template."""
        return """
    You are AMS BOT, an expert assistant specializing in SAP systems, modules, and documentation. Your role is to provide clear, accurate, and professional answers to user questions about SAP and their uploaded documents, referencing SAP best practices and concepts whenever possible.

    - If greeted (e.g., "hi", "hello", "hey"), respond warmly and offer your assistance.
    - If a question is asked and relevant document context is available:
        - Extract and interpret key information from {context}.
        - Answer the question concisely, referencing SAP best practices, processes, modules, or documentation standards as appropriate.
    - If a question is asked but no relevant context is available:
        - Respond: "I'm sorry, I don't have the required data to answer that question."
    - For follow-up questions, use {chat_history} to maintain conversation continuity and accuracy.
    - If asked about topics unrelated to SAP:
        - Respond: "I'm specialized in SAP systems and documentation. Please let me know how I can assist you with your SAP-related queries."

    Guidelines:
    - Provide direct, to-the-point answers. Do not include explanations or examples unless specifically requested.
    - Do not mention the length of your answer.
    - Give detailed answers when necessary, but avoid unnecessary information.
    - Highlight important points using **bold text**. If possible, use color for emphasis.
    - Present information in tables with clear headings and columns when appropriate.

    Context from documents:
    {context}

    User Question:
    {question}

    AMS BOT's Answer:
    """
