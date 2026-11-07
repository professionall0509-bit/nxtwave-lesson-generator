
import workflow.nodes as nodes
from workflow.graph import lesson_workflow

generation_count = 0
evaluation_count = 0
received_feedback = []


def fake_generator(topic, feedback=""):
    global generation_count

    generation_count += 1
    received_feedback.append(feedback)

    return f"Simulated lesson attempt {generation_count}"


def fake_evaluator(topic, lesson):
    global evaluation_count

    evaluation_count += 1

    checks = {}

    criteria = [
        "accuracy_and_grounding",
        "beginner_friendly_language",
        "teaches_by_example",
        "clear_and_jargon_free",
        "covers_key_points",
        "coherent_teaching_flow"
    ]

    for criterion in criteria:
        checks[criterion] = {
            "status": "PASS",
            "reason": "Simulated successful check.",
            "suggestion": "No improvement needed.",
            "evidence": "Simulated supporting lesson text."
        }

    # Deliberately fail the first evaluation.
    if evaluation_count == 1:
        checks["accuracy_and_grounding"] = {
            "status": "FAIL",
            "reason": "Simulated technical accuracy failure.",
            "suggestion": "Correct the technical explanation.",
            "evidence": ""
        }

    overall_status = (
        "PASS"
        if all(check["status"] == "PASS" for check in checks.values())
        else "FAIL"
    )

    return {
        "overall_status": overall_status,
        "checks": checks
    }


# Replace real functions only inside this test process.
nodes.generate_lesson = fake_generator
nodes.evaluate_lesson = fake_evaluator


initial_state = {
    "topic": "RAG Retry Test",
    "lesson": "",
    "feedback": "",
    "evaluation": {},
    "attempts": 0,
    "max_retries": 2,
    "rejection_log": [],
    "final_lesson": None,
    "status": "STARTED"
}

print("\nStarting simulated retry test...")

result = lesson_workflow.invoke(initial_state)

print("\n========== RETRY TEST RESULT ==========")
print("Final status:", result["status"])
print("Generation attempts:", result["attempts"])
print("Evaluation attempts:", evaluation_count)
print("Rejected attempts:", len(result["rejection_log"]))
print("Feedback received on retry:", bool(received_feedback[1]))

assert result["status"] == "PASS"
assert result["attempts"] == 2
assert evaluation_count == 2
assert len(result["rejection_log"]) == 1
assert bool(received_feedback[1])

print("\nSUCCESS: Failure, feedback, retry and PASS routing verified.")
