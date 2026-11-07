
from agents.evaluator import evaluate_lesson

bad_lesson = """
# Introduction to RAG

RAG means Random Answer Generator.

RAG always prevents hallucinations.
It guarantees that every AI answer is 100% correct.

RAG does not use external documents.
It simply guesses answers from memory.
"""

result = evaluate_lesson(
    topic="Introduction to RAG",
    lesson=bad_lesson
)

print("\n========== EVALUATOR FAILURE TEST ==========")
print("Overall status:", result["overall_status"])

for criterion, check in result["checks"].items():
    print(f"\n{criterion}: {check['status']}")
    print("Reason:", check["reason"])
    print("Evidence:", check["evidence"])
