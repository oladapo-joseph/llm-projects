from langchain_community.document_loaders import PyPDFLoader, TextLoader

def load_document(file,pwd=None,headers=None):
    """
        Loads and processes a PDF file using the PyPDFLoader.
        Args:
            pdf (list): The file path or file-like object of the PDF to be loaded.
            pwd (str, optional): The password for the PDF file, if it is encrypted. Defaults to None.
            headers (dict, optional): Additional headers to be used during the loading process. Defaults to None.
        Returns:
            list: A list of documents or pages extracted from the PDF.
    
    """
    try:
        loader = PyPDFLoader(file[0],password=pwd, headers=headers, mode='single')
    except:
        loader = TextLoader(file[0])

    return loader.load()
    


