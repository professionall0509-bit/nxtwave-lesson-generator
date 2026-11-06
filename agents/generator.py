
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "gemini-3.5-flash-lite"


def generate_lesson(topic: str, feedback: str = "") -> str:
    """Generate a beginner-friendly lesson on the given topic."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from the .env file.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an expert AI educator.

TARGET LEARNER:
An Indian 12th-grade graduate with limited English vocabulary
and no prior knowledge of Artificial Intelligence.

TOPIC: {topic}

TASK:
Create a complete, standalone beginner-friendly lesson.

The lesson must explain:
1. What the topic means.
2. Why it is important.
3. How it works, step by step.
4. A simple real-world example.
5. A practical AI-related example.
6. A short summary of key concepts.
7. Clearly explain the full form of RAG:
   Retrieval-Augmented Generation.
8. Explain Retrieval, Augmented, and Generation separately.
9. Explain the three main steps: question, retrieval, and generation.

RULES:
- Use simple English and short sentences.
- Explain technical words immediately.
- Never assume prior AI knowledge.
- Use relatable examples.
- Keep the teaching flow logical.
- Do not invent facts.

IMPORTANT TECHNICAL ACCURACY RULES:

1. RAG does not completely prevent AI hallucinations.
2. RAG can reduce hallucinations by providing relevant information
   from external sources.
3. RAG does not guarantee that every generated answer is correct.
4. Never use statements such as:
   "RAG stops AI from lying."
   "RAG eliminates hallucinations."
   "RAG always gives correct answers."
5. Never invent specific facts, figures, policies, or page numbers.
6. If using a hypothetical company or bank example, clearly label it
   as hypothetical.
7. Never present an invented policy as information from a real document.
8. Use general examples when no source document is provided.

Use this accurate explanation:
"RAG helps reduce incorrect answers by allowing AI to retrieve
relevant information from external sources. However, AI can still
make mistakes or misunderstand the retrieved information."

PREVIOUS EVALUATOR FEEDBACK:
{feedback if feedback else "No previous feedback. This is the first attempt."}

Improve the lesson using the feedback if provided.

Return only the lesson in Markdown.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty lesson.")

    return response.text
