# app/services/adaptive_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.quiz import StudentAnswer

LEVELS = ["easy", "medium", "hard"]

def suggest_topic(db: Session, student_id: str) -> str:
    """
    Suggest the topic where the student is weakest.
    """
    results = (
        db.query(
            StudentAnswer.topic,
            func.avg(StudentAnswer.is_correct.cast(Integer)).label("accuracy")
        )
        .filter(StudentAnswer.student_id == student_id)
        .group_by(StudentAnswer.topic)
        .order_by("accuracy")
        .all()
    )
    
    if results:
        # Pick topic with lowest accuracy
        return results[0].topic
    else:
        # Default fallback if no history
        return "General"

def get_next_difficulty(student_id: str, topic: str, db: Session) -> str:
    """
    Determine the next question difficulty for a topic and student.
    """
    answers = (
        db.query(StudentAnswer)
        .filter(
            StudentAnswer.student_id == student_id,
            StudentAnswer.topic == topic
        )
        .all()
    )
    
    if not answers:
        return "medium"
    
    correct_count = sum(a.is_correct for a in answers)
    total = len(answers)
    accuracy = correct_count / total

    # Increase difficulty if accuracy > 0.8, decrease if <0.5
    last_diff = answers[-1].difficulty if answers else "medium"
    index = LEVELS.index(last_diff)

    if accuracy > 0.8 and index < 2:
        return LEVELS[index + 1]
    elif accuracy < 0.5 and index > 0:
        return LEVELS[index - 1]
    else:
        return last_diff

def suggest_question(db: Session, student_id: str, topic: str, difficulty: str = None) -> dict:
    """
    Returns the next question with difficulty.
    """
    if not difficulty:
        difficulty = get_next_difficulty(student_id, topic, db)
    
    return {
        "topic": topic,
        "difficulty": difficulty,
        "question": f"New {difficulty} question for {topic} goes here"
    }