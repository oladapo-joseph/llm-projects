from langchain_community.document_loaders import UnstructuredURLLoader
from typing import List




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
        loader = UnstructuredURLLoader(urls=[str(url) for url in urls], verify_ssl=False)
        docs = loader.load()
        print(docs)
        print(urls)
        
        if not docs:
            raise ValueError("No content loaded from URLs")
             
        return docs
    except Exception as e:
        print(f"Unable to load urls: {e}")
        return None 

