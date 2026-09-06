from langgraph.graph import END, START, StateGraph

from app.agents.review_agent import ReviewGenerationAgent
from app.agents.spec_agent import SpecRetrievalAgent
from app.agents.state import AgentState


specification_agent = SpecRetrievalAgent()
review_agent = ReviewGenerationAgent()


def specification_node(state: AgentState) -> AgentState:
    return specification_agent.run_state(state)


def review_node(state: AgentState) -> AgentState:
    return review_agent.run_state(state)


builder = StateGraph(AgentState)
builder.add_node("specification_agent", specification_node)
builder.add_node("review_agent", review_node)
builder.add_edge(START, "specification_agent")
builder.add_edge("specification_agent", "review_agent")
builder.add_edge("review_agent", END)
workflow = builder.compile()
