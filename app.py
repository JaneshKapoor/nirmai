import streamlit as st
import os
import tempfile
import requests
import json
import PyPDF2
import io
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Nirmai - Indian Budget 2025 Chatbot",
    page_icon="💰",
    layout="wide"
)

# Gemini API key
GEMINI_API_KEY = "AIzaSyCviEIIdHiZ0N2SWH5VsAlirsgcVVB7VmM"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def extract_text_from_pdf_path(pdf_path):
    """Extract text from a PDF file path."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def query_gemini(prompt, context, api_key):
    """Query the Gemini API with the given prompt and context."""
    url = f"{GEMINI_API_URL}?key={api_key}"
    
    # Construct the full prompt with context
    full_prompt = f"""
    Based on the following Indian Budget 2025 document content, please answer the question.
    
    Document content:
    {context}
    
    Question: {prompt}
    
    Please provide a detailed and accurate answer based only on the information in the document.
    If the information is not available in the documents, please state that clearly.
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        response_data = response.json()
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            if 'content' in response_data['candidates'][0] and 'parts' in response_data['candidates'][0]['content']:
                return response_data['candidates'][0]['content']['parts'][0]['text']
        return "Sorry, I couldn't generate a response."
    else:
        return f"Error: {response.status_code} - {response.text}"

def load_pdfs_from_directory(directory_path):
    """Load all PDFs from a directory."""
    loaded_pdfs = {}
    pdf_files = list(Path(directory_path).glob("*.pdf"))
    
    if not pdf_files:
        return loaded_pdfs
    
    for pdf_path in pdf_files:
        file_name = pdf_path.name
        if file_name not in st.session_state.pdf_contents:
            with st.spinner(f"Processing {file_name}..."):
                try:
                    pdf_content = extract_text_from_pdf_path(pdf_path)
                    loaded_pdfs[file_name] = pdf_content
                    st.success(f"Successfully processed '{file_name}'")
                except Exception as e:
                    st.error(f"Error processing '{file_name}': {str(e)}")
    
    return loaded_pdfs

# App title and description
st.title("Nirmai")
st.markdown("<h2 style='text-align: center; color: #2c3e50;'>Indian Budget 2025 Chatbot</h2>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin: 20px 0;'>
        <p style='font-size: 1.2em; color: #34495e;'>
            Ask questions about the Indian Budget 2025. I'll help you understand the key points and details.
        </p>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for PDF content
if 'pdf_contents' not in st.session_state:
    st.session_state.pdf_contents = {}

# Sidebar for PDF upload and directory loading
with st.sidebar:
    st.header("Load Budget Documents")
    
    # Option 1: Upload files directly
    st.subheader("Option 1: Upload Files")
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            if file_name not in st.session_state.pdf_contents:
                with st.spinner(f"Processing {file_name}..."):
                    pdf_content = extract_text_from_pdf(uploaded_file)
                    st.session_state.pdf_contents[file_name] = pdf_content
                st.success(f"Successfully processed '{file_name}'")
    
    # Option 2: Load from directory
    st.subheader("Option 2: Load from Directory")
    pdf_directory = st.text_input("Enter path to PDF directory", "cbdata")
    
    if st.button("Load PDFs from Directory"):
        if os.path.isdir(pdf_directory):
            new_pdfs = load_pdfs_from_directory(pdf_directory)
            st.session_state.pdf_contents.update(new_pdfs)
            if not new_pdfs:
                st.warning(f"No PDF files found in {pdf_directory}")
        else:
            st.error(f"Directory not found: {pdf_directory}")
    
    # Display PDF info
    if st.session_state.pdf_contents:
        st.header("Loaded Documents")
        st.info(f"Total documents loaded: {len(st.session_state.pdf_contents)}")
        for pdf_name, pdf_content in st.session_state.pdf_contents.items():
            with st.expander(f"{pdf_name} ({len(pdf_content) / 1000:.2f} KB)"):
                st.text(pdf_content[:300] + "..." if len(pdf_content) > 300 else pdf_content)
    
    # Option to clear all PDFs
    if st.session_state.pdf_contents:
        if st.button("Clear All Documents"):
            st.session_state.pdf_contents = {}
            st.experimental_rerun()

# Main chat interface
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about the Indian Budget 2025..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Check if any PDFs are uploaded
    if not st.session_state.pdf_contents:
        with st.chat_message("assistant"):
            st.error("Please upload budget documents first!")
            st.session_state.messages.append({"role": "assistant", "content": "Please upload budget documents first!"})
    else:
        # Get response from Gemini using all PDFs
        with st.chat_message("assistant"):
            with st.spinner("Searching through all documents..."):
                # Combine all PDF contents with document names
                combined_context = ""
                for pdf_name, pdf_content in st.session_state.pdf_contents.items():
                    combined_context += f"\n\n--- DOCUMENT: {pdf_name} ---\n{pdf_content[:50000]}"  # Limit content size
                
                # Get response based on all documents
                response = query_gemini(prompt, combined_context, GEMINI_API_KEY)
                
                # Display response with document count
                doc_count = len(st.session_state.pdf_contents)
                st.markdown(f"**Answering based on {doc_count} document{'s' if doc_count > 1 else ''}:**\n\n{response}")
                st.session_state.messages.append({"role": "assistant", "content": f"**Answering based on {doc_count} document{'s' if doc_count > 1 else ''}:**\n\n{response}"})

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 20px; margin-top: 50px; color: #7f8c8d;'>
        <p>Powered by Nirmai AI | Indian Budget 2025 Chatbot</p>
    </div>
""", unsafe_allow_html=True) 