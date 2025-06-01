"""
Script to generate historical financial documents for the RAG system's knowledge base.
These documents represent historical policies, contracts, and agreements that the system
will search through when answering queries.
"""

import os
import sys
from pathlib import Path

# Add the scripts directory to the Python path
scripts_dir = str(Path(__file__).parent.parent)
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

from rag_data.document_generator import HistoricalDocumentGenerator

def main():
    """Generate historical documents for the RAG system."""
    # Define output directory
    output_dir = "data/rag_documents"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize document generator
    generator = HistoricalDocumentGenerator(output_dir=output_dir)
    
    # Clear existing documents
    print("Clearing existing historical documents...")
    for file in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, file))
    
    # Generate documents
    print("\nGenerating historical documents...")
    generated_files = []
    
    # Generate historical leasing agreements (from past 2 years)
    print("\nGenerating historical leasing agreements...")
    for i in range(20):
        try:
            filename = generator.create_leasing_agreement()
            generated_files.append(filename)
            print(f"Generated historical leasing agreement: {filename}")
        except Exception as e:
            print(f"Error generating leasing agreement: {e}")
    
    # Generate historical credit policies
    print("\nGenerating historical credit policies...")
    for i in range(10):
        try:
            filename = generator.create_credit_policy()
            generated_files.append(filename)
            print(f"Generated historical credit policy: {filename}")
        except Exception as e:
            print(f"Error generating credit policy: {e}")
    
    # Print summary
    print("\nHistorical Document Generation Summary:")
    print(f"Total documents generated: {len(generated_files)}")
    print(f"Output directory: {os.path.abspath(output_dir)}")
    print("\nGenerated files:")
    for file in generated_files:
        print(f"- {file}")
    
    print("\nThese documents will be used as the knowledge base for the RAG system.")
    print("They represent historical policies and agreements that the system will search through.")

if __name__ == "__main__":
    main() 