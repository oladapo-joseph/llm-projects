import streamlit as st 
from youtube2DB import check_If_Youtube, save_youtube
from llm_worker import getResponse
from web2DB import url_loader
from file import load_document
from common import save_to_vectorDB, check_FAISS
from uuid import uuid4
import gc



st.title('Cardy AI')
st.subheader("Your :blue[Cool AI] :sunglasses:")

if "id" not in st.session_state:
    st.session_state.id = uuid4()
    st.session_state.messages = []
    st.session_state.context = None
    st.session_state.summary = None
    st.session_state.output = None
    st.session_state.document = None
    st.session_state.db = None
    st.session_state.docs= None
    st.session_state.load_status= False
    st.session_state.url = []
    st.session_state.url_input = None


st.session_state.db  = check_FAISS()

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

# to select data source 
data_sources= ['Web Articles 📜', 'Youtube video ▶️', 'Pdf File 📂']


def youtube_():

    st.session_state.url = st.text_input('Enter the url below', placeholder='https://youtube.com/xxxxxx')
    st.markdown(st.session_state.url)
    if st.session_state.url:
        valid_url = check_If_Youtube(str(st.session_state.url))
        print('Status', valid_url)
        if valid_url: 
            st.session_state.db = save_youtube('link',[valid_url,st.session_state.url])
            st.session_state.load_status = True
            st.info('Youtube Loaded')
            st.session_state.url = ''
        else:
            st.error('Unable to load link')



def pdf_():
    st.session_state.document = st.file_uploader('Select File', type=['pdf', 'txt'])

    if st.session_state.document:
        data = [st.session_state.document, st.session_state.document.name]
        st.session_state.db = save_to_vectorDB('document',load_document,data)
        if st.session_state.db:
            st.info('Loaded')
        else:
            st.error('Unable to load pdf')




def handle_url_submit():
    """Handle URL form submission and clear input"""
    if st.session_state.url_input:
        if st.session_state.url_input not in st.session_state.url:
            st.session_state.url.append(st.session_state.url_input)
        st.session_state.url_input = ""  # Clear the input

def process_urls():
    """Process all URLs in the form"""
    with st.spinner('Processing URLs...'):
        try:

            db = save_to_vectorDB('url', url_loader, [st.session_state.url, st.session_state.url])
            if db:
                st.session_state.vectorDb = db
                st.success("Successfully processed articles")
                st.session_state.url = []  # Clear the URLs after processing
                st.rerun()
            else:
                st.error('Unable to process Urls') 
        except Exception as e:
            st.error(f"Error processing: {e}")


def articles_():
# Text input for new URL
    new_url = st.text_input(
        "Enter URL",
        placeholder="https://example.com/article",
        key="url_input",  # Use session state key
        value=st.session_state.url_input  # Bind to session state
    )
    # Add URL button inside form
    add_url = st.form_submit_button(
        "Add URL",
        on_click=handle_url_submit
    )
    if add_url and new_url:
        if new_url not in st.session_state.url:
            st.session_state.url.append(new_url)
        
def display_url():
        # Display added URLs with remove buttons
        
    if st.session_state.url:
        st.subheader("Added URLs:")
        
        for i, url in enumerate(st.session_state.url):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"{i+1}. {url[:30]}...")
            with col2:
                if st.button("❌", key=f"remove_{i}"):
                    st.session_state.url.pop(i)
                    st.rerun()
        
        # Process all URLs button
        
        if st.button("Process All URLs"):
            process_urls()
            




with st.sidebar:

    source = st.selectbox('Select Data Source', options = data_sources, 
                          placeholder='Choose a data Source', index=None )

    if source:
        with st.form('data', clear_on_submit=True):
            if source.startswith('Youtube'):
                youtube_()
                st.form_submit_button(f'Load {source}')    
            elif source.startswith('Pdf'):
                pdf_()
                st.form_submit_button(f'Load {source}')    
            else:
                pass
            
        if source.startswith('Web'): 
            with st.form('articles', clear_on_submit=True):
                articles_()
                
            display_url()
      


col1, col2 = st.columns([6, 1])

with col1:
    st.subheader("Chat with the AI")

with col2:
    st.button("Clear 🗑️", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's up?"):
    
    if st.session_state.db is None:
        st.error("Please enter a valid link to the article.")
        st.stop()
    
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
        streaming_response = getResponse(prompt, st.session_state.db)
        
        for chunk in streaming_response.split(' '):
            full_response += chunk + ' '
            # Simulate typing delay
            message_placeholder.markdown(full_response + "▌")     

        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})