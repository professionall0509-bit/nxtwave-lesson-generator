
from workflow.graph import lesson_workflow
from memory.database import (
    initialize_database,
    save_run,
    learn_from_rejections,
    get_learning_rules
)


def main():
    initialize_database()

    # Deliberately provide a lesson that should fail evaluation.
    initial_state = {
        "topic": "Introduction to RAG - Failure Test",
        "lesson": "",
        "feedback": "",
        "evaluation": {},
        "attempts": 0,
        "max_retries": 2,
        "rejection_log": [],
        "final_lesson": None,
        "status": "STARTED"
    }

    print("\nStarting deliberate failure test...")

    result = lesson_workflow.invoke(initial_state)

    print("\n========== TEST RESULT ==========")
    print("Status:", result["status"])
    print("Generation attempts:", result["attempts"])
    print("Rejected attempts:", len(result["rejection_log"]))

    for entry in result["rejection_log"]:
        print("\nFailed attempt:", entry["attempt"])

        for criterion, details in entry["failed_criteria"].items():
            print("-", criterion)
            print("  Reason:", details["reason"])
            print("  Suggestion:", details["suggestion"])

    # Save test results separately using the test topic.
    save_run(
        topic=initial_state["topic"],
        status=result["status"],
        attempts=result["attempts"],
        rejection_log=result["rejection_log"]
    )

    learn_from_rejections(result["rejection_log"])

    print("\n========== LEARNED RULES ==========")

    rules = get_learning_rules()

    for rule in rules:
        print(
            rule["criterion"],
            "|",
            rule["suggestion"],
            "| Occurrences:",
            rule["occurrences"]
        )

    print("\nFailure test completed.")


if __name__ == "__main__":
    main()
