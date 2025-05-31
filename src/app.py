import streamlit as st
from pathlib import Path

# Configure the Streamlit page settings
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

# Create a file uploader component that accepts multiple PDF and DOCX files
uploaded_files = st.file_uploader(
    "Upload your documents (PDF/DOCX)",
    type=['pdf', 'docx'],
    accept_multiple_files=True
)

# Create a text input field for user queries
query = st.text_input("Ask a question about your documents:")

# Process the query if one is entered
if query:
    st.write("Processing your query...")
    # TODO: Implement RAG pipeline
    # This section will be updated to:
    # 1. Process uploaded documents
    # 2. Generate embeddings
    # 3. Query the vector store
    # 4. Display results with source documents
    st.write("This is where the RAG results will appear.") 