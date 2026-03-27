# app/services/analytics_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.quiz import StudentAnswer
from typing import List, Dict

def get_all_answers(db: Session) -> List[StudentAnswer]:
    """
    Return all student answers with feedback.
    """
    return db.query(StudentAnswer).all()


def get_topic_stats(db: Session) -> Dict[str, Dict[str, float]]:
    """
    Calculate correct/incorrect stats per topic across all students.
    Returns a dictionary like:
    {
        "Math": {"correct": 10, "incorrect": 5, "accuracy": 0.67},
        "Science": {"correct": 7, "incorrect": 3, "accuracy": 0.7},
    }
    """
    results = (
        db.query(
            StudentAnswer.topic,
            func.sum(StudentAnswer.is_correct.cast(Integer)).label("correct"),
            func.count(StudentAnswer.id).label("total")
        )
        .group_by(StudentAnswer.topic)
        .all()
    )
    
    stats = {}
    for topic, correct, total in results:
        stats[topic] = {
            "correct": int(correct),
            "incorrect": int(total - correct),
            "accuracy": round(correct / total, 2) if total else 0.0
        }
    return stats


def get_student_progress(db: Session, student_id: str) -> Dict[str, Dict[str, float]]:
    """
    Returns a student's topic-wise performance.
    {
        "Math": {"correct": 5, "total": 7, "accuracy": 0.71, "difficulty_progression": ["medium", "hard"]},
        "Science": {"correct": 2, "total": 3, "accuracy": 0.67, "difficulty_progression": ["easy", "medium"]}
    }
    """
    answers = db.query(StudentAnswer).filter(StudentAnswer.student_id == student_id).all()
    
    progress = {}
    for ans in answers:
        if ans.topic not in progress:
            progress[ans.topic] = {"correct": 0, "total": 0, "difficulty_progression": []}
        progress[ans.topic]["total"] += 1
        progress[ans.topic]["correct"] += int(ans.is_correct)
        progress[ans.topic]["difficulty_progression"].append(ans.difficulty)
    
    # calculate accuracy
    for topic in progress:
        total = progress[topic]["total"]
        correct = progress[topic]["correct"]
        progress[topic]["accuracy"] = round(correct / total, 2) if total else 0.0
    
    return progress


def get_leaderboard(db: Session, top_n: int = 10) -> List[Dict[str, float]]:
    """
    Returns top students by overall accuracy.
    """
    results = (
        db.query(
            StudentAnswer.student_id,
            func.sum(StudentAnswer.is_correct.cast(Integer)).label("correct"),
            func.count(StudentAnswer.id).label("total")
        )
        .group_by(StudentAnswer.student_id)
        .all()
    )
    
    leaderboard = []
    for student_id, correct, total in results:
        leaderboard.append({
            "student_id": student_id,
            "correct": int(correct),
            "total": int(total),
            "accuracy": round(correct / total, 2) if total else 0.0
        })
    
    # sort descending by accuracy
    leaderboard.sort(key=lambda x: x["accuracy"], reverse=True)
    return leaderboard[:top_n]