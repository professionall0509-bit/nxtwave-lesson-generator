import tempfile
from pathlib import Path

import memory.database as database
from main import build_memory_feedback


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use a separate temporary database.
        database.DB_PATH = Path(temp_dir) / "test_memory.db"

        database.initialize_database()

        rejection = [
            {
                "attempt": 1,
                "failed_criteria": {
                    "accuracy_and_grounding": {
                        "reason": "Unsupported policy claim.",
                        "suggestion": (
                            "Avoid inventing exact policy figures "
                            "or presenting fictional policies as facts."
                        )
                    }
                }
            }
        ]

        # Simulate the same failure occurring twice.
        database.learn_from_rejections(rejection)
        database.learn_from_rejections(rejection)

        # Retrieve the learned rule from SQLite.
        learning_rules = database.get_learning_rules()

        # Pass the retrieved rule through the actual main.py helper.
        feedback = build_memory_feedback([], learning_rules)

        print("\n========== MEMORY INTEGRATION TEST ==========")
        print("Retrieved learning rules:", len(learning_rules))
        print("\nFeedback passed to generator:")
        print(feedback)

        assert learning_rules, "No learned rules were retrieved."
        assert "Avoid inventing exact policy figures" in feedback

        print("\nSUCCESS: SQLite memory is retrieved and converted into generator feedback.")


if __name__ == "__main__":
    main()