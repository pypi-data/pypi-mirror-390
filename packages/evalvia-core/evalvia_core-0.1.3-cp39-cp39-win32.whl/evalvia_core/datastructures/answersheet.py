from typing import Dict, List, Optional
from .rubric import Rubric


class Answer:
    """
    Represents an individual answer with its associated pages, text content, and evaluation rubric.
    """
    def __init__(self, q_id: str, text: str, pages: List[int], eval_rubric: Rubric = None, feedback: str = ""):
        self.q_id = q_id
        self.text = text
        self.pages = pages
        self.eval_rubric = eval_rubric if eval_rubric is not None else Rubric([])
        self.feedback = feedback

    def set_eval_rubric(self, rubric: Rubric) -> None:
        """Set the evaluation rubric for this answer."""
        if not isinstance(rubric, Rubric):
            raise TypeError("rubric must be an instance of Rubric")
        self.eval_rubric = rubric

    def set_feedback(self, feedback: str) -> None:
        """Set feedback for this answer."""
        self.feedback = feedback
    
    def get_awarded_marks(self) -> float:
        """Calculate and return the total awarded marks based on the evaluation rubric."""
        return sum([criterion.mark for criterion in self.eval_rubric.criteria if criterion.is_fulfilled])

    def __repr__(self):
        return f"Answer(pages={self.pages}, text={self.text!r}, eval_rubric={self.eval_rubric})"


class Answersheet:
    """
    Represents a complete answersheet containing multiple answers indexed by question ID.
    """
    def __init__(self, subject: str, language: str , class_level: Optional[str] = None):
        self.answers: Dict[str, Answer] = {}
        self.subject = subject
        self.class_level = class_level
        self.language = language

    def add_answer(self, question_id: str, answer: Answer) -> None:
        """Add an answer to the answersheet."""
        if not isinstance(answer, Answer):
            raise TypeError("answer must be an instance of Answer")
        self.answers[question_id] = answer

    def add_rubric(self, question_id: str, rubric: Rubric) -> None:
        """Add a rubric to a specific answer."""
        if question_id not in self.answers:
            raise ValueError(f"cannot add rubric. Question ID '{question_id}' not found in answersheet")
        if not isinstance(rubric, Rubric):
            raise TypeError("rubric must be an instance of Rubric")
        self.answers[question_id].set_eval_rubric(rubric)
    
    def get_rubric(self, question_id: str) -> Rubric:
        """Get the rubric for a specific answer."""
        if question_id not in self.answers:
            return Rubric([])
        return self.answers[question_id].eval_rubric
    
    def add_feedback(self, question_id: str, feedback: str) -> None:
        """Add feedback to a specific answer."""
        if question_id not in self.answers:
            raise ValueError(f"cannot add feedback. Question ID '{question_id}' not found in answersheet")
        self.answers[question_id].set_feedback(feedback)

    def get_answer(self, question_id: str) -> Answer:
        """Get an answer by question ID."""
        if question_id not in self.answers:
            raise ValueError(f"Question ID '{question_id}' not found in answersheet")
        return self.answers[question_id]

    def get_pager(self, question_id: str) -> List[int]:
        """Get the pages for a specific answer."""
        if question_id not in self.answers:
            raise ValueError(f"Question ID '{question_id}' not found in answersheet")
        return self.answers[question_id].pages

    def get_all_answers(self) -> Dict[str, Answer]:
        """Get all answers in the answersheet."""
        return self.answers.copy()

    def get_question_ids(self) -> List[str]:
        """Get all question IDs in the answersheet."""
        return list(self.answers.keys())

    def __repr__(self):
        return f"Answersheet(answers={len(self.answers)})"
