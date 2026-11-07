
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

        if criterion == "coherent_teaching_flow":
            if any(
                word in lower_line
                for word in [
                    "introduction", "first", "next", "then",
                    "finally", "step", "summary", "in conclusion"
                ]
            ):
                return line

        elif any(word in lower_line for word in keywords[criterion]):
            return line

    return ""


def detect_unsupported_policy_claims(lesson: str) -> list:
    """Detect potentially misleading RAG explanations and unsupported policy figures."""

    patterns = [
        # Unsupported claims about company policies.
        r"\b(?:official|company|corporate)\s+policy\b",
        r"\b(?:must|shall|required to)\b.{0,100}\b\d+\s*(?:days?|weeks?|months?|years?)\b",
        r"\b(?:full refund|guaranteed refund|mandatory refund)\b",
        r"\b(?:return|refund)\s+policy\b.{0,150}\b\d+\b",

        # Specific return/refund periods presented as facts.
        r"\b(?:returned|return|refund|refundable|exchange)\b"
        r".{0,100}\b\d+\s*(?:days?|weeks?)\b",

        # Misleading claims that retrieval automatically changes
        # the model's permanent memory.
        r"\b(?:adds?|stores?|saves?)\b.{0,80}"
        r"\b(?:retrieved information|retrieved data|retrieved text|"
        r"external information|external data)\b.{0,80}"
        r"\b(?:permanent|long.term)?\s*memory\b",

        r"\b(?:retrieved information|retrieved data|retrieved text)\b"
        r".{0,80}\b(?:becomes?|is stored in|gets saved in)\b"
        r".{0,80}\b(?:permanent|long.term)?\s*memory\b",
    ]

    findings = []

    for pattern in patterns:
        matches = re.findall(pattern, lesson, flags=re.IGNORECASE)
        findings.extend(matches)

    return list(dict.fromkeys(findings))


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
   Check every important factual and technical claim.

   For RAG, verify that:
   - RAG stands for Retrieval-Augmented Generation.
   - RAG retrieves relevant information from external sources.
   - Retrieved information is provided to the language model
     to help generate an answer.
   - RAG can reduce hallucinations but cannot eliminate them.
   - RAG does not guarantee that every answer is correct.

   Check for unsupported or invented information:
   - Flag fabricated prices, percentages, dates, deadlines, return periods, company policies, and other specific figures.
   - Flag fictional policies presented as facts from real companies.
   - Flag claims that information came from a real document when no document was provided.
   - Allow clearly labelled hypothetical examples, but do not allow invented details to be presented as verified facts.

   PASS only when the lesson is technically accurate and contains no unsupported factual claims.
   Otherwise, FAIL.

STRICT ACCURACY AND GROUNDING RULES:

1. RAG stands for Retrieval-Augmented Generation.
2. Retrieved information is provided to the language model as context for generating an answer. Do not claim that retrieval automatically adds information to the model's permanent memory.
3. RAG can reduce hallucinations but cannot guarantee completely correct answers.
4. Check all specific numbers, dates, deadlines, prices, percentages, return periods, and company policies.
5. Do not accept invented policy figures presented as real facts.
6. A hypothetical company example must clearly identify invented policy details and figures as fictional.
7. Do not claim that a system retrieved information from a real document unless that document was actually provided or the example is clearly hypothetical.
8. A heading or disclaimer alone does not make an inaccurate explanation acceptable.
9. Mark accuracy_and_grounding as FAIL if the lesson contains a misleading technical explanation or an unsupported factual claim.
10. Mark PASS only when the actual explanations and examples are accurate and appropriately qualified.


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
- Check the actual explanations, not just headings or keywords.
- A heading alone is never sufficient evidence.
- A generic example alone does not prove technical accuracy.
- Unsupported factual claims must cause accuracy_and_grounding to FAIL.
- If uncertain whether an important factual claim is supported,
  do not automatically PASS it.
- Do not invent facts or examples.
- Do not generate evidence quotations.

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
    # Deterministic safeguard for unsupported policy claims.
    policy_findings = detect_unsupported_policy_claims(lesson)

    if policy_findings:
        checks["accuracy_and_grounding"]["status"] = "FAIL"
        checks["accuracy_and_grounding"]["reason"] = (
            "Potentially unsupported policy claims detected: "
            + "; ".join(policy_findings)
        )
        checks["accuracy_and_grounding"]["suggestion"] = (
            "Remove unsupported policy figures and claims, "
            "or clearly identify them as hypothetical examples."
        )
    all_passed = all(
        checks[item]["status"] == "PASS"
        for item in RUBRIC
    )

    return {
        "overall_status": "PASS" if all_passed else "FAIL",
        "checks": checks
    }
