from langchain_openai import ChatOpenAI 
from langchain_core.prompts import PromptTemplate 
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv ,dotenv_values
from langchain.agents import load_tools, initialize_agent, AgentType

env =dotenv_values('../.env')



def generate_code(language, concept):
    chat = ChatOpenAI(api_key = env['OPENAI_API_KEY'], temperature=0.2)

    prompt = PromptTemplate(
        input_variables= ['language', 'concept'],
        template = """
        You are a senior software engineer. 
        Write a short {language} script showing how to do a {concept}.
        Explain the concept briefly before giving the code sample.

"""
    )
    chain = prompt | chat | StrOutputParser()

    response = chain.invoke({'language':language, 'concept':concept})
    

    return response
# print(generate_code('Python', 'Recursion'))



