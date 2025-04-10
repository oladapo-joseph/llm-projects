import streamlit as st
import pandas as pd
from graphGen import create_graph
from agentx import AgentState 
from response_gen import generate_report
import gc 
# filepath: c:/Users/HP/Desktop/nlp projects/csv_analysis/app.py

# Initialize session state for the app
if "id" not in st.session_state:
    st.session_state.messages = []
    st.session_state.context = None
    st.session_state.summary = None
    st.session_state.output = None

if 'agent_state' not in st.session_state:
        st.session_state.agent_state = AgentState(
            python_code="",
            final_answer="",
            df=None,
            exception="",
            df_head="",
            df_columns=[],
            question="",
            code_valid=False,
            error=False,
            next_state="getFile",
            retries=0,
            max_retries=3,
        )


def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

# Streamlit app layout
st.title("CSV Data Analysis Assistant")
st.write("Upload a CSV file and ask questions about your data.")

# File upload
with st.sidebar:
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        # Load the CSV file into a DataFrame
        with st.spinner('Processing File...'):
            print("Current state:", st.session_state.agent_state['next_state'])
            st.session_state.agent_state["df"] = pd.read_csv(uploaded_file)
            st.session_state.agent_state["df"] = st.session_state.agent_state["df"].dropna(axis=1, how="all")
            st.session_state.agent_state["df_head"] = str(st.session_state.agent_state["df"].sample(30).to_markdown())
            st.session_state.agent_state["df_columns"] = st.session_state.agent_state["df"].columns.tolist()
            # st.session_state.agent_state["next_state"] = "get_question"

        st.write("File uploaded successfully! Here's a preview of your data:")
        st.dataframe(st.session_state.agent_state["df"].head(), use_container_width=True)

# Question input
def get_question(prompt):
    st.session_state.agent_state['question'] = prompt
        
# Workflow execution
def startWorkflow():
    if st.session_state.agent_state['df'] is not None:
        # Initialize the graph and start the workflow
        print("Current state:", st.session_state.agent_state['next_state'])
        graph = create_graph()
        st.session_state.output = graph.invoke(st.session_state.agent_state)

        # Display the final answer
        if st.session_state.agent_state["exception"]:
            st.error("An error occurred:")
            st.write(st.session_state.agent_state['exception'])


col1, col2 = st.columns([6, 1])

with col1:
    st.subheader("Chat with the AI")

with col2:
    st.button("Clear ↺", on_click=reset_chat)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's do you want to know?"):
    
    if st.session_state.agent_state['df'] is None:
        st.error("Please upload a file first.")
        st.stop()
    get_question(prompt)
    print("Current state:", st.session_state.agent_state['next_state'])
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    startWorkflow()
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        if st.session_state.output:
        
        # Simulate stream of response with milliseconds delay
            streaming_response = generate_report(
                                            st.session_state.agent_state['question'],
                                            st.session_state.output
                                                )
            
            for chunk in streaming_response.split(' '):
                full_response += chunk + ' '
                # Simulate typing delay
                message_placeholder.markdown(full_response + "▌")     

        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})