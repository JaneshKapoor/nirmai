import streamlit as st

def main():
    st.set_page_config(
        page_title="Nirmai App",
        page_icon="✨",
        layout="wide"
    )

    st.title("Welcome to Nirmai")
    st.write("This is a new Streamlit application.")

if __name__ == "__main__":
    main() 