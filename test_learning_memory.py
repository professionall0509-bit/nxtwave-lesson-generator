
import tempfile
from pathlib import Path

import memory.database as database


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        database.DB_PATH = Path(temp_dir) / "test_memory.db"

        database.initialize_database()

        test_rejection = [
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

        database.learn_from_rejections(test_rejection)
        database.learn_from_rejections(test_rejection)

        rules = database.get_learning_rules()

        print("\n========== LEARNING MEMORY TEST ==========")

        for rule in rules:
            print("Criterion:", rule["criterion"])
            print("Learned rule:", rule["suggestion"])
            print("Occurrences:", rule["occurrences"])

        assert len(rules) == 1
        assert rules[0]["occurrences"] == 2

        print("\nSUCCESS: Repeated failures became a learned rule.")


if __name__ == "__main__":
    main()
