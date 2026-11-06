
from langgraph.graph import StateGraph, START, END

from workflow.state import LessonState
from workflow.nodes import generate_node, evaluate_node


def route_after_evaluation(state: LessonState):
    """Decide whether to retry or finish."""

    if state["status"] == "PASS":
        return END

    if state["attempts"] <= state["max_retries"]:
        return "generate"

    return END


def build_workflow():
    """Build and compile the lesson generation workflow."""

    workflow = StateGraph(LessonState)

    workflow.add_node("generate", generate_node)
    workflow.add_node("evaluate", evaluate_node)

    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", "evaluate")

    workflow.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "generate": "generate",
            END: END
        }
    )

    return workflow.compile()


lesson_workflow = build_workflow()
