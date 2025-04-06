from agentx import AgentState 


def getQuestion(state:AgentState) -> AgentState:
    """
    Get the question from the user.
    """
    state['question'] = "What is the total volumne traded in May 2023?"
    state['next_state'] = "generate_python_code"
    return state


def go_to_next(state: AgentState):
    return state['next_state']
