from typing import List
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

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
        self.persist_directory = persist_directory
        # Initialize the embedding model - using a lightweight but effective model
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        # Initialize ChromaDB vector store with the embedding model
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )

    def add_documents(self, texts: List[str], metadatas: List[dict] = None):
        """
        Add documents to the vector store for later retrieval.
        
        Args:
            texts (List[str]): List of text chunks to be added to the vector store
            metadatas (List[dict], optional): List of metadata dictionaries for each text chunk.
                                            If None, generates default metadata with source info.
        """
        if metadatas is None:
            metadatas = [{"source": f"document_{i}"} for i in range(len(texts))]
        
        # Add texts to vector store with their metadata
        self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
        # Persist changes to disk
        self.vectorstore.persist()

    def query(self, query: str, k: int = 3) -> List[str]:
        """
        Query the vector store for relevant documents based on semantic similarity.
        
        Args:
            query (str): The search query text
            k (int): Number of most relevant documents to return. Defaults to 3.
            
        Returns:
            List[str]: List of the k most relevant document chunks
        """
        # Perform similarity search and return the most relevant documents
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def clear(self):
        """
        Clear all documents from the vector store and reinitialize it.
        Useful for starting fresh or when you want to remove all stored documents.
        """
        # Delete the existing collection
        self.vectorstore.delete_collection()
        # Reinitialize the vector store
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        ) 