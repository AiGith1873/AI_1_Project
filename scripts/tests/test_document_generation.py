"""
Test script for document generation functionality.
Verifies that both historical and test documents are created correctly.
"""

import os
import pytest
from rag_data.document_generator import HistoricalDocumentGenerator
from test_data.generate_test_queries import generate_test_documents

def test_historical_document_generation():
    """Test that historical documents are generated successfully."""
    # Setup
    test_dir = "test_historical_docs"
    generator = HistoricalDocumentGenerator(output_dir=test_dir)
    
    try:
        # Generate historical documents
        leasing_agreement = generator.create_leasing_agreement()
        credit_policy = generator.create_credit_policy()
        
        # Verify files exist
        assert os.path.exists(os.path.join(test_dir, leasing_agreement))
        assert os.path.exists(os.path.join(test_dir, credit_policy))
        
        # Verify file sizes (basic check that files are not empty)
        assert os.path.getsize(os.path.join(test_dir, leasing_agreement)) > 0
        assert os.path.getsize(os.path.join(test_dir, credit_policy)) > 0
        
        # Verify file names contain expected prefixes
        assert "historical_leasing_agreement" in leasing_agreement
        assert "historical_credit_policy" in credit_policy
        
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                os.remove(os.path.join(test_dir, file))
            os.rmdir(test_dir)

def test_test_document_generation():
    """Test that test query documents are generated successfully."""
    # Setup
    test_dir = "test_query_docs"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        # Generate test documents
        test_files = generate_test_documents(num_docs=2)  # Generate 2 documents for testing
        
        # Verify files exist
        for file in test_files:
            assert os.path.exists(file)
            assert os.path.getsize(file) > 0
            
            # Verify file names contain expected content
            assert "current_report" in file
            assert any(ext in file for ext in ['.pdf', '.docx'])
            
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            for file in os.listdir(test_dir):
                os.remove(os.path.join(test_dir, file))
            os.rmdir(test_dir)

if __name__ == "__main__":
    pytest.main([__file__]) 