from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI ,OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate 
from langchain_community.vectorstores import  FAISS 
from youtube_transcript_api import YouTubeTranscriptApi 
from dotenv import load_dotenv 


load_dotenv('../.env')

# the text-embedding-3-small performs better

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


template = """

        You are a very good youtube assistant that can answer questions about
        videos based on the video's transcript

        Answer the following question: {question}
        By searching the transcript : {docs}

        Only use information from the transcript given to answer the question
        If you dont have enough context to answer a question you can say "i dont know"
        or "i dont have enough information from the video"

        Your answers should be as detailed as possible

"""


def create_Youtube_vectors(url:str)->FAISS: 
    
    def getId(url)->str:
        if url.startswith('http'):
            return url.split('/')[-1]
        return url
    
    transcript= YouTubeTranscriptApi.get_transcript(getId(url))
    
    full_transcript = " ".join([i['text'] for i in transcript])

    # next thing is to split the transcript into documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, 
                                                   chunk_overlap=200)
    docs = text_splitter.split_text(full_transcript)

    db = FAISS.from_texts(docs, embeddings)

    return db, docs


def getSummary(docs):
    if type(docs) == list:
        newdocs=  " ".join(i for i in docs)
    else:
        newdocs =docs 

    llm = ChatOpenAI(temperature=0.4)

    prompt = PromptTemplate(
        input_variables=['file'],
        template= '''
            You are a good writer.

            Summarize this video transcript: {file}
            Do this in less than 100 words.
'''
    )
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({'file':newdocs})

    return response


def getResponse(db,query, k=4):

    docs = db.similarity_search(query, k)

    page_content= ' '.join([i.page_content for i in docs])

    llm = ChatOpenAI()

    prompt = PromptTemplate(
        input_variables=['question', 'docs'],
        template= template 

    )
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({'question':query, 'docs':page_content})

    return response 
