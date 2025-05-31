from typing import List, Union
from pathlib import Path
import PyPDF2
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    """
    A utility class for processing and chunking documents (PDF and DOCX).
    Handles document reading and text splitting for RAG applications.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document processor with text splitting configuration.
        
        Args:
            chunk_size (int): Maximum size of each text chunk in characters.
                             Defaults to 1000 characters.
            chunk_overlap (int): Number of characters to overlap between chunks.
                               Defaults to 200 characters.
        """
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def read_pdf(self, file_path: Union[str, Path]) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            file_path (Union[str, Path]): Path to the PDF file.
            
        Returns:
            str: Extracted text content from the PDF.
            
        Note:
            This method reads the PDF page by page and concatenates the text.
        """
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text

    def read_docx(self, file_path: Union[str, Path]) -> str:
        """
        Extract text content from a DOCX file.
        
        Args:
            file_path (Union[str, Path]): Path to the DOCX file.
            
        Returns:
            str: Extracted text content from the DOCX file.
            
        Note:
            This method reads the document paragraph by paragraph and adds newlines between them.
        """
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def process_document(self, file_path: Union[str, Path]) -> List[str]:
        """
        Process a document file and split it into chunks.
        
        Args:
            file_path (Union[str, Path]): Path to the document file (PDF or DOCX).
            
        Returns:
            List[str]: List of text chunks from the document.
            
        Raises:
            ValueError: If the file type is not supported (not PDF or DOCX).
            
        Note:
            This method automatically detects the file type and uses the appropriate
            reader method before splitting the text into chunks.
        """
        file_path = Path(file_path)
        
        # Determine file type and extract text accordingly
        if file_path.suffix.lower() == '.pdf':
            text = self.read_pdf(file_path)
        elif file_path.suffix.lower() == '.docx':
            text = self.read_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        # Split the extracted text into chunks
        chunks = self.text_splitter.split_text(text)
        return chunks 