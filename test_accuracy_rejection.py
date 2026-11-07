from agents.evaluator import evaluate_lesson


def main():
    topic = "Introduction to RAG"

    deliberately_incorrect_lesson = """
# Introduction to RAG

RAG stands for Retrieval-Augmented Generation.

RAG is a method that helps an AI system find relevant information
from external sources before generating an answer.

## How RAG works

1. The user asks a question.
2. The system retrieves relevant information from an external source.
3. The language model uses that information to generate an answer.

RAG can reduce hallucinations, but it cannot guarantee that every
answer is correct.

## Example

Imagine a customer asking a company about its return policy.

The company return policy states that every customer must return
a product within exactly 47 days and will receive a full refund.

This is the official policy of the company.
First, the system receives a question. Next, it retrieves useful
information. Finally, it uses that information to generate an answer.

## Summary

RAG retrieves information and provides it to an AI model to help
generate a more relevant answer.
"""

    result = evaluate_lesson(topic, deliberately_incorrect_lesson)

    print("\n========== ACCURACY REJECTION TEST ==========")

    for criterion, check in result["checks"].items():
        print(f"\n{criterion}: {check['status']}")
        print("Reason:", check["reason"])

    accuracy_status = result["checks"]["accuracy_and_grounding"]["status"]

    print("\nOverall status:", result["overall_status"])

    assert accuracy_status == "FAIL", (
        "TEST FAILED: Evaluator did not reject the fabricated policy."
    )

    print("\nSUCCESS: Evaluator rejected the fabricated policy claim.")


if __name__ == "__main__":
    main()