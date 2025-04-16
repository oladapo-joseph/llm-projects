import streamlit as st 
from youtube import create_Youtube_vectors ,check_If_Youtube, youtube_loader, save_youtube
from llm_worker import getResponse
from web2DB import url_loader
from common import save_to_vectorDB
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
    st.session_state.existing =[]
    st.session_state.db = None
    st.session_state.docs= None
    st.session_state.load_status= False
    st.session_state.url = []

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



# def pdf_():








with st.sidebar:

    source = st.selectbox('Select Data Source', options = data_sources, 
                          placeholder='Choose a data Source', index=None )

    if source:
        with st.form('data', clear_on_submit=True):
            if source.startswith('Youtube'):
                youtube_()
            
            st.form_submit_button('Load Youtube')

if st.session_state.load_status:
    st.markdown("Successful")