from pydantic import BaseModel
from typing import Optional

# This is the data we expect when a student submits an answer
class SubmitAnswer(BaseModel):
    student_id: int
    topic: str
    question: str
    student_answer: str
    correct_answer: str
    time_taken_seconds: Optional[int] = None

# This is what the API will return after processing
class AnswerResponse(BaseModel):
    is_correct: bool
    ai_feedback: str