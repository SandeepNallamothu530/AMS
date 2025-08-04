import os
import io
import tempfile
import logging
from typing import List, Dict, Any
import PyPDF2
from langchain_community.document_loaders import UnstructuredFileLoader
from src.config import Config

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Class to handle document processing operations."""
    
    @staticmethod
    def extract_text_from_pdf(uploaded_file) -> str:
        """Extract text from PDF using PyPDF2."""
        try:
            # Read the uploaded file content
            pdf_content = uploaded_file.getvalue()
            pdf_file = io.BytesIO(pdf_content)
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            total_pages = len(pdf_reader.pages)
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text += f"\n\n--- Page {page_num + 1} ---\n\n"
                        text += page_text
                    else:
                        logger.warning(f"Page {page_num + 1} appears to be empty or image-only")
                except Exception as e:
                    logger.error(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
            
            if not text.strip():
                logger.warning("No text could be extracted from the PDF. It might be image-based or corrupted.")
                return ""
            
            logger.info(f"Successfully extracted text from {total_pages} pages of {uploaded_file.name}")
            return text
            
        except Exception as e:
            logger.error(f"Error processing PDF {uploaded_file.name}: {e}")
            raise e

    @staticmethod
    def get_text_from_documents(uploaded_files: List, status_callback=None) -> list:
        """Extract text from various document types and return list of (file_name, text)."""
        results = []
        
        try:
            for uploaded_file in uploaded_files:
                file_extension = uploaded_file.name.lower().split('.')[-1]
                
                try:
                    if file_extension == 'pdf':
                        # Use PyPDF2 for PDF processing
                        doc_text = DocumentProcessor.extract_text_from_pdf(uploaded_file)
                        
                        if not doc_text.strip():
                            if status_callback:
                                status_callback("warning", f"⚠️ No text extracted from {uploaded_file.name}. This might be an image-based PDF.")
                            continue
                            
                    else:
                        # Use UnstructuredFileLoader for other file types
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        try:
                            loader = UnstructuredFileLoader(
                                tmp_file_path,
                                mode="elements",
                                strategy="fast"
                            )
                            
                            documents = loader.load()
                            doc_text = "\n".join(doc.page_content for doc in documents)
                            
                        finally:
                            # Clean up the temporary file
                            try:
                                os.unlink(tmp_file_path)
                            except:
                                pass
                    
                    if doc_text.strip():
                        results.append((uploaded_file.name, doc_text))
                        logger.info(f"Successfully processed {uploaded_file.name}")
                    else:
                        if status_callback:
                            status_callback("warning", f"No content extracted from {uploaded_file.name}")
                    
                except Exception as e:
                    logger.error(f"Error processing {uploaded_file.name}: {e}")
                    if status_callback:
                        status_callback("error", f"Could not process {uploaded_file.name}: {e}")
                    continue
                        
        except Exception as e:
            logger.error(f"Error in document processing: {e}")
            if status_callback:
                status_callback("error", f"Error processing documents: {e}")
        
        return results

    @staticmethod
    def validate_files(uploaded_files: List) -> tuple[bool, str]:
        """Validate uploaded files."""
        if not uploaded_files:
            return False, "No files uploaded"
        
        for file in uploaded_files:
            if file.size > Config.MAX_FILE_SIZE:
                return False, f"File {file.name} is too large. Maximum size is 10MB."
            if file.type not in Config.SUPPORTED_FILE_TYPES:
                return False, f"File {file.name} has unsupported type: {file.type}"
        
        return True, "All files are valid"

    @staticmethod
    def get_pdf_info(uploaded_file) -> Dict[str, Any]:
        """Get basic information about the PDF."""
        try:
            pdf_content = uploaded_file.getvalue()
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            info = {
                'total_pages': len(pdf_reader.pages),
                'metadata': pdf_reader.metadata if pdf_reader.metadata else {},
                'encrypted': pdf_reader.is_encrypted
            }
            
            return info
        except Exception as e:
            logger.error(f"Error getting PDF info: {e}")
            return {}