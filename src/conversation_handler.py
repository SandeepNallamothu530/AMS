import logging
from typing import Optional
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_openai import AzureChatOpenAI
from src.config import Config

logger = logging.getLogger(__name__)

class ConversationHandler:
    """Class to handle conversation chain operations."""
    
    def __init__(self):
        self.prompt_template = Config.get_prompt_template()
        self.memory = None
        self.conversation_chain = None
    
    def get_conversation_chain(self, vectorstore: AzureSearch) -> Optional[ConversationalRetrievalChain]:
        """Create conversation chain with the given vector store."""
        try:
            # Validate vector store
            if not vectorstore:
                logger.error("No vector store provided")
                return None

            # Initialize Azure OpenAI
            llm = AzureChatOpenAI(
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                azure_deployment=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
                api_key=Config.AZURE_OPENAI_KEY,
                api_version=Config.AZURE_API_VERSION,
                temperature=Config.temperature,
                max_tokens=Config.max_tokens,
                streaming=True
            )

            # Create prompt template
            PROMPT = PromptTemplate(
                template=self.prompt_template,
                input_variables=["context", "chat_history", "question"]
            )

            # Initialize memory
            if not self.memory:
                self.memory = ConversationBufferMemory(
                    memory_key='chat_history',
                    return_messages=True,
                    output_key='answer'
                )

            # Configure retriever with search parameters
            retriever = vectorstore.as_retriever(
                search_type="hybrid",
                search_kwargs={
                    # "k": Config.RETRIEVER_K,
                }
            )

            conversation_chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=retriever,
                memory=self.memory,
                return_source_documents=True,
                combine_docs_chain_kwargs={'prompt': PROMPT},
                verbose=True  # Enable verbose mode for debugging
            )
            
            self.conversation_chain = conversation_chain
            logger.info("Conversation chain created successfully with Azure Search")
            return conversation_chain
            
        except Exception as e:
            logger.error(f"Error creating conversation chain: {e}", exc_info=True)
            return None
    
    def process_user_input(self, user_question: str) -> Optional[dict]:
        """Process user input and return response."""
        if not self.conversation_chain:
            return None
        
        try:
            response = self.conversation_chain({'question': user_question})
            return response
        except Exception as e:
            logger.error(f"Error processing user input: {e}", exc_info=True)
            return None
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory = None
        self.conversation_chain = None
        logger.info("Conversation memory cleared")