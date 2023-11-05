import streamlit as st
from utils import (
    embed_docs_v2,
    parse_docx,
    parse_pdf_v2,
    parse_txt,
    text_to_docs,)

def clear_submit():
    st.session_state["submit"] = False

def sidebar():
    with st.sidebar:
        uploaded_files = st.file_uploader("Upload a pdf, docx, or txt file", 
                                          type=["pdf", "docx", "txt"],
                                          accept_multiple_files=True,
                                          help="Scanned documents are not supported yet!",
                                          on_change=clear_submit,)


