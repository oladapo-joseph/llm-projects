import streamlit as st
from youtubeTranscript_OpenAI import getSummary, getResponse,embeddings, template
import gc 
import uuid
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_core.prompts import PromptTemplate 
from langchain_community.vectorstores import  FAISS 
from youtube_transcript_api import YouTubeTranscriptApi 
from dotenv import load_dotenv 


load_dotenv('../.env')

st.title('Youtube Assistant')



if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None



query = ''
vectorDb =''

def create_Youtube_vectors(url:str)->FAISS: 
    
    def getId(url)->str:
        from urllib.parse import urlparse, parse_qs
        if url.startswith('http'):
            query = urlparse(url).query
            params = parse_qs(query)
            return params.get('v', [url.split('/')[-1]])[0]
        return url
    
    transcript= YouTubeTranscriptApi.get_transcript(getId(url))
    
    full_transcript = " ".join([i['text'] for i in transcript])

    # next thing is to split the transcript into documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                   chunk_overlap=200)
    docs = text_splitter.split_text(full_transcript)

    db = FAISS.from_texts(docs, embeddings)

    return db, docs

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()


with st.sidebar:
    url = st.sidebar.text_input('Share the Url of the Youtube video', placeholder='https://youtube.com/xxxxxxxx',)
    if url:
        try:
            with st.spinner('Fetching Transcript'):
                vectorDb, summary = create_Youtube_vectors(url)
                st.markdown(f'You requested to know about this {url}')
                st.session_state.file_cache['summary'] = getSummary(summary)
                st.success("Ready to Chat! View Summary Below")
                st.markdown(st.session_state.file_cache['summary'])
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

col1, col2 = st.columns([6, 1])

with col1:
    st.subheader("Chat with the AI")

with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What's up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Simulate stream of response with milliseconds delay
        streaming_response = getResponse(vectorDb, prompt)
        
        for chunk in streaming_response.split(' '):
            full_response += chunk
            full_response += ' '
            message_placeholder.markdown(full_response + "▌")

        

        message_placeholder.markdown(full_response)
        # st.session_state.context = ctx

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})