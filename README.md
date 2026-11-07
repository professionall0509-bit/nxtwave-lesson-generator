# Self-Evaluating AI Lesson Generator

An AI-powered lesson generation system that creates beginner-friendly educational content, evaluates its quality using six strict criteria, and improves future generations using persistent memory and feedback.

## Project Overview

This project generates educational lessons for beginners using Generative AI.

For the assignment topic, the system generates a lesson on **Introduction to RAG (Retrieval-Augmented Generation)**, evaluates the generated content, and decides whether it meets the required quality standards.

If a lesson fails evaluation, the system records the reasons for rejection, provides improvement feedback, and retries generation within a configured limit.

It also stores previous results and repeated improvement rules in SQLite to support future generations.

## Key Features

- **AI-powered lesson generation:** Generates beginner-friendly lessons using Google Gemini.
- **Six-criterion evaluation:** Evaluates accuracy, clarity, examples, coverage, language, and teaching flow.
- **PASS/FAIL validation:** Accepts a lesson only when all required evaluation criteria pass.
- **Automatic regeneration:** Sends evaluation feedback back to the generator when a lesson fails.
- **Retry control:** Supports a maximum of two retries after the initial generation.
- **Rejection logging:** Records failed attempts, reasons, and improvement suggestions.
- **Persistent memory:** Stores previous runs and learned improvement rules using SQLite.
- **Self-evolving feedback:** Reuses repeated failure patterns to guide future generation.
- **Streamlit interface:** Provides an interactive interface for generating, evaluating, and downloading lessons.

## System Architecture

The workflow is built using LangGraph.

```text
              User enters topic
                     |
                     v
             Retrieve past memory
                     |
                     v
              Generate lesson
                     |
                     v
             Evaluate the lesson
                     |
                     v
              PASS or FAIL?
                /       \
              PASS      FAIL
               |          |
               v          v
          Save lesson   Record rejection
               |          |
               |       Generate feedback
               |          |
               |       Retry generation
               |          |
               v          v
          Save results   Re-evaluate
               |
               v
        Update persistent memory
```

## Evaluation Criteria

Every generated lesson is evaluated against six criteria.

| Criterion | Description |
|---|---|
| Accuracy and Grounding | Checks factual correctness and unsupported claims. |
| Beginner-Friendly Language | Ensures the lesson is understandable for beginners. |
| Teaches by Example | Checks whether examples explain the concepts clearly. |
| Clear and Jargon-Free | Ensures technical terms are explained simply. |
| Covers Key Points | Checks whether essential topic concepts are covered. |
| Coherent Teaching Flow | Evaluates the logical sequence of the lesson. |

**Acceptance rule:** All six criteria must PASS for the lesson to be accepted.

## Technology Stack

- Python
- Google Gemini API
- LangGraph
- LangChain
- Streamlit
- SQLite
- Pydantic
- Pytest

## Project Structure

```text
nxtwave-lesson-generator/
│
├── agents/
│   ├── generator.py
│   └── evaluator.py
│
├── workflow/
│   ├── graph.py
│   ├── nodes.py
│   └── state.py
│
├── memory/
│   └── database.py
│
├── outputs/
│   ├── final_lesson.md
│   └── rejection_log.json
│
├── tests/
│
├── app.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup and Installation

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd nxtwave-lesson-generator
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit your actual API key to GitHub.

### 5. Run the application

Launch the Streamlit interface:

```bash
streamlit run app.py
```

Alternatively, run the command-line workflow:

```bash
python main.py
```

## Testing

Run the accuracy rejection test:

```bash
python test_accuracy_rejection.py
```

Run the valid lesson test:

```bash
python test_accuracy_pass.py
```

Run the RAG technical accuracy test:

```bash
python test_rag_accuracy.py
```

These tests verify rejection of fabricated policy claims, acceptance of valid RAG explanations, and detection of misleading claims about permanent model memory.

## Generated Outputs

The system saves:

- `outputs/final_lesson.md` — the accepted lesson, when evaluation passes.
- `outputs/rejection_log.json` — rejection history for the latest run.

Previous runs and repeated learning rules are stored in the SQLite database.

## Limitations

- Evaluation uses an LLM and targeted deterministic checks; it is not a complete independent fact-checking system.
- The quality of generated lessons depends on the underlying language model.
- Gemini API usage is subject to the configured API quota and availability.
- Persistent memory stores feedback patterns; it does not automatically retrain the language model.

## Assignment

Developed as a take-home assignment for the **Associate GenAI Engineer – Content Systems** role at NxtWave.

The project demonstrates AI content generation, structured evaluation, controlled regeneration, rejection tracking, and persistent feedback-based improvement.