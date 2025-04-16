import pandas as pd 
from agentx import AgentState 


def getFileDetails(state:AgentState) -> AgentState:
    """
    Get the head of the dataframe and the columns of the dataframe.
    """
    
    # state['df'] = state['df'].dropna(axis=1, how="all")
    state['df_head'] = state['df'].sample(30).to_markdown()
    state['df_columns'] = state['df'].columns.tolist()
    state['next_state'] = "get_question"
    print("next: ", state['next_state'])
    
    return state
