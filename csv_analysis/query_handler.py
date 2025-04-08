from agentx import AgentState 


def getQuestion(state:AgentState) -> AgentState:
    """
    Get the question from the user.
    """
    state['question'] = state['question']
    state['next_state'] = "generate_python_code"
    return state


def go_to_next(state: AgentState):
    return state['next_state']
