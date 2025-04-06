from langchain_openai import ChatOpenAI
import pandas as pd
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.agents.agent_toolkits.python.base import create_python_agent
from langchain_experimental.utilities import PythonREPL
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain.agents import AgentType
from agentx import AgentState
from langgraph.graph import StateGraph, START, END 
import pandas as pd

load_dotenv('.env')  # Load environment variables from .env file

def generate_code(state:AgentState) -> AgentState:
    prompt = PromptTemplate(
        input_variables=['columns', 'head', 'question'],
        template="""
        
        You are an expert data scientist and a helpful assistant that can analyze CSV files."),
    
        I have a CSV file with the following columns: {columns}. 
        Here are 10 random rows from the file: {head}. 
        Use this as context to understand how the actual table looks like ensure you use the date 
        in the data as your reference date and use it to answer the following question.
        {question} 
        
        1. Write a python script that shows how to answer the question using STRICTLY the above context provided and include imports of libraries that are needed to run the script.
        2. Make sure to use the pandas library in the script. the script should be a function that takes a dataframe as an input.
        3. The function should be named 'get_answer' and should return the answer as a string.
        4. Use the provided columns to write the script, based on the context given above, do not use external sources, ensure the datatypes match the column description.
        5. Do not include any explanations or comments in the script.
        6. The script should not include any print statements or any other output statements.
        7. Return the script as a string, preferably in a code block.
        8. The script should be valid python code and should not include any syntax errors or  (DO NOT INCLUDE ```markdown) and print the markdown reports.
        

        """
     )
    llm= ChatOpenAI(temperature=0, model="gpt-3.5-turbo", verbose=True)
    chain =  prompt | llm | StrOutputParser()

    response =   chain.invoke({
        "head": state['df_head'],
        "columns": state['df_columns'],
        "question": state['question']
    })
    state['python_code'] = response
    state['next_state'] = "validate_code"
    state['code_valid'] = False

    return state


def validate_code(state:AgentState) -> AgentState:
    try:
        # Create a Python REPL environment
        prompt2 = PromptTemplate(input_variables=['script', 'question'],
                        template="""
                        You are an expert data scientist.

                        You are given a python script that takes in a dataframe as an input and returns the answer to this {question} that was asked.
                        The script is as follows: 
                        {script}

                        Verify that the script is correct and does not contain any errors or bugs.
                         DO NOT INCLUDE ```markdown and print the markdown reports.
                        If the script is correct, return the script as it is without changing anything or saying anything.

                        Else regenerate the correct script that takes in a dataframe as an input and returns the answer to the question asked.
                        The script should be a function that takes a dataframe as an input and returns the answer as a string.

                        Return the script as a string, preferably in a code block.
                        The script should be valid python code and should not include any syntax errors or 
                        
                        DO NOT INCLUDE ```markdown and print the markdown reports.

                        """
                )
        llm2 = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", verbose=True)
        chain2 = prompt2 | llm2 | StrOutputParser()
        response = chain2.invoke({
            "script": state['python_code'],
            "question": state['question']
        })
        state['python_code'] = response
        state['code_valid'] = True
        state['next_state'] = "execute_python_code"
    except Exception as e:
        state['exception'] = str(e)
        state['next_state'] = "regenerate_python_code"
        if state['retries'] < state['max_retries']:
            state['retries'] += 1
        else:
            state['next_state'] = 'result'
    return state



def execute_code(state:AgentState) -> AgentState:
    print("--- PYTHON CODE EXECUTER ---")
    Python_script = state['python_code']
    
    namespace = {'pd':pd}
    exec(Python_script, namespace)
    try:
        state['final_answer'] = namespace['get_answer'](state['df']) 
        state['next_state'] = 'result'
        state['error'] = False
    except Exception as e:
        print("Error executing Python code:", e)
        state['exception'] = f"Error executing Python code:, {e}"
        state['next_state'] = "regenerate_python_code"
        state['error']= True
    return state



def regenerate_code(state:AgentState) -> AgentState:
    print("Regenerating Python code...")
    prompt = PromptTemplate(input_variables= ['error', 'script', 'question'], 
                            template="""
                            You are an expert debugger and an expert data_scientist

                            An initial python script was generated to answer the question: {question}
                            The script is as follows: {script}

                            The script was not able to run successfully and returned the following error: {error}
                            Regenerate the correct script that takes in a dataframe as an input and returns the answer to the question asked.

                            The script should be a function that takes a dataframe as an input and returns the answer as a string.

                            DO NOT INCLUDE ```markdown and print the markdown reports.
                        """
    )


    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", verbose=True)
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({
        "script": state['python_code'],
        "question": state['question'],
        "error": state['exception']
    })
    state['python_code'] = response
    

    state['next_state'] = "validate_code"

    return state


def result(state:AgentState) -> AgentState:
    print("Final Answer:", state['final_answer'])
    state['next_state'] = END
    return state
    