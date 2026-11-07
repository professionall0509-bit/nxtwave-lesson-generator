
import json
from pathlib import Path

from workflow.graph import lesson_workflow
from memory.database import (
    initialize_database,
    save_run,
    get_previous_runs,
    learn_from_rejections,
    get_learning_rules
)

OUTPUT_DIR = Path(__file__).parent / "outputs"


def build_memory_feedback(previous_runs, learning_rules):
    feedback_parts = []

    # Reuse feedback from recent rejected attempts.
    for run in previous_runs[:3]:
        rejection_log = json.loads(run["rejection_log"] or "[]")

        for rejection in rejection_log:
            for criterion, details in rejection["failed_criteria"].items():
                feedback_parts.append(
                    f"{criterion}: {details['suggestion']}"
                )

    # Reuse learned rules from repeated failures.
    for rule in learning_rules:
        feedback_parts.append(
            f"{rule['criterion']}: {rule['suggestion']}"
        )

    return "\n".join(dict.fromkeys(feedback_parts))


def save_outputs(result):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Save the lesson only when it passes evaluation.
    if result["final_lesson"]:
        lesson_path = OUTPUT_DIR / "final_lesson.md"
        lesson_path.write_text(
            result["final_lesson"],
            encoding="utf-8"
        )
        print(f"\nFinal lesson saved to: {lesson_path}")

    # Save the rejection log for every run.
    rejection_path = OUTPUT_DIR / "rejection_log.json"
    rejection_path.write_text(
        json.dumps(
            result["rejection_log"],
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )
    print(f"Rejection log saved to: {rejection_path}")


def main():
    topic = "Introduction to RAG"

    initialize_database()

    previous_runs = get_previous_runs(topic)
    learning_rules = get_learning_rules()

    memory_feedback = build_memory_feedback(
        previous_runs,
        learning_rules
    )

    print("\nStarting the lesson generation workflow...")
    print(f"Topic: {topic}")
    print(f"Previous runs found: {len(previous_runs)}")
    print(f"Learned rules available: {len(learning_rules)}")

    initial_state = {
        "topic": topic,
        "lesson": "",
        "feedback": memory_feedback,
        "evaluation": {},
        "attempts": 0,
        "max_retries": 2,
        "rejection_log": [],
        "final_lesson": None,
        "status": "STARTED"
    }

    result = lesson_workflow.invoke(initial_state)

    # Save the run and learn from its rejection history.
    save_run(
        topic=topic,
        status=result["status"],
        attempts=result["attempts"],
        rejection_log=result["rejection_log"]
    )

    learn_from_rejections(result["rejection_log"])

    # Save generated files.
    save_outputs(result)

    print("\n========== WORKFLOW RESULT ==========")
    print(f"Status: {result['status']}")
    print(f"Generation attempts: {result['attempts']}")

    if result["final_lesson"]:
        print("\n========== FINAL LESSON ==========")
        print(result["final_lesson"])
    else:
        print("\nNo lesson passed the evaluation.")

    print("\n========== REJECTION LOG ==========")

    if result["rejection_log"]:
        for entry in result["rejection_log"]:
            print(f"\nAttempt: {entry['attempt']}")

            for criterion, details in entry["failed_criteria"].items():
                print(f"- {criterion}: {details['reason']}")
                print(f"  Improvement: {details['suggestion']}")
    else:
        print("No rejected attempts.")

    print("\nRun saved to persistent memory.")
    print("Learning rules updated.")


if __name__ == "__main__":
    main()
