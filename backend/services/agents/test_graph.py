from typing import TypedDict
from langgraph.graph import StateGraph, END

from backend.services.agents.state import AgentState
from backend.services.agents.nodes import (
    resume_agent,
    jd_match_agent,
    roadmap_agent,
    resource_agent,
    final_decision_agent
)



# -----------------------------
# 1. State define karo
# -----------------------------
class SimpleState(TypedDict):
    message: str
    step_count: int


# -----------------------------
# 2. Nodes banao (functions)
# -----------------------------
def node_one(state: SimpleState) -> SimpleState:
    print("Node 1 chal raha hai")
    state["message"] = state["message"] + " -> Node1 se guzra"
    state["step_count"] += 1
    return state


def node_two(state: SimpleState) -> SimpleState:
    print("Node 2 chal raha hai")
    state["message"] = state["message"] + " -> Node2 se guzra"
    state["step_count"] += 1
    return state


# -----------------------------
# 3. Graph banao
# -----------------------------
graph = StateGraph(SimpleState)

graph.add_node("first", node_one)
graph.add_node("second", node_two)

graph.set_entry_point("first")
graph.add_edge("first", "second")
graph.add_edge("second", END)

app = graph.compile()


# -----------------------------
# 4. Test chalao
# -----------------------------
if __name__ == "__main__":
    result = app.invoke({"message": "Shuru", "step_count": 0})
    print("\nFinal Result:")
    print(result)