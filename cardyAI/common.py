from central_import import embeddings, FAISS, RecursiveCharacterTextSplitter,List, PromptTemplate, ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser



def get_Metadata(db: FAISS) -> list:
    """
    Extract source URLs from FAISS database.
    
    Args:
        db: FAISS vector store instance
        
    Returns:
        list: List of source URLs from document metadata
    """
    try:
        # Retrieve documents using their ids
        sources = [db.docstore.search(doc_id).metadata['source'] for doc_id in list(db.index_to_docstore_id.values())]
        
        # Extract source URLs from metadata
        return set(sources)
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return []


def getSummary(docs)->str:
    """
    Summarizes the provided text or list of texts into a concise format.
    Args:
        docs (str or list): The input text or a list of text strings to be summarized.
    Returns:
        str: A summary of the input text(s) in less than 100 words.
    """


    if type(docs) == list:
        newdocs=  " ".join(i for i in docs)
    else:
        newdocs =docs 

    llm = ChatGoogleGenerativeAI(temperature=0.4, streaming=True)

    prompt = PromptTemplate(
        input_variables=['file'],
        template= '''
            You are a good writer.

            Summarize this transcript: {file}
            Do this in less than 100 words.
'''
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({'file':newdocs})
    return response


def getChunks(docs:List[str]) -> List:
    """
    Takes a list of documents and splits .
    
    Args:
        docs: List of URLs to process
    Returns:
        List: List of document chunks
    """
    try:    
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.'],
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(docs)
        
        if not split_docs:
            raise ValueError("No chunks created from documents")
            
        print(f"Created {len(split_docs)} chunks from {len(docs)} documents")
        return split_docs
        
    except Exception as e:
        print(f"Error in getChunks: {e}")
        return []


def load_local():
    return FAISS.load_local('faiss_index', embeddings=embeddings, 
                     allow_dangerous_deserialization=True)
    

def check_FAISS()->bool:
    """
    This function checks if the FAISS database is empty or not.
    """
    try:
        # print('loaded')
        return load_local()
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None


def save_to_vectorDB(datatype: str, loader, data_source: list[str] | str = None) -> FAISS:
    """
    Takes a list of sources (URLs or PDFs) and returns a FAISS vector database.
    
    Args:
        datatype: Type of source ('url' or document {'pdf' or 'text'}).
        loader: Function to load documents from the source.
        data_source: List or single source (URLs or PDFs) to process.
        
    Returns:
        FAISS: Vector database containing the processed documents.
    """
    try:
        # Ensure data_source is a list
        if len(data_source)<2:
            data_ = source = data_source
        else:
            data_,  source = data_source
        if isinstance(source, str):
            source = [source]

        db = check_FAISS()
        if db:
            old_sources = get_Metadata(db)
            new_sources = [src for src in source if src not in old_sources]

            if not new_sources:
                print(f"No new {datatype}s to process. Using existing data...")
                return db

            print(f"Found {len(new_sources)} new {datatype}s to process...")
            print(new_sources[:5])
            docs = loader(data_)

            if not docs:
                print(f"No {datatype}s loaded.")
                return None

            split_docs = getChunks(docs)
            if not split_docs:
                raise ValueError("No text chunks were created from the documents.")

            print(f"Adding {len(split_docs)} new documents to the index...")
            db.add_documents(split_docs)
            db.save_local('faiss_index')
            print('done adding documents')
            return db
        else:
            print(f"Creating new FAISS index with {len(data_source)} {datatype}s...")
            docs = loader(data_source)

            if not docs:
                print(f"No {datatype}s loaded.")
                return None

            split_docs = getChunks(docs)
            if not split_docs:
                raise ValueError("No text chunks were created from the documents.")

            db = FAISS.from_documents(documents=split_docs, embedding=embeddings)
            db.save_local('faiss_index')
            print('done adding')
            return db

    except ValueError as e:
        print(f"Error processing {datatype}s: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

