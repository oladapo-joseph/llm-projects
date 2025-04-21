from central_import import FAISS, load_dotenv, PromptTemplate, ChatGoogleGenerativeAI
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from tools import search_tool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime 

load_dotenv('../.env')

NOW = datetime.now().date()


def getResponse(query: str, db: FAISS) -> str:
    """
    Given a query and a FAISS vector database, performs a retrieval on the data.
    If the retrieved context is useful, the context is passed to the agent.
    Otherwise, the query is handled directly. A search tool is only invoked
    when necessary. Memory is enabled for the agent.
    """
    # LLM for both retrieval and agent
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2, streaming=True)
    # llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.1, streaming=True )
    # Setup retriever from FAISS DB and memory
    retriever = db.as_retriever(search_kwargs={"k": 10})
    memory = ConversationBufferMemory(memory_key="history")

    # Build a prompt template that uses provided context if relevant.
    template = """
        Your name is Cardy and you are a helpful assistant with great writing skills. 

        Answer the question: {input}

        You can use the context information provided below if it is relevant:
        ----------------
        {context}
        ----------------

        Your task:
        1. Respond to greetings and salutations 
        2. Answer will be based ONLY on the provided context
        3. If you can't answer from the context, say "I don't have enough information."
        4. Be detailed and accurate
        5. Include the source or url from the context as a markdown link at the end of your response, else dont use.
        
        Format your response as:
        [Your detailed answer]
            """
    template = f"Note that today's date is {NOW}\n" + template 
    prompt = PromptTemplate(input_variables=['context', 'input'], template=template)

    # Create a chain that searches the FAISS DB and builds context for the question.
    doc_chain = create_stuff_documents_chain(llm, prompt, output_parser=StrOutputParser())
    retrieval_chain = create_retrieval_chain(retriever, doc_chain)

    # First, invoke the retrieval chain to see if context is available.
    retrieval_output = retrieval_chain.invoke({'input': query})
    
    print(retriever.get_relevant_documents(query))
    # Check if the retrieved context is useful.
    # (You can adjust the condition depending on your expected outputs)
    if "I don't have enough information"  in retrieval_output['answer']:
        # Prepend context if retrieval yields information.
        modified_query = f"Context:\n{retrieval_output['answer']}\n\nQuestion:\n{query}"
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
    
        

    # Define the search tool (which will only be used if the agent deems it necessary)
    
    return retrieval_output['answer']
