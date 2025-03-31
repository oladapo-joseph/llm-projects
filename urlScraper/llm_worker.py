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
        llm=llm,chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt, "verbose": True},
        return_source_documents=True
    )
    
    # Get the response
    response = chain.invoke({"query": query})
    
    return response["result"]

print(getResponse("What happened in Edo state?", db, k=3))


"""
loaded
No new URLs to process. using old data...


> Entering new StuffDocumentsChain chain...


> Entering new LLMChain chain...
Prompt after formatting:

                    You are a very good assistant with great writing skills.

                    Use the following context to answer the question:
                    photo

March 30, 2025

News

This decision was communicated in a statement issued by the state government regarding the tragic incident. The killings occurred on Thursday, March 27, 2025, in the Uromi area of Esan North East Local Government Area.

The Edo State Governor, Senator Monday Okpebholo, has ordered the suspension of the Edo State Security Corps Commander, CP Friday Ibadin (Rtd.), following the recent killings of 16 Northern travellers by a mob in Uromi.

This decision was communicated in a statement issued by the state government regarding the tragic incident. The killings occurred on Thursday, March 27, 2025, in the Uromi area of Esan North East Local Government Area.

The statement read: “After reviewing the preliminary report on the unfortunate incident, His Excellency, Senator Monday Okpebholo, has ordered the immediate suspension of all illegal vigilante groups operating under any guise in Edo State. Also suspended is the Commander of the Edo State Security Corps, CP Friday Ibadin (Rtd.).”      

“Its actions do not reflect the core values, character, and principles of the Okpebholo administration or the objectives of the corps as enshrined in the Edo State Security Corps Governance Law,” the statement continued.

According to the statement, 14 individuals have already been arrested, and an intense manhunt is underway for other perpetrators.

A special team set up by the Inspector General of Police is leading the operation. The Edo State Government emphasised its commitment to the constitutionally guaranteed rights of citizens to move freely and engage in lawful business anywhere in the country.

Latest News

2 hours ago

Sallah: Two children killed, 20 injured in Gombe stampede

2 hours ago

Abiodun pledges completion of road repairs in Ogun communities

2 hours ago

2027: I’m ready to step down for better candidate – Adebayo

3 hours ago

Ebonyi varsity doctors threaten strike

3 hours ago

PFN condemns Edo travellers killing, demands justice

Top News

Nigerian boxer Olanrewaju dies after collapsing in Ghana fight

February 19, 2022

Eid-el-Fitr: Govs, lawmakers congratulate Muslims, preach unity, tolerance

Lynched Edo travellers: Governors move against reprisals as 16 slain hunters buried

I nearly withdrew from 2023 presidential race -Tinubu

Dangote, Adenuga, Rabiu, Otedola remain on forbes Africa’s billionaires List

MRS, others raise petrol prices to N930 in Lagos, N960 in North

We are worried if they will ever see – Mums of babies born blind

Heartbreaking story of newlyweds burnt in Lagos tanker fire

                    Question: What happened in Edo state?

                    Only use information from the provided context to answer the question.
                    If you don't have enough context to answer, say "I don't have enough information."
                    Your answers should be as detailed as possible.
    

> Finished chain.

> Finished chain.
In Edo State, there was a tragic incident where 16 Northern travelers were killed by a mob in the 
Uromi area of Esan North East Local Government Area on Thursday, March 27, 2025. In response to this, the Edo State Governor, 
Senator Monday Okpebholo, ordered the immediate suspension of all illegal vigilante groups operating in the state, as well as 
the suspension of the Edo State Security Corps Commander, CP Friday Ibadin (Rtd.). 
The Governor emphasized that the actions of the perpetrators did not reflect the values of the administration or the objectives 
of the security corps. So far, 14 individuals have been arrested, and a manhunt is underway for other perpetrators.
 The Edo State Government is committed to upholding the constitutionally guaranteed rights of citizens to move freely and 
 engage in lawful business.

"""