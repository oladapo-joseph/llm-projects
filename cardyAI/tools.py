from langchain.tools import Tool
from langchain_core.tools.convert import tool
from tavily import TavilyClient
from central_import import load_dotenv


# Create a LangChain-compatible tool

@tool
def search_tool(query:str) -> list[dict]:
    """
        Use this tool to search the web using Tavily
        Args:
            query:str
                the question being asked 
        Return:
            search_result:list[dict]
                a list of dictionaries contain the details of the info,
                note that the key info lies in these keys; content and url (source)

    """
    client = TavilyClient()

    search_result = client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

    return search_result 