from langgraph.graph import START, StateGraph, END
from langgraph.graph.graph import CompiledGraph
from agentx import AgentState
from code_handler import generate_code, validate_code, execute_code, regenerate_code, result
from query_handler import getQuestion, go_to_next
from filehandler import getFileDetails
from typing import Annotated, Literal, Union
from enum import Enum

# Define possible next states
class NextState(str, Enum):
    VALIDATE = "validate_code"
    EXECUTE = "execute_python_code"
    REGENERATE = "regenerate_python_code"
    RESULT = "result"
    END = "end"

def create_graph() -> CompiledGraph:
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("getFile", getFileDetails)
    workflow.add_node("get_question", getQuestion)
    workflow.add_node("generate_python_code", generate_code)
    workflow.add_node("validate_code", validate_code)
    workflow.add_node("execute_python_code", execute_code)
    workflow.add_node("regenerate_python_code", regenerate_code)
    workflow.add_node("result", result)
    
    # Define the router function for conditional edges
    def router(state: AgentState) -> str:
   
        return state.get('next_state')
    
    # Add edges
    workflow.add_edge(START, "getFile")
    workflow.add_edge("getFile", "get_question")
    workflow.add_edge("get_question", "generate_python_code")
    workflow.add_edge("generate_python_code", "validate_code")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "validate_code",
        router,
        {
            "execute_python_code": "execute_python_code",
            "result": "result"
        }
    )
    
    workflow.add_conditional_edges(
        "execute_python_code",
        router,
        {
            "result": "result",
            "regenerate_python_code": "regenerate_python_code"
        }
    )
    
    workflow.add_edge("regenerate_python_code", "validate_code")
    workflow.add_edge("result", END)
    
    graph =  workflow.compile()

    try:
        graph.get_graph(xray=1).draw_mermaid_png(output_file_path="pandas_q.png")
    except Exception as e:
        print(f"Failed to generate graph visualization: {e}")
    
    return graph

# Create and compile the graph
# graph = create_graph()

# if __name__ == "__main__":
#     # Visualize the graph (optional)
#     try:
#         graph.get_graph(xray=1).draw_mermaid_png(output_file_path="pandas_q.png")
#     except Exception as e:
#         print(f"Failed to generate graph visualization: {e}")