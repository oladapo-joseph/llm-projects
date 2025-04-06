from langchain_openai import ChatOpenAI
import pandas as pd
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_experimental.agents.agent_toolkits.python.base import create_python_agent
from langchain_experimental.utilities import PythonREPL
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain.agents import AgentType


load_dotenv('../.env')  # Load environment variables from .env file

df= pd.read_csv('../data/ngxdata.csv', low_memory=False)
df = df.dropna(axis=1, how='all')  # Drop columns that are completely empty 

df_head = str(df.sample(10).to_markdown())
df_columns = df.columns.tolist()

prompt = PromptTemplate(
        input_variables=['columns', 'head', 'question'],
        template="""
        
        You are an expert data scientist and a helpful assistant that can analyze CSV files."),
    
        I have a CSV file with the following columns: {columns}. 
        Here are 10 random rows from the file: {head}. 
        Use this as context to understand how the actual table looks like and use it to answer the following question.
        {question}
        
        1. Write a python script that shows how to answer the question using STRICTLY the above context provided.
        2. Make sure to use the pandas library in the script. the script should be a function that takes a dataframe as input and returns the answer.
        3. The function should be named 'get_answer' and should return the answer as a string.
        4. Use the provided columns to write the script, based on the context given above, do not use external sources, ensure the datatypes match the column description.
        5. Do not include any explanations or comments in the script.
        6. Store the final output of the script as final_answer.
        7. Return the script as a string, preferably in a code block.
        8. The script should be valid python code and should not include any syntax errors."""
     )


llm= ChatOpenAI(temperature=0, model="gpt-3.5-turbo", verbose=True)
#     tool = PythonREPLTool(),
#     prompt=prompt,
#     agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True
# )

chain =  prompt | llm | StrOutputParser()

response =   chain.invoke({
    "head": df_head,
    "columns": df_columns,
    "question": "What is the latest stock price of MTN ?"
})

print(response['text']) 
print("-----------------------------------------------------")
print("-----------------------------------------------------")
final_answer = {}
exec(response['text'], final_answer)
print(final_answer['final_answer'](df))
