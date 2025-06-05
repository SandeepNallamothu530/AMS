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
        """Create vector store from text chunks using Azure Cognitive Search.
        If an existing index is present, delete it before creating a new one.
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

            # Create proper Azure credential
            credential = AzureKeyCredential(Config.AZURE_SEARCH_KEY)

            # Delete existing Azure Search index if it exists
            index_client = SearchIndexClient(
                endpoint=Config.AZURE_SEARCH_ENDPOINT,
                credential=credential
            )

            try:
                index_client.get_index(Config.AZURE_SEARCH_INDEX_NAME)
                index_client.delete_index(Config.AZURE_SEARCH_INDEX_NAME)
                logger.info(f"Deleted existing Azure Search index: {Config.AZURE_SEARCH_INDEX_NAME}")
            except ResourceNotFoundError:
                logger.info(f"No existing Azure Search index to delete: {Config.AZURE_SEARCH_INDEX_NAME}")

            # Create AzureSearch vector store
            vectorstore = AzureSearch.from_documents(
                documents=docs,
                embedding=embeddings,
                azure_search_endpoint=Config.AZURE_SEARCH_ENDPOINT,
                azure_search_key=Config.AZURE_SEARCH_KEY,
                index_name=Config.AZURE_SEARCH_INDEX_NAME,
            )
            logger.info(f"Created Azure vector store with {len(text_chunks)} chunks")
            return vectorstore
        except Exception as e:
            logger.error(f"Error creating Azure vector store: {e}", exc_info=True)
            return None