import streamlit as st
from youtubeTranscript_OpenAI import getSummary, getResponse,create_Youtube_vectors


st.title('Youtube Assistant')
st.subheader('Here to help you with your videos')

with st.sidebar:
    with st.form(key='ikform'):
        url = st.sidebar.text_input('Share the Url of the Youtube video', placeholder='https://youtube.com/xxxxxxxx',)

query = ''
vectorDb =''
if url:
    with st.spinner('Fetching Transcript'):
        vectorDb, summary = create_Youtube_vectors(url)
        st.markdown(f'You requested to know about this {url}')
        st.markdown('---')
        st.markdown(f'Video Summary:')
        st.markdown(f'{getSummary(summary)}')
        st.markdown('---')
        st.markdown('What would you like to know about the video?')
        query = st.sidebar.text_area("You can type your question here")
else:
    st.info('Please enter a Url link')

if query:
    response =getResponse(vectorDb, query)
    with st.spinner('Answering your question'):
        try: 
            st.session_state['prompt_result'] = response 
        except Exception as e:
            st.error(f'Error fetching response, {str(e)}')

    if 'prompt_result' in st.session_state:
        st.markdown(st.session_state['prompt_result'])
    else:
        st.info("What would you like to know about the video.")


