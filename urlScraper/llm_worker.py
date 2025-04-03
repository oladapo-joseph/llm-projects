from langchain_core.output_parsers import StrOutputParser 
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
# from scraper import Url_to_vectorDB
load_dotenv('../.env')


def getResponse(query: str, db: FAISS, k=4) -> str:
    """
    Takes a query and a FAISS vector database, retrieves relevant documents,
    and generates a response using OpenAI's GPT-3 model.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, streaming=True)
    retriever = db.as_retriever(search_kwargs={"k": k})
    
    template = """
    You are a helpful assistant with great writing skills and also a graduate.


    Answer the question: {question}

    You can take context information from below:
    ----------------
    {context}
    ----------------

    Your task:
    1. Answer normally if basic questions but other questions will be based ONLY on the provided context
    2. If you can't answer from the context, say "I don't have enough information."
    3. Be detailed and accurate
    
    Format your response as:
    [Your detailed answer]

    
    """
    # Get relevant documents first
    docs = retriever.get_relevant_documents(query)


    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={
            "prompt": PromptTemplate(
                template=template,
                input_variables=["context", "question"]),
            "document_variable_name": "context",'verbose':True
        },
        return_source_documents=True
        
    )
    
    
    # Create response with source formatting
    response = chain.invoke({"query": query})
    
    return response['result']
