from langchain import hub 
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from web2DB import embeddings 


load_dotenv('../.env')


db = FAISS.load_local('../faiss_index', embeddings, allow_dangerous_deserialization=True)


def getResponse(query: str, db: FAISS, k=4) -> str:
    """
    Takes a query and a FAISS vector database, retrieves relevant documents,
    and generates a response using OpenAI's GPT-3 model.
    """
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2, streaming=True)
    retriever = db.as_retriever(search_kwargs={"k": k})
    
    template = """
    You are a helpful assistant with great writing skills and also a graduate.


    Answer the question: {input}

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
    prompt = PromptTemplate(
                        input_variables= ['context', 'input'],
                        template=template
                    )
    doc_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever,doc_chain)
    response = chain.invoke({'input':query})
    return response['answer']

# you can test it out on your own with just ordinary inputs
# query = input('What will you like to know: ')

# x = getResponse(query, db,5)

# print (x)
