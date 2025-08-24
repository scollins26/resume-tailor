import os
import PyPDF2
from docx import Document
from typing import Optional
from loguru import logger
from ..models import FileFormat

class FileService:
    """Service for handling file operations and text extraction"""
    
    @staticmethod
    def extract_text_from_file(file_path: str, file_format: FileFormat) -> Optional[str]:
        """Extract text content from various file formats"""
        try:
            if file_format == FileFormat.PDF:
                return FileService._extract_from_pdf(file_path)
            elif file_format == FileFormat.DOCX:
                return FileService._extract_from_docx(file_path)
            elif file_format == FileFormat.TXT:
                return FileService._extract_from_txt(file_path)
            else:
                logger.error(f"Unsupported file format: {file_format}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text from file {file_path}: {e}")
            return None
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            return ""
    
    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading DOCX file: {e}")
            return ""
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading TXT file: {e}")
            return ""
    
    @staticmethod
    def detect_file_format(file_path: str) -> Optional[FileFormat]:
        """Detect file format based on file extension"""
        _, extension = os.path.splitext(file_path.lower())
        
        if extension == '.pdf':
            return FileFormat.PDF
        elif extension == '.docx':
            return FileFormat.DOCX
        elif extension == '.txt':
            return FileFormat.TXT
        else:
            logger.warning(f"Unsupported file extension: {extension}")
            return None
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: int = 10) -> bool:
        """Validate file size"""
        try:
            file_size = os.path.getsize(file_path)
            max_size_bytes = max_size_mb * 1024 * 1024
            return file_size <= max_size_bytes
        except Exception as e:
            logger.error(f"Error validating file size: {e}")
            return False
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace('\x00', '')  # Remove null bytes
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
