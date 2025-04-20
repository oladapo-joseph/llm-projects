import os
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader

import pdfplumber

def load_document(file):
    """
    Loads and processes a PDF or text file using PyPDFLoader or TextLoader.

    Args:
        file: File-like object (e.g., from Streamlit file uploader).
        pwd (str, optional): Password for the PDF file, if encrypted. Defaults to None.
        headers (dict, optional): Additional headers for loading. Defaults to None.

    Returns:
        list: A list of documents or pages extracted from the file.
    """
    try:
        # Save the file to a temporary location
        temp_file_path = os.path.join("temp", file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_file_path, "wb") as f:
            f.write(file.read())

        # Use PyPDFLoader for PDFs
        if file.name.endswith('.pdf'):
            loader = PyPDFLoader(temp_file_path)
            print('Using PyPDFLoader for PDF')
        elif file.name.endswith('.txt'):
            loader = TextLoader(temp_file_path)
            print('Using TextLoader for TXT')
        else:
            raise ValueError("Unsupported file type")

        return loader.load()

    except Exception as e:
        print(f"Error loading document: {e}")
        return []

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)



