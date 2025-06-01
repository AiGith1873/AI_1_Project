# 🩹 Monkey-patch Streamlit to avoid touching torch.classes
import sys

# Prevent Streamlit from attempting to access torch.classes.__path__
import types
import torch

torch_classes_fake = types.ModuleType("torch.classes")
torch_classes_fake.__path__ = []
sys.modules["torch.classes"] = torch_classes_fake

import os
import streamlit as st
from pathlib import Path
import logging
import time

# --- Set environment variables from .env (if not already set) ---
from dotenv import load_dotenv
load_dotenv()

os.environ["HF_HOME"] = os.getenv("HF_HOME", os.path.expanduser("~/.cache/huggingface/hub"))
chroma_db_dir = os.getenv("CHROMA_DB_DIR", "chroma_db")

from src.components.rag_pipeline import RAGPipeline, RAGPipelineError
from src.components.llm_client import LLMClient, LLMError
from src.utils.document_processor import DocumentProcessor
from src.config.settings import DeploymentConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page settings
st.set_page_config(
    page_title="Financial Document RAG System",
    page_icon="📄",
    layout="wide"
)

# Display the main title and description
st.title("Financial Document RAG System")
st.markdown("""
This system allows you to query internal financial documents using natural language.
Upload your documents and ask questions about their contents.
""")

# Initialize components
try:
    rag_pipeline = RAGPipeline(persist_directory=chroma_db_dir)
    llm_client = LLMClient()
    document_processor = DocumentProcessor()
    
    # Log initialization
    config = DeploymentConfig.get_active_config()
    logger.info(f"Initialized with model: {config['model_name']}")
    logger.info(f"Using base URL: {config['base_url']}")
    
except Exception as e:
    st.error(f"❌ Failed to initialize components: {str(e)}")
    st.stop()

# File uploader for PDF/DOCX files
uploaded_files = st.file_uploader(
    "Upload your documents (PDF/DOCX)",
    type=['pdf', 'docx'],
    accept_multiple_files=True
)

# Text input for user queries
query = st.text_input("Ask a question about your documents:")

# Show upload status
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} document(s) uploaded successfully")
else:
    st.warning("⚠️ Please upload at least one document to proceed")

# Process the query if one is entered
if query:
    if not uploaded_files:
        st.error("❌ Please upload at least one document before asking a question")
    else:
        with st.spinner("Processing your query..."):
            try:
                # 1. Process uploaded documents and add to vector store
                uploaded_chunks = []
                for file in uploaded_files:
                    temp_path = Path("temp") / file.name
                    temp_path.parent.mkdir(exist_ok=True)
                    with open(temp_path, "wb") as f:
                        f.write(file.getvalue())
                    chunks = document_processor.process_document(temp_path)
                    rag_pipeline.add_documents(chunks, [{"source": file.name} for _ in chunks])
                    uploaded_chunks.extend(chunks)
                    temp_path.unlink()

                # 2. Query the vector store for relevant context (global search)
                relevant_docs = rag_pipeline.query(query)

                # 3. Hybrid context: always include uploaded chunks, plus global search results (no duplicates)
                context = []
                seen_contents = set()
                
                # Add all uploaded chunks first
                for chunk in uploaded_chunks:
                    if chunk not in seen_contents:
                        context.append(chunk)
                        seen_contents.add(chunk)
                
                # Add top global results (excluding duplicates)
                for doc in relevant_docs:
                    if doc.page_content not in seen_contents:
                        context.append(doc.page_content)
                        seen_contents.add(doc.page_content)

                # 4. Allow context to be empty (for debugging Ollama connection)
                if not context:
                    st.info("No relevant context found. Sending only your question to the LLM.")

                # 5. Generate response using LLM (RunPod/Ollama)
                response = llm_client.generate_response(
                    prompt=query,
                    context=context if context else None
                )
                st.success("✅ Response generated successfully")
                st.write("Response:", response["text"])

            except (RAGPipelineError, LLMError) as e:
                st.error(f"❌ Error: {e}")
                import traceback
                st.text(traceback.format_exc())
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {e}")
                import traceback
                st.text(traceback.format_exc()) 