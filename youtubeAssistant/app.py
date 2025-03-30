import streamlit as st
from youtubeTranscript_OpenAI import getSummary, getResponse,create_Youtube_vectors
import gc 
import uuid


st.title('Youtube Assistant')
st.write("This app uses OpenAI's GPT-3 to answer questions about a Youtube video.")

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}
    st.session_state.messages = []
    st.session_state.context = None
    st.session_state.summary = None
    st.session_state.url = None


session_id = st.session_state.id
client = None
query = ''
vectorDb =''

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

with st.sidebar:
    url = st.sidebar.text_input('Share the Url of the Youtube video', placeholder='https://youtube.com/xxxxxxxx',)
    if url and url != st.session_state.url: 
        st.session_state.url = url
        try:
            with st.spinner('Fetching Transcript'):
                st.session_state.vectorDb, st.session_state.summary = create_Youtube_vectors(url)
                st.markdown(f'You requested to know about this {url}')
                st.session_state.file_cache['summary'] = getSummary(st.session_state.summary)
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
st.sidebar.markdown(st.session_state.file_cache['summary'])


# Accept user input
if prompt := st.chat_input("What's up?"):
    
    if st.session_state.vectorDb is None:
        st.error("Please enter a valid Youtube URL")
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
        streaming_response = getResponse(st.session_state.vectorDb, prompt)
        
        for chunk in streaming_response.split(' '):
            full_response += chunk + ' '
            # Simulate typing delay
            message_placeholder.markdown(full_response + "▌")     

        message_placeholder.markdown(full_response)
        # st.session_state.context = ctx

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})