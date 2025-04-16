from main import FAISS, load_dotenv, PromptTemplate, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


load_dotenv('../.env')
 

def getResponse(query: str, db: FAISS) -> str:
    """
    Takes a query and a FAISS vector database, retrieves relevant documents,
    and generates a response using Google Gemini 2.0 Flash
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, streaming=True)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    
    template = """
    You are a helpful assistant with great writing skills.


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
    chain = create_retrieval_chain(retriever, doc_chain)
    response = chain.invoke({'input':query})
    return response['answer']

    
