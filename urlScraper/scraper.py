from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import UnstructuredURLLoader, PlaywrightURLLoader, UnstructuredHTMLLoader
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain_openai import ChatOpenAI 
from langchain_huggingface import HuggingFaceEmbeddings 
from typing import List, Optional
from playwright.sync_api import sync_playwright

import os ,sys


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def Url_to_vectorDB(urls: list[str]) -> FAISS:
    """
    Takes a list of URLs and returns a FAISS vector database.
    
    Args:
        urls: List of URLs to process
        
    Returns:
        FAISS: Vector database containing the processed documents
    """
    try:
        # Ensure urls is a list
        if isinstance(urls, str):
            urls = [urls]
        db = checkFAISS() 
        if db:
            old_urls = getMetaData(db)
            new_urls = [url for url in urls if url not in old_urls]
            if not new_urls:
                print("No new URLs to process. using old data...")
                return db

            print(f"Found {len(new_urls)} new URLs to process...")
            split_docs = getChunks(new_urls)
            if not split_docs:
                raise ValueError("No text chunks were created from the documents")

            print(f"Adding {len(split_docs)} new documents to index...")
            db.add_documents(split_docs)
            db.save_local('../faiss_index') 
            return db
        else:   
        # Create new database
            print(f"Creating new FAISS index with {len(urls)} urls...")
            db = FAISS.from_documents(
                                        documents=getChunks(urls),
                                        embedding=embeddings
                                    )
            db.save_local('../faiss_index')
            return FAISS.load_local('../faiss_index', 
                            embeddings, 
                            allow_dangerous_deserialization=True )

    except ValueError as e:
        print(f"Error processing documents: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def getChunks(urls: List[str]) -> List:
    """
    Takes a list of URLs and returns a list of text chunks.
    
    Args:
        urls: List of URLs to process
    Returns:
        List: List of document chunks
    """
    # First try UnstructuredURLLoader
    try:
        loader = UnstructuredURLLoader(urls=urls, verify_ssl=False)
        docs = loader.load()
        
        if not docs or docs[0].page_content.strip() == '':
            print("Trying PlaywrightURLLoader...")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                loader = PlaywrightURLLoader(
                                urls=urls,
                                remove_selectors=["header", "footer", "nav"],
                                continue_on_failure=True,
                                headless=True
                            )
                docs = loader.load()
                print(docs)
                browser.close()
        
        if not docs:
            raise ValueError("No content loaded from URLs")
            
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.'],
            chunk_size=500,
            chunk_overlap=100
        )
        split_docs = text_splitter.split_documents(docs)
        
        if not split_docs:
            raise ValueError("No chunks created from documents")
            
        print(f"Created {len(split_docs)} chunks from {len(docs)} documents")
        return split_docs
        
    except Exception as e:
        print(f"Error in getChunks: {e}")
        return []


def checkFAISS()->bool:
    """
    This function checks if the FAISS database is empty or not.
    """
    try:
        print('loaded')
        return FAISS.load_local('../faiss_index', embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None


def getMetaData(db: FAISS) -> list:
    """
    Extract source URLs from FAISS database.
    
    Args:
        db: FAISS vector store instance
        
    Returns:
        list: List of source URLs from document metadata
    """
    try:
        # Retrieve documents using their ids
        url_sources = [db.docstore.search(doc_id).metadata['source'] for doc_id in list(db.index_to_docstore_id.values())]
        
        # Extract source URLs from metadata
        return set(url_sources)
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return []

"""
if __name__ == "__main__":
    sys.argv[0] = os.path.basename(__file__)
    urls = sys.argv[1:]
    if not urls:
        print("Please provide a list of URLs to process.")
        sys.exit(1)
    urls = [url.strip() for url in urls if url.strip()]  # Remove empty strings

    print(Url_to_vectorDB(urls))
"""    # Example usage:
    #python scraper.py "https://www.youtube.com/watch?v=example1" "https://www.youtube.com/watch?v=example2"
