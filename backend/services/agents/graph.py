from langgraph.graph import StateGraph, END

from backend.services.agents.state import AgentState

from backend.services.agents.nodes import (
    resume_agent,
    jd_match_agent,
    roadmap_agent,
    resource_agent,
    final_decision_agent,
)

from backend.services.agents.evaluation import run_full_evaluation


# ============================================================
# ROUTING
# ============================================================

def route_after_match(state: AgentState) -> str:
    """
    The application-analysis workflow always continues through
    preparation/resource analysis before the final decision.

    We intentionally do not skip these agents for high-match
    candidates because they provide useful preparation context.
    """

    return "roadmap"


# ============================================================
# GRAPH
# ============================================================

graph = StateGraph(AgentState)

graph.add_node(
    "resume",
    resume_agent
)

graph.add_node(
    "jd_match",
    jd_match_agent
)

graph.add_node(
    "roadmap",
    roadmap_agent
)

graph.add_node(
    "resource",
    resource_agent
)

graph.add_node(
    "decision",
    final_decision_agent
)


# ============================================================
# FLOW
# ============================================================

graph.set_entry_point("resume")

graph.add_edge(
    "resume",
    "jd_match"
)

graph.add_conditional_edges(
    "jd_match",
    route_after_match,
    {
        "roadmap": "roadmap"
    }
)

graph.add_edge(
    "roadmap",
    "resource"
)

graph.add_edge(
    "resource",
    "decision"
)

graph.add_edge(
    "decision",
    END
)


# ============================================================
# COMPILE
# ============================================================

app = graph.compile()


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_state: AgentState = {
        "resume_id": 5,

        "jd_text": """
        We are looking for a Data Scientist with
        Python, SQL, Machine Learning,
        Exploratory Data Analysis,
        Feature Engineering,
        Pandas, Scikit-learn and AWS experience.
        """,

        "resume_text": None,
        "structured_resume": None,

        "match_score": None,
        "matched_skills": None,
        "missing_skills": None,

        "roadmap": None,
        "resources": None,

        "recommendation": None,
        "reasoning": None,
        "estimated_prep_time": None,
    }

    print("=" * 70)
    print("PATHPILOT AI - LANGGRAPH APPLICATION AGENT")
    print("=" * 70)

    try:

        result = app.invoke(test_state)

        print("\nMATCH SCORE:")
        print(result.get("match_score"))

        print("\nMATCHED SKILLS:")
        print(result.get("matched_skills"))

        print("\nMISSING SKILLS:")
        print(result.get("missing_skills"))

        print("\nROADMAP:")
        print(result.get("roadmap"))

        print("\nRESOURCES:")
        print(result.get("resources"))

        print("\nRECOMMENDATION:")
        print(result.get("recommendation"))

        print("\nREASONING:")
        print(result.get("reasoning"))

        print("\nESTIMATED PREPARATION:")
        print(result.get("estimated_prep_time"))

        print("\n" + "=" * 70)
        print("AGENT EVALUATION")
        print("=" * 70)

        try:
            eval_report = run_full_evaluation(result)
            print(eval_report)

        except Exception as evaluation_error:
            print(
                "Evaluation failed:",
                str(evaluation_error)
            )

    except Exception as error:

        print("\nAGENT WORKFLOW FAILED")
        print(type(error).__name__)
        print(str(error))
        raise