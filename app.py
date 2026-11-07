
import json
from pathlib import Path

import streamlit as st

from workflow.graph import lesson_workflow
from memory.database import (
    initialize_database,
    save_run,
    get_previous_runs,
    learn_from_rejections,
    get_learning_rules
)

OUTPUT_DIR = Path(__file__).parent / "outputs"


def build_memory_feedback(previous_runs, learning_rules):
    feedback_parts = []

    for run in previous_runs[:3]:
        rejection_log = json.loads(run["rejection_log"] or "[]")

        for rejection in rejection_log:
            for criterion, details in rejection["failed_criteria"].items():
                feedback_parts.append(
                    f"{criterion}: {details['suggestion']}"
                )

    for rule in learning_rules:
        feedback_parts.append(
            f"{rule['criterion']}: {rule['suggestion']}"
        )

    return "\n".join(dict.fromkeys(feedback_parts))


def save_outputs(result):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if result["final_lesson"]:
        (OUTPUT_DIR / "final_lesson.md").write_text(
            result["final_lesson"],
            encoding="utf-8"
        )

    (OUTPUT_DIR / "rejection_log.json").write_text(
        json.dumps(
            result["rejection_log"],
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def run_generation(topic):
    initialize_database()

    previous_runs = get_previous_runs(topic)
    learning_rules = get_learning_rules()

    memory_feedback = build_memory_feedback(
        previous_runs,
        learning_rules
    )

    initial_state = {
        "topic": topic,
        "lesson": "",
        "feedback": memory_feedback,
        "evaluation": {},
        "attempts": 0,
        "max_retries": 2,
        "rejection_log": [],
        "final_lesson": None,
        "status": "STARTED"
    }

    result = lesson_workflow.invoke(initial_state)

    save_run(
        topic=topic,
        status=result["status"],
        attempts=result["attempts"],
        rejection_log=result["rejection_log"]
    )

    learn_from_rejections(result["rejection_log"])
    save_outputs(result)

    return result, len(previous_runs), len(learning_rules)


# ---------------- STREAMLIT UI ----------------

st.set_page_config(
    page_title="AI Lesson Generator",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Self-Evaluating AI Lesson Generator")

st.write(
    "Generate beginner-friendly lessons using AI, "
    "evaluate them against six quality criteria, "
    "and improve future generations using persistent memory."
)

st.divider()

topic = st.text_input(
    "Enter your lesson topic",
    value="Introduction to RAG"
)

generate_button = st.button(
    "Generate and Evaluate Lesson",
    type="primary",
    disabled=not topic.strip()
)

if generate_button:
    try:
        with st.spinner(
            "Generating and evaluating your lesson. Please wait..."
        ):
            result, previous_count, rule_count = run_generation(
                topic.strip()
            )

        st.session_state["result"] = result
        st.session_state["previous_count"] = previous_count
        st.session_state["rule_count"] = rule_count

    except Exception as error:
        st.error(f"Workflow failed: {error}")


# Display results
if "result" in st.session_state:
    result = st.session_state["result"]

    st.divider()
    st.subheader("Workflow Results")

    col1, col2, col3 = st.columns(3)

    col1.metric("Final Status", result["status"])
    col2.metric("Generation Attempts", result["attempts"])
    col3.metric(
        "Previous Runs",
        st.session_state["previous_count"]
    )

    st.write(
        "Learned rules available:",
        st.session_state["rule_count"]
    )

    # Evaluation results
    st.subheader("Evaluation Results")

    evaluation = result.get("evaluation", {})
    checks = evaluation.get("checks", {})

    if checks:
        for criterion, details in checks.items():
            status = details.get("status", "UNKNOWN")

            with st.expander(
                f"{'✅' if status == 'PASS' else '❌'} "
                f"{criterion.replace('_', ' ').title()} — {status}"
            ):
                st.write("**Reason:**", details.get("reason", ""))
                st.write(
                    "**Improvement:**",
                    details.get("suggestion", "")
                )
                if details.get("evidence"):
                    st.write(
                        "**Evidence:**",
                        details["evidence"]
                    )

    # Final lesson
    if result.get("final_lesson"):
        st.success("The lesson passed all evaluation checks.")

        st.subheader("Generated Lesson")

        st.markdown(result["final_lesson"])

        st.download_button(
            label="Download Final Lesson",
            data=result["final_lesson"],
            file_name="final_lesson.md",
            mime="text/markdown"
        )
    else:
        st.error(
            "The lesson did not pass evaluation "
            "within the allowed generation attempts."
        )

    # Rejection history
    st.subheader("Rejection Log")

    rejection_log = result.get("rejection_log", [])

    if rejection_log:
        for entry in rejection_log:
            with st.expander(
                f"Rejected Attempt {entry['attempt']}"
            ):
                st.markdown("**Failed criteria:**")

                for criterion, details in entry[
                    "failed_criteria"
                ].items():
                    st.write(
                        f"- {criterion}: {details['reason']}"
                    )
                    st.write(
                        f"  Improvement: {details['suggestion']}"
                    )
    else:
        st.info("No rejected attempts in this run.")

    st.download_button(
        label="Download Rejection Log",
        data=json.dumps(
            rejection_log,
            indent=2,
            ensure_ascii=False
        ),
        file_name="rejection_log.json",
        mime="application/json"
    )
