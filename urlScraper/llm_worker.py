from langchain_core.output_parsers import StrOutputParser 
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationChain, RetrievalQA
from scraper import Url_to_vectorDB
load_dotenv('../.env')

db = Url_to_vectorDB(['https://www.vanguardngr.com/2025/03/traffic-laws-lagos-govt-clarifies-deployment-of-speed-limit-cameras/'])

def getResponse(query: str, db: FAISS, k=4) -> str:
    """
    Takes a query and a FAISS vector database, retrieves relevant documents,
    and generates a response using OpenAI's GPT-3 model.
    """
    # Load the model
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, streaming=True)
    
    # Create a retriever from the database
    retriever = db.as_retriever(search_kwargs={"k": k})
    
    # Create a prompt template with correct variable names
    template = """
                    You are a very good assistant with great writing skills.

                    Use the following context to answer the question:
                    {context}

                    Question: {question}

                    Only use information from the provided context to answer the question.
                    If you don't have enough context to answer, say "I don't have enough information."
                    Your answers should be as detailed as possible.
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )
    
    # Create the chain without memory (memory is handled differently in RetrievalQA)
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={
            "prompt": prompt,
        },
        return_source_documents=True
    )
    
    # Get the response
    response = chain.invoke({"query": query})
    
    return response["result"]

print(getResponse("What is the new traffic law in Lagos?", db, k=3))