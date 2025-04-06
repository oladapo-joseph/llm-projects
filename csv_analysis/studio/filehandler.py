import pandas as pd 
from agentx import AgentState 


df = pd.read_csv('../data/ngxdata.csv', low_memory=False)
df = df.dropna(axis=1, how='all')  # Drop columns that are completely empty


def getFileHead(state:AgentState) -> AgentState:
    """
    Get the head of the dataframe and the columns of the dataframe.
    """
    state['df_head'] = str(df.sample(30).to_markdown())
    state['df_columns'] = df.columns.tolist()
    state['next_state'] = "get_question"
    state['df'] = df
    return state



