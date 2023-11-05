import re
from io import BytesIO
from typing import Any, Dict, List
import docx2txt
import streamlit as st
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz


@st.cache_data
def parse_docx(file: BytesIO) -> str:
    text = docx2txt.process(file)
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text

@st.cache_data
def parse_txt(file: BytesIO) -> str:
    text = file.read().decode("utf-8")
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text

@st.cache_data
def text_to_docs(text: str | List[str] ) -> List[Document]:
    """Converts a string or list of strings to a list of Documents
    with metadata."""
    if isinstance(text, str):
        # Take a single string as one page
        text = [text]
    page_docs = [Document(page_content=page) for page in text]

    # Add page numbers as metadata
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    # Split pages into chunks
    doc_chunks = []

    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=0,
        )
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk, metadata={"page": doc.metadata["page"], "chunk": i}
            )
            # Add sources a metadata
            doc.metadata["source"] = f"{doc.metadata['page']}-{doc.metadata['chunk']}"
            doc_chunks.append(doc)
    return doc_chunks

def wrap_text_in_html(text: str | List[str]) -> str:
    """Wraps each text block separated by newlines in <p> tags"""
    if isinstance(text, list):
        # Add horizontal rules between pages
        text = "\n<hr/>\n".join(text)
    return "".join([f"<p>{line}</p>" for line in text.split("\n")])


def embed_docs_chroma(chroma_client, docs): 
        doc_chunks_list = [doc.page_content for doc in docs]
        id_list = [str(doc.metadata['chunk']) for doc in docs]
        source_list = [{"source": doc.metadata['source']} for doc in docs]
        try:
            chroma_client.delete_collection(name="app_collection")
            collection = chroma_client.create_collection(name="app_collection")
        except: 
            collection = chroma_client.create_collection(name="app_collection")
        try:
            collection.add(
                documents = doc_chunks_list,
                metadatas = source_list,
                ids = id_list)
        except Exception as e:
            print(f"Excpetion: {e}")
        return collection


@st.cache_data
def parse_pdf_v2(file) -> List[str]:
    #print(file)
    file_contents = file.read()
    pdf_file = BytesIO(file_contents)
    doc = fitz.open(stream= pdf_file, filetype="pdf")
    pages = sorted(doc, key=lambda page: page.number)  # Sort pages in ascending order
    extracted_text = []
    for page in pages:
        text_boxes = page.get_text("blocks")
        sorted_text_boxes = sorted(text_boxes, key=lambda box: (box[0]))  # Sort text boxes by x and y coordinates
        #print(sorted_text_boxes)
        for box in sorted_text_boxes:
            x, y, width, height, text, _, _ = box
            if "image" in text:
                print(text)
            else:
                extracted_text.append(text)
            
    #extracted_text = sorted(extracted_text, key=lambda item: item[1])  # Sort text by y-coordinate
    text = "".join(extracted_text)
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Fix newlines in the middle of sentences
    text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text

@st.cache_data
def parse_pdf_v3(file):
    #print(file)
    #file_contents = file.read()
    #pdf_file = BytesIO(file_contents)
    pdf_file = file
    doc = fitz.open(pdf_file)
    pages = sorted(doc, key=lambda page: page.number)  # Sort pages in ascending order
    extracted_text = []
    for page in pages:
        text_boxes = page.get_text("blocks")
        sorted_text_boxes = sorted(text_boxes, key=lambda box: (box[0]))  # Sort text boxes by x and y coordinates
        #print(sorted_text_boxes)
        for box in sorted_text_boxes:
            x, y, width, height, text, _, _ = box
            if "image" in text:
                print(text)
            else:
                extracted_text.append(text)
            
    #extracted_text = sorted(extracted_text, key=lambda item: item[1])  # Sort text by y-coordinate
    text = "".join(extracted_text)
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
    # Fix newlines in the middle of sentences
    text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
    # Remove multiple newlines
    text = re.sub(r"\n\s*\n", "\n\n", text)

    return text

@st.cache_data
def get_sources_v2(match_doc, documents):
    sources = []
    for doc in documents:
        if doc.page_content == match_doc:
            sources.append(doc.metadata['source'])
    return "Source: " + sources[0]

def search_docs_chroma(index, query):
    relevant_chunks = index.query(query_texts=[query], n_results = 5,)
    sources = []
    for i, chunk in enumerate(relevant_chunks['documents'][0]):
        print("=========")
        print("Paragraph index : ", relevant_chunks['ids'][0][i])
        print("Paragraph : ", chunk)
        sources.append(chunk)
    return sources
