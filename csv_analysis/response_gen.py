from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv

load_dotenv('../.env')  # Load environment variables from .env file

def generate_report(question: str, answer: str) -> str:
    """
    Generates a markdown report based on the question and answer provided.

    Args:
        question (str): The question to be answered.
        answer (str): The answer to the question.

    Returns:
        str: A markdown report containing the question and answer.
    """
    template = """

        You are a helpful assistant that can write reports

        I have a question like this: {question}.
        And the answer to the question is: {answer}.
        Write a markdown report that answers the question and includes the answer.
    """

    prompt = PromptTemplate(
        input_variables=["question", "answer"],
        template=template)

    llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-2.0-flash", verbose=True)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "question": question,
        "answer": answer
    })

    return response