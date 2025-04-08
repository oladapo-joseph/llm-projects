import pandas as pd 
from agentx import AgentState 


# df = pd.read_csv('../data/ngxdata.csv', low_memory=False)
# df = df.dropna(axis=1, how='all')  # Drop columns that are completely empty


def getFileHead(state:AgentState) -> AgentState:
    """
    Get the head of the dataframe and the columns of the dataframe.
    """
    print(state['next_state'])
    state['df_head'] = state['df_head']
    state['df_columns'] = state['df_columns']
    state['next_state'] = "get_question"
    print("next: ", state['next_state'])
    state['df'] = state['df']
    return state



