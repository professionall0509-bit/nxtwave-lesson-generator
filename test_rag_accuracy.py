
from agents.evaluator import detect_unsupported_policy_claims

bad_lesson = """
RAG retrieves information from external documents
and adds the retrieved information to the AI's permanent memory.
"""

good_lesson = """
RAG retrieves relevant information from external documents
and provides it to the language model as context
when generating an answer.
"""

bad_findings = detect_unsupported_policy_claims(bad_lesson)
good_findings = detect_unsupported_policy_claims(good_lesson)

print("Misleading explanation findings:", bad_findings)
print("Correct explanation findings:", good_findings)

assert bad_findings, "The misleading memory claim was not detected."
assert not good_findings, "The correct explanation was incorrectly flagged."

print("\nSUCCESS: RAG memory accuracy checks passed.")
