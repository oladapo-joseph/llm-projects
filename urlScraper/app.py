import streamlit as st
from llm_worker import getResponse
from urlScraper.web2DB import Url_to_vectorDB, checkFAISS
from dotenv import load_dotenv
import gc 
import uuid


# the idea is to have links to add resources to the vector database and also interact with the chatgpt model

st.title('Research Assistant')
st.write("This app uses OpenAI's GPT-3 to answer questions about any research article.")

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}
    st.session_state.messages = []
    st.session_state.context = None
    st.session_state.summary = None
    st.session_state.url = []
    st.session_state.vectorDb = checkFAISS()



session_id = st.session_state.id
client = None
query = ''
vectorDb =''

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()
if 'url_input' not in st.session_state:
    st.session_state.url_input = ""

def handle_url_submit():
    """Handle URL form submission and clear input"""
    if st.session_state.url_input:
        if st.session_state.url_input not in st.session_state.url:
            st.session_state.url.append(st.session_state.url_input)
        st.session_state.url_input = ""  # Clear the input

@st.fragment
def process_urls():
    """Process all URLs in the form"""
    with st.spinner('Processing URLs...'):
        try:
            db = Url_to_vectorDB(st.session_state.url)
            if db:
                st.session_state.vectorDb = db
                st.success(f"Successfully processed articles")
                st.session_state.url = []  # Clear the URLs after processing
                
        except Exception as e:
            st.error(f"Error processing: {e}")

with st.sidebar:
    st.subheader("Add Research Articles")
    
    # Create a form
    with st.form(key="url_form"):
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
    
    # Display added URLs with remove buttons
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
    if st.session_state.url:
        if st.button("Process All URLs"):
            process_urls()
            


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
    
    if st.session_state.vectorDb is None:
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
        streaming_response = getResponse(prompt, st.session_state.vectorDb,6)
        
        for chunk in streaming_response.split(' '):
            full_response += chunk + ' '
            # Simulate typing delay
            message_placeholder.markdown(full_response + "▌")     

        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})