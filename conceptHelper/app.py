from prompter import generate_code 
import streamlit as st 


st.title('Code generation')

language  = st.sidebar.selectbox('Which language do you want to learn about?', 
                                 ('C#', "Python", 'Javascript'),index=None,
                                  placeholder='Choose an option',)
concept = ''
if language:
    concept = st.sidebar.text_input(f'What concept do you want to see in {language}',max_chars=20)
    st.markdown(f'You will like to know about {language}')

else:
    st.markdown('Please Select a language')
st.markdown('---')
if concept:
    with st.spinner('Generating code'):
        try:    
            st.markdown(f'You want to learn about {concept} in {language}')
            st.markdown('---')
            st.session_state['prompt_result'] = generate_code(language, concept)
        except Exception as e:
            st.error(f'Error fetching response, {str(e)}')

if 'prompt_result' in st.session_state:
    st.markdown(st.session_state['prompt_result'])
else:
    st.info("Pick a language and select a concept.")


