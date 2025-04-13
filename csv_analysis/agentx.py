from typing import TypedDict 
import pandas as pd 

class AgentState(TypedDict):
    file: str
    python_code: str
    final_answer: str
    df: pd.DataFrame
    exception: str
    df_head: str
    df_columns: list[str]
    question: str
    code_valid: bool
    error : bool 
    next_state: str
    retries: int=0
    max_retries: int
