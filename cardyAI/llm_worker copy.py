from central_import import FAISS, load_dotenv, PromptTemplate, ChatGoogleGenerativeAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from tools import search_tool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser

load_dotenv('../.env')


def getResponse(query: str, db: FAISS) -> str:
    """
    Given a query and a FAISS vector database, performs a retrieval on the data.
    If the retrieved context is useful, the context is passed to the agent.
    Otherwise, the query is handled directly. A search tool is only invoked
    when necessary. Memory is enabled for the agent.
    """
    # LLM for both retrieval and agent
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, streaming=True)

    # Setup retriever from FAISS DB and memory
    retriever = db.as_retriever(search_kwargs={"k": 5})
    memory = ConversationBufferMemory(memory_key="chat_history")

    # Build a prompt template that uses provided context if relevant.
    template = """
Your name is Cardy and you are a helpful assistant with great writing skills.

Answer the question: {input}

You can use the context information provided below if it is relevant:
----------------
{context}
----------------

If the question is basic and the context isn’t needed, feel free to answer normally.
If you do use the context, include the source or URL (as a markdown link) only if present in the context.
If you’re not sure, say "I don't have enough information."
Provide a detailed and accurate answer.
    
Format your response as:
[Your detailed answer]
    """
    prompt = PromptTemplate(input_variables=['context', 'input'], template=template)

    # Create a chain that searches the FAISS DB and builds context for the question.
    doc_chain = create_stuff_documents_chain(llm, prompt, output_parser=StrOutputParser())
    retrieval_chain = create_retrieval_chain(retriever, doc_chain)

    # First, invoke the retrieval chain to see if context is available.
    retrieval_output = retrieval_chain.invoke({'input': query})
    
    # Check if the retrieved context is useful.
    # (You can adjust the condition depending on your expected outputs)
    if "I don't have enough information" not in retrieval_output and "Context:" not in retrieval_output:
        # Prepend context if retrieval yields information.
        modified_query = f"Context:\n{retrieval_output}\n\nQuestion:\n{query}"
    else:
        modified_query = query

    # Define the search tool (which will only be used if the agent deems it necessary)
    tools = [search_tool]

    # Initialize the agent with memory enabled
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
    )

    # Run the agent on the modified query
    response = agent.run(modified_query)
    return response


def getResponse(query: str, db: FAISS) -> str:
    """
    Takes a query and a FAISS vector database, retrieves relevant documents,
    and generates a response using Google Gemini 2.0 Flash
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, streaming=True)
    retriever = db.as_retriever(search_kwargs={"k": 5})
    memory = ConversationBufferMemory(memory_key="chat_history")
    template = """
    
    Your name is Cardy and You are a helpful assistant with great writing skills.


    Answer the question: {input}

    You can take context information from below:
    ----------------
    {context}
    ----------------

    Your task:
    1. You dont have to use any tool if it is a basic question, Answer normally if basic questions but other questions will be based ONLY on the provided context
    2. If you can't answer from the context, say "I don't have enough information."
    3. Be detailed and accurate
    4. Include the source or url from the context as a markdown link at the end of your response, else dont use.
    5. 
    
    Format your response as:
    [Your detailed answer] 

    
    """

    prompt = PromptTemplate(
                        input_variables= ['context', 'input'],
                        template=template
                    )
    doc_chain = create_stuff_documents_chain(llm, prompt,output_parser=StrOutputParser())
    retrieval_chain = create_retrieval_chain(retriever, doc_chain)

    # Define tools for the agent
    tools = [search_tool]

    # Initialize the agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        # memory = True,
        handle_parsing_errors=True,
    )

    # Invoke the agent with the retrieval chain and query
    response = agent.run(retrieval_chain.invoke({'input': query}))

    return response
    