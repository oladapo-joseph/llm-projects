from common import FAISS, embeddings, check_FAISS, getChunks,get_Metadata
from langchain_community.document_loaders import UnstructuredURLLoader, PlaywrightURLLoader
from typing import List
from playwright.sync_api import sync_playwright



def url_loader(urls:List[str])->List:
    
    """
        Loads content from a list of URLs using different loaders.
        This function attempts to load content from the provided URLs using the 
        `UnstructuredURLLoader`. If the content cannot be loaded or is empty, it 
        falls back to using the `PlaywrightURLLoader` with specific configurations 
        to remove unnecessary elements like headers, footers, and navigation bars.
        Args:
            urls (List[str]): A list of URLs to load content from.
        Returns:
            List: A list of documents loaded from the URLs. Each document contains 
            the content of a webpage.
        Raises:
            ValueError: If no content is successfully loaded from the provided URLs.
        Exceptions:
            If an error occurs during the loading process, it prints an error message 
            and returns `None`.
    

    """
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
             
        return docs
    except Exception as e:
        print(f"Unable to load urls: {e}")
        return None 

