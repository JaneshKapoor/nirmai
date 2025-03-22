import os
from typing import List
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import streamlit as st

def load_pdfs_from_directory(directory_path: str) -> List[Document]:
    """
    Load all PDF files from a directory and convert them to LangChain documents.
    """
    documents = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    
    # Get list of PDF files
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    
    if not pdf_files:
        st.warning(f"No PDF files found in {directory_path}")
        return documents
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, filename in enumerate(pdf_files):
        status_text.text(f"Processing {filename}...")
        file_path = os.path.join(directory_path, filename)
        
        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    chunks = text_splitter.split_text(text)
                    for chunk in chunks:
                        documents.append(Document(
                            page_content=chunk,
                            metadata={
                                "source": filename,
                                "page": page_num + 1,
                                "total_pages": total_pages
                            }
                        ))
            
            # Update progress
            progress = (idx + 1) / len(pdf_files)
            progress_bar.progress(progress)
            
        except Exception as e:
            st.error(f"Error processing {filename}: {str(e)}")
            continue
    
    status_text.text("Document processing complete!")
    return documents 