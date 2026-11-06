
from agents.generator import generate_lesson
from agents.evaluator import evaluate_lesson


def generate_node(state):
    """Generate a lesson using previous evaluator feedback."""

    topic = state["topic"]
    feedback = state.get("feedback", "")

    lesson = generate_lesson(topic, feedback)

    return {
        "lesson": lesson,
        "attempts": state.get("attempts", 0) + 1,
        "status": "GENERATED"
    }


def evaluate_node(state):
    """Evaluate the generated lesson and record failures."""

    topic = state["topic"]
    lesson = state["lesson"]

    evaluation = evaluate_lesson(topic, lesson)

    failed_checks = {
        name: check
        for name, check in evaluation["checks"].items()
        if check["status"] == "FAIL"
    }

    rejection_log = list(state.get("rejection_log", []))

    if evaluation["overall_status"] == "PASS":
        return {
            "evaluation": evaluation,
            "final_lesson": lesson,
            "feedback": "",
            "status": "PASS",
            "rejection_log": rejection_log
        }

    # Build feedback for the next generation attempt.
    feedback_parts = []

    for criterion, check in failed_checks.items():
        feedback_parts.append(
            f"{criterion}: {check['reason']} "
            f"Improvement needed: {check['suggestion']}"
        )

    feedback = "\n".join(feedback_parts)

    # Record this rejected attempt.
    rejection_log.append({
        "attempt": state["attempts"],
        "failed_criteria": {
            criterion: {
                "reason": check["reason"],
                "suggestion": check["suggestion"]
            }
            for criterion, check in failed_checks.items()
        },
        "lesson": lesson
    })

    return {
        "evaluation": evaluation,
        "feedback": feedback,
        "rejection_log": rejection_log,
        "status": "FAIL"
    }
