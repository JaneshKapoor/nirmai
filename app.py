import streamlit as st
import os
from utils.pdf_loader import load_pdfs_from_directory
from utils.model_setup import setup_model
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chain" not in st.session_state:
    st.session_state.chain = None
if "error" not in st.session_state:
    st.session_state.error = None

def check_api_key():
    """Check if the Google API key is properly set up."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("""
            ⚠️ Google API Key not found! Please follow these steps:
            
            1. Create a `.env` file in your project root if you haven't already
            2. Add your Google API key to the `.env` file like this:
               ```
               GOOGLE_API_KEY=your_api_key_here
               ```
            3. Get your API key from: https://makersuite.google.com/app/apikey
            4. Restart the application after adding the API key
        """)
        return False
    return True

def initialize_model():
    """Initialize the model and load documents if not already done."""
    if not check_api_key():
        return
    
    if st.session_state.chain is None:
        try:
            with st.spinner("Loading budget documents and initializing the model..."):
                # Load PDFs from the cbdata directory
                documents = load_pdfs_from_directory("cbdata")
                # Setup the model
                st.session_state.chain = setup_model(documents)
                st.success("Model initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing the model: {str(e)}")
            st.session_state.error = str(e)

def main():
    st.set_page_config(
        page_title="Nirmai - Indian Budget 2025 Chatbot",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stTitle {
            color: #1f77b4;
            text-align: center;
        }
        .stMarkdown {
            font-size: 1.1em;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("<h1 class='stTitle'>Nirmai</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>Indian Budget 2025 Chatbot</h2>", unsafe_allow_html=True)
    
    # Description
    st.markdown("""
        <div style='text-align: center; padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin: 20px 0;'>
            <p style='font-size: 1.2em; color: #34495e;'>
                Ask questions about the Indian Budget 2025. I'll help you understand the key points and details.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Initialize the model
    initialize_model()

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
        if prompt := st.chat_input("Ask a question about the Indian Budget 2025"):
            if st.session_state.error:
                st.error("Please fix the API key issue before asking questions.")
                return

            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get bot response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.chain({"question": prompt})
                        st.markdown(response["answer"])
                        
                        # Display source documents if available
                        if response.get("source_documents"):
                            with st.expander("View Sources"):
                                for doc in response["source_documents"]:
                                    st.markdown(f"**Source:** {doc.metadata['source']}")
                                    st.markdown(doc.page_content)
                                    st.divider()

                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response["answer"]})
                    except Exception as e:
                        st.error(f"Error getting response: {str(e)}")

    # Footer
    st.markdown("""
        <div style='text-align: center; padding: 20px; margin-top: 50px; color: #7f8c8d;'>
            <p>Powered by Nirmai AI | Indian Budget 2025 Chatbot</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 