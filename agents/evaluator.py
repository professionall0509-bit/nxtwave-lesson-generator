
import os
import json
import re

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"

RUBRIC = [
    "accuracy_and_grounding",
    "beginner_friendly_language",
    "teaches_by_example",
    "clear_and_jargon_free",
    "covers_key_points",
    "coherent_teaching_flow",
]


def extract_evidence(lesson: str, criterion: str) -> str:
    """Select real text from the lesson as supporting evidence."""

    lines = [
        line.strip()
        for line in lesson.splitlines()
        if line.strip()
    ]

    # Remove Markdown heading and bullet markers.
    clean_lines = [
        re.sub(r"^#{1,6}\s*|^[-*]\s*", "", line).strip()
        for line in lines
    ]

    keywords = {
        "accuracy_and_grounding": [
            "reduce", "hallucination", "mistake", "correct",
            "external source", "retrieved"
        ],
        "beginner_friendly_language": [
            "simple", "imagine", "think", "let us",
            "for example"
        ],
        "teaches_by_example": [
            "example", "imagine", "library", "school",
            "company", "customer"
        ],
        "clear_and_jargon_free": [
            "retrieval", "generation", "augmented",
            "means", "finding", "search"
        ],
        "covers_key_points": [
            "what", "why", "how", "step", "rag"
        ],
        "coherent_teaching_flow": [
            "what", "why", "how", "summary",
            "step", "introduction"
        ],
    }

    for line in clean_lines:
        if len(line) < 20:
            continue

        lower_line = line.lower()

        if any(word in lower_line for word in keywords[criterion]):
            return line

    return ""


def evaluate_lesson(topic: str, lesson: str) -> dict:
    """Evaluate a lesson using six strict PASS/FAIL criteria."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    if not lesson or not lesson.strip():
        raise ValueError("Lesson cannot be empty.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are a strict quality evaluator for beginner learning content.

TARGET LEARNER:
An Indian 12th-grade graduate with limited English vocabulary
and no previous knowledge of Artificial Intelligence.

TOPIC: {topic}

LESSON TO EVALUATE:
{lesson}

Evaluate these six criteria:

1. accuracy_and_grounding:
   Are explanations technically correct?
   Are factual claims supported or appropriately qualified?
   For RAG, it can reduce hallucinations but cannot guarantee correctness.
   Flag invented real-world policies presented as facts.

2. beginner_friendly_language:
   Is the lesson understandable to a complete beginner?
   Are sentences simple and easy to follow?

3. teaches_by_example:
   Does it include useful examples that explain the concept?

4. clear_and_jargon_free:
   Are technical terms explained immediately?
   Is unexplained jargon avoided?

5. covers_key_points:
   Does it explain WHAT the topic is, WHY it matters,
   and HOW it works?

6. coherent_teaching_flow:
   Does the lesson follow a logical teaching sequence?

STRICT RULES:
- Each criterion must receive only PASS or FAIL.
- No partial credit.
- Evaluate only the actual lesson.
- Do not invent facts or examples.
- Do not generate evidence quotations.
- Do not pass a criterion simply because a heading exists.

Return ONLY this JSON structure:

{{
  "checks": {{
    "accuracy_and_grounding": {{
      "status": "PASS",
      "reason": "Specific explanation",
      "suggestion": "Practical improvement"
    }},
    "beginner_friendly_language": {{
      "status": "PASS",
      "reason": "Specific explanation",
      "suggestion": "Practical improvement"
    }},
    "teaches_by_example": {{
      "status": "PASS",
      "reason": "Specific explanation",
      "suggestion": "Practical improvement"
    }},
    "clear_and_jargon_free": {{
      "status": "PASS",
      "reason": "Specific explanation",
      "suggestion": "Practical improvement"
    }},
    "covers_key_points": {{
      "status": "PASS",
      "reason": "Specific explanation",
      "suggestion": "Practical improvement"
    }},
    "coherent_teaching_flow": {{
      "status": "PASS",
      "reason": "Specific explanation",
      "suggestion": "Practical improvement"
    }}
  }}
}}

Every criterion must be present.
Use only PASS or FAIL.
Do not include evidence.
Do not include overall_status.
Do not use Markdown code fences.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )

    if not response.text:
        raise RuntimeError("Evaluator returned an empty response.")

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise ValueError("Evaluator returned invalid JSON.") from exc

    if not isinstance(result, dict):
        raise ValueError("Evaluator response must be a JSON object.")

    checks = result.get("checks")

    if not isinstance(checks, dict) or set(checks) != set(RUBRIC):
        raise ValueError("Evaluator response is missing rubric criteria.")

    # Validate Gemini's evaluation and attach Python-selected evidence.
    for criterion in RUBRIC:
        check = checks[criterion]

        if not isinstance(check, dict):
            raise ValueError(f"Invalid result for {criterion}.")

        if check.get("status") not in ("PASS", "FAIL"):
            raise ValueError(f"Invalid status for {criterion}.")

        if not isinstance(check.get("reason"), str):
            raise ValueError(f"Missing reason for {criterion}.")

        if not isinstance(check.get("suggestion"), str):
            raise ValueError(f"Missing suggestion for {criterion}.")

        evidence = extract_evidence(lesson, criterion)

        check["evidence"] = evidence

        # No evidence means the result cannot be accepted as PASS.
        if not evidence:
            check["status"] = "FAIL"
            check["reason"] = (
                "No supporting passage could be extracted "
                "from the original lesson."
            )
            check["suggestion"] = (
                "Add a clear explanation or example to the lesson."
            )

    all_passed = all(
        checks[item]["status"] == "PASS"
        for item in RUBRIC
    )

    return {
        "overall_status": "PASS" if all_passed else "FAIL",
        "checks": checks
    }
