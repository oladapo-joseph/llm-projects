from youtube_transcript_api import YouTubeTranscriptApi
from central_import import (FAISS, 
                    embeddings, ChatGoogleGenerativeAI, 
                    RecursiveCharacterTextSplitter)
from common import check_FAISS, get_Metadata, getChunks
from langchain_core.prompts import PromptTemplate 
from langchain_core.output_parsers import StrOutputParser




def check_If_Youtube(url) -> str:
    from urllib.parse import urlparse, parse_qs
    if url.startswith('http'):
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc:
            query = parse_qs(parsed_url.query)
            return query.get('v', [None])[0]
        elif 'youtu.be' in parsed_url.netloc:
            return parsed_url.path.lstrip('/')
    elif url.startswith('youtu.be/'):
        return url.split('/')[-1]
    return False

def create_Youtube_vectors(youtubeID:str, url)->FAISS: 
    
    

    print('valid')
    transcript= YouTubeTranscriptApi.get_transcript(youtubeID)

    full_transcript = " ".join([i['text'] for i in transcript])

    # next thing is to split the transcript into documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                chunk_overlap=200)
    docs = text_splitter.split_text(full_transcript)

    db = FAISS.from_texts(docs, embeddings, metadatas=[{'source':url} for i in range(len(docs))])

    return db, docs

def youtube_loader(youtubeID:str)->FAISS: 
    
    transcript= YouTubeTranscriptApi.get_transcript(youtubeID)

    full_transcript = " ".join([i['text'] for i in transcript])

    return full_transcript

def youtube_chunks(full_transcript):

    # next thing is to split the transcript into documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                chunk_overlap=200)
    docs = text_splitter.split_text(full_transcript)

    return  docs



def save_youtube(datatype: str, data_: list[str] = None) -> FAISS:

    try:
        # Ensure data_ is a list
        data_, url = data_
        db = check_FAISS()
        if db:
            old_s = get_Metadata(db)
            new_s = url if url not in old_s else None

            if not new_s:
                print(f"No new {datatype}s to process. Using existing data...")
                return db

            print(f"Found {len(new_s)} new {datatype}s to process...")
            docs = youtube_loader(new_s)
            if not docs:
                raise ValueError(f"No {datatype}s loaded.")

            split_docs = youtube_chunks(docs)
            if not split_docs:
                raise ValueError("No text chunks were created from the documents.")

            print(f"Adding {len(split_docs)} new documents to the index...")
            db.add_documents(split_docs)
            db.save_local('faiss_index')
            return db
        else:
            print(f"Creating new FAISS index with {len(data_)} {datatype}s...")
            
            docs = youtube_loader(data_)
            
            if not docs:
                raise ValueError(f"No {datatype}s loaded.")

            split_docs = youtube_chunks(docs)
            if not split_docs:
                raise ValueError("No text chunks were created from the documents.")

            db = FAISS.from_texts(docs, embeddings, metadatas=[{'source':url} for i in range(len(docs))])
            db.save_local('faiss_index')
            
            return db

    except ValueError:
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


