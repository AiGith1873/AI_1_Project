"""
RAG Pipeline for document processing and retrieval.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
from functools import wraps
import os
from langchain.schema import Document

# LangChain imports
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

def with_timeout(timeout_seconds: int = 30):
    """Decorator to add timeout to functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            if time.time() - start_time > timeout_seconds:
                raise TimeoutError(f"Operation timed out after {timeout_seconds} seconds")
            return result
        return wrapper
    return decorator

class RAGPipelineError(Exception):
    """Custom exception for RAG pipeline errors."""
    pass

def error_handler(func):
    """Decorator for error handling in RAG pipeline methods."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            raise RAGPipelineError(error_msg)
    return wrapper

class RAGPipeline:
    """
    A Retrieval-Augmented Generation (RAG) pipeline that combines document retrieval with language model generation.
    This class handles document storage, embedding, and retrieval using ChromaDB as the vector store.
    """
    def __init__(self, persist_directory: str = "chroma_db"):
        """
        Initialize the RAG pipeline with a vector store and embedding model.
        
        Args:
            persist_directory (str): Directory where the vector store will be persisted.
                                    Defaults to "chroma_db" in the current directory.
        """
        self.logger = logging.getLogger(__name__)
        self.persist_directory = str(Path(persist_directory).expanduser().absolute())
        
        try:
            # Initialize embedding model
            self.logger.info(f"Initializing RAG pipeline with persist directory: {self.persist_directory}")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Initialize vector store
            self.logger.info("Initializing ChromaDB vector store")
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            self.logger.info("RAG pipeline initialization complete")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
            raise RAGPipelineError(f"RAG pipeline initialization failed: {str(e)}")

    @with_timeout(timeout_seconds=60)
    @error_handler
    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Add documents to the vector store for later retrieval.
        
        Args:
            texts (List[str]): List of text chunks to be added to the vector store
            metadatas (List[Dict[str, Any]], optional): List of metadata dictionaries for each text chunk.
            
        Raises:
            RAGPipelineError: If document addition fails
            TimeoutError: If operation takes too long
        """
        if not texts:
            logger.warning("No documents provided to add_documents")
            return

        logger.info(f"Adding {len(texts)} documents to vector store")
        if metadatas is None:
            metadatas = [{"source": f"document_{i}"} for i in range(len(texts))]
            logger.debug(f"Generated default metadata for {len(texts)} documents")
        
        try:
            # Create documents with metadata
            documents = [
                Document(page_content=text, metadata=metadata)
                for text, metadata in zip(texts, metadatas)
            ]
            
            # Add documents to vector store
            self.vector_store.add_documents(documents)
            logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            error_msg = f"Error adding documents to vector store: {str(e)}"
            logger.error(error_msg)
            raise RAGPipelineError(error_msg)

    @with_timeout(timeout_seconds=30)
    @error_handler
    def query(self, query: str, k: int = 4) -> List[Document]:
        """
        Query the vector store for relevant documents based on semantic similarity.
        
        Args:
            query (str): The search query text
            k (int): Number of most relevant documents to return. Defaults to 4.
            
        Returns:
            List[Document]: List of the k most relevant document chunks
            
        Raises:
            RAGPipelineError: If query fails
            TimeoutError: If operation takes too long
        """
        if not query.strip():
            logger.warning("Empty query received")
            return []

        logger.info(f"Processing query: {query}")
        logger.debug(f"Search parameters: k={k}")
        
        try:
            # Perform similarity search
            logger.debug("Performing similarity search")
            results = self.vector_store.similarity_search(query, k=k)
            
            # Extract and log results
            logger.info(f"Found {len(results)} relevant documents for query")
            logger.debug(f"Retrieved documents: {results}")
            
            return results
        except Exception as e:
            error_msg = f"Error querying vector store: {str(e)}"
            logger.error(error_msg)
            raise RAGPipelineError(error_msg)

    @error_handler
    def clear(self) -> None:
        """
        Clear all documents from the vector store and reinitialize it.
        
        Raises:
            RAGPipelineError: If clearing fails
        """
        logger.info("Clearing vector store")
        try:
            # Delete the existing collection
            logger.debug("Deleting existing collection")
            self.vector_store.delete_collection()
            
            # Reinitialize the vector store
            logger.debug("Reinitializing vector store")
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            logger.info("Successfully cleared and reinitialized vector store")
        except Exception as e:
            error_msg = f"Error clearing vector store: {str(e)}"
            logger.error(error_msg)
            raise RAGPipelineError(error_msg)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dict[str, Any]: Statistics about the vector store
        """
        try:
            collection = self.vector_store._collection
            return {
                "total_documents": collection.count(),
                "embedding_dimension": collection.dimension,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            return {
                "error": str(e),
                "persist_directory": self.persist_directory
            } 