from agents.evaluator import evaluate_lesson


def main():
    topic = "Introduction to RAG"

    valid_lesson = """
# Introduction to RAG

RAG stands for Retrieval-Augmented Generation.

It is a method that helps AI find useful information
from external sources before answering a question.

## Why is RAG useful?

An AI model may not know information from a particular document.
RAG helps it retrieve relevant information before generating an answer.

## How does RAG work?

First, a user asks a question.
Next, the system searches for relevant information.
Finally, the AI uses the retrieved information to generate an answer.

## Example

Imagine a student asking questions about a textbook.
A RAG system searches the textbook and gives relevant information
to the AI model. The AI then uses that information to answer.

RAG can reduce incorrect answers, but it cannot guarantee
that every answer is correct.

## Summary

RAG combines information retrieval with AI answer generation.
"""

    result = evaluate_lesson(topic, valid_lesson)

    print("\n========== VALID LESSON TEST ==========")

    for criterion, check in result["checks"].items():
        print(f"{criterion}: {check['status']}")
        print("Reason:", check["reason"])

    print("\nOverall status:", result["overall_status"])

    assert result["checks"]["accuracy_and_grounding"]["status"] == "PASS", (
        "Valid lesson was incorrectly rejected by accuracy safeguard."
    )

    assert result["overall_status"] == "PASS", (
        "Valid beginner lesson did not pass all evaluation criteria."
    )

    print("\nSUCCESS: Valid RAG lesson passed evaluation.")


if __name__ == "__main__":
    main()