import logging
from typing import List, Optional
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from src.config import Config
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain.schema import Document
from azure.core.exceptions import ResourceNotFoundError
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)

class TextProcessor:
    """Class to handle text processing and vector store operations."""
    
    @staticmethod
    def get_text_chunks(text: str) -> List[str]:
        """Split text into chunks using token-based splitting."""
        if not text.strip():
            return []
        
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=Config.CHUNK_SIZE,
                chunk_overlap=Config.CHUNK_OVERLAP,
                length_function=lambda x: len(encoding.encode(x)),
                separators=["\n\n", "\n", ".", " ", ""]
            )
            chunks = text_splitter.split_text(text)
            logger.info(f"Created {len(chunks)} text chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error creating text chunks: {e}")
            return []

    @staticmethod
    def get_vectorstore(text_chunks: List[str]) -> Optional[object]:
        """Create or update vector store from text chunks using Azure Cognitive Search.
        New embeddings will be merged with existing index if present.
        """
        if not text_chunks:
            logger.debug("No text chunks provided")
            return None

        try:
            # Configure embeddings
            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                azure_deployment=Config.EMBEDDING_MODEL,
                api_key=Config.AZURE_OPENAI_KEY,
                api_version=Config.AZURE_API_VERSION,
            )

            # Prepare documents
            docs = [Document(page_content=chunk) for chunk in text_chunks]

            # Create or update AzureSearch vector store
            vectorstore = AzureSearch(
                azure_search_endpoint=Config.AZURE_SEARCH_ENDPOINT,
                azure_search_key=Config.AZURE_SEARCH_KEY,
                index_name=Config.AZURE_SEARCH_INDEX_NAME,
                embedding_function=embeddings,
            )

            # Add new documents to existing index
            vectorstore.add_documents(docs)
            logger.info(f"Added {len(text_chunks)} new chunks to Azure vector store")
            return vectorstore
        except Exception as e:
            logger.error(f"Error updating Azure vector store: {e}", exc_info=True)
            return None