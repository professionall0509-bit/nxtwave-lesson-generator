
import json as json_lib

from agents.generator import generate_lesson
from agents.evaluator import evaluate_lesson

print("Generating lesson...")

lesson = generate_lesson("Introduction to RAG")

print("\nEvaluating lesson...")

result = evaluate_lesson(
    topic="Introduction to RAG",
    lesson=lesson
)

print("\n========== EVALUATION RESULT ==========")

print(json_lib.dumps(result, indent=4))
