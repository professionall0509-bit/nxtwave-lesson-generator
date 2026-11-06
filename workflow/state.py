
from typing import TypedDict, Optional


class LessonState(TypedDict):
    # Input
    topic: str

    # Generated lesson
    lesson: str

    # Evaluator feedback
    feedback: str
    evaluation: dict

    # Retry management
    attempts: int
    max_retries: int

    # Rejection history
    rejection_log: list

    # Final output
    final_lesson: Optional[str]
    status: str
