from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Services
from app.services.ai_service import (
    generate_feedback,
    generate_question,
    get_next_difficulty
)
from app.services.analytics_service import (
    get_all_answers,
    get_topic_stats
)
from app.services.adaptive_service import (
    suggest_topic,
    suggest_question
)

# Database
from app.database.base import get_db


router = APIRouter(prefix="/quiz", tags=["quiz"])


# =========================
# 📦 Request Model
# =========================
class SubmitAnswer(BaseModel):
    topic: str
    question: str
    student_answer: str
    correct_answer: str | None = None
    is_correct: bool


# =========================
# ✅ Submit Answer
# =========================
@router.post("/submit")
async def submit_answer(answer: SubmitAnswer, db: Session = Depends(get_db)):
    """
    Accepts a student's answer and returns AI-generated feedback.
    """
    try:
        feedback = await generate_feedback(answer, db)
        return {"feedback": feedback}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# =========================
# 🧠 FULL LEARNING FLOW
# =========================
@router.post("/learn")
async def learning_flow(answer: SubmitAnswer, db: Session = Depends(get_db)):
    """
    Complete adaptive learning cycle:
    1. Save answer
    2. Generate feedback
    3. Adjust difficulty
    4. Generate next question
    """
    try:
        # Step 1: Feedback + Save
        feedback = await generate_feedback(answer, db)

        # Step 2: Decide next difficulty
        current_difficulty = "medium"  # can later store in DB
        next_difficulty = get_next_difficulty(current_difficulty, answer.is_correct)

        # Step 3: Generate next question
        next_question = await generate_question(answer.topic, next_difficulty)

        return {
            "feedback": feedback,
            "next": {
                "topic": answer.topic,
                "difficulty": next_difficulty,
                "question": next_question
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 📊 Get All Answers
# =========================
@router.get("/answers")
def list_answers(db: Session = Depends(get_db)):
    """
    Retrieve all stored student answers.
    """
    try:
        answers = get_all_answers(db)

        return {
            "answers": [
                {
                    "id": a.id,
                    "topic": a.topic,
                    "question": a.question,
                    "student_answer": a.student_answer,
                    "correct_answer": a.correct_answer,
                    "is_correct": a.is_correct,
                    "feedback": a.feedback
                }
                for a in answers
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 📈 Analytics
# =========================
@router.get("/analytics")
def topic_analytics(db: Session = Depends(get_db)):
    """
    Get performance stats per topic.
    """
    try:
        stats = get_topic_stats(db)
        return {"analytics": stats}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Query
from app.services.analytics_service import get_student_progress, get_leaderboard

@router.get("/analytics/student")
def student_progress(student_id: str, db: Session = Depends(get_db)):
    """
    Get topic-wise progress for a single student.
    """
    try:
        progress = get_student_progress(db, student_id)
        return {"student_id": student_id, "progress": progress}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/leaderboard")
def leaderboard(top_n: int = Query(10, description="Top N students"), db: Session = Depends(get_db)):
    """
    Get top N students by overall accuracy.
    """
    try:
        top_students = get_leaderboard(db, top_n)
        return {"leaderboard": top_students}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# 🎯 Adaptive Topic Suggestion
# =========================
@router.get("/adaptive/topic")
def next_topic(db: Session = Depends(get_db)):
    """
    Suggest weakest topic for improvement.
    """
    try:
        topic = suggest_topic(db)
        return {"suggested_topic": topic}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# ❓ Adaptive Question (from DB logic)
# =========================
@router.get("/adaptive/question")
def next_question(topic: str, db: Session = Depends(get_db)):
    """
    Suggest a question based on past performance.
    """
    try:
        question = suggest_question(db, topic)
        return {"suggested_question": question}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 🤖 AI Question Generator
# =========================
@router.get("/generate")
async def ai_generate_question(
    topic: str = Query(..., description="Topic"),
    difficulty: str = Query("medium", description="easy | medium | hard"),
):
    """
    Generate AI-powered question.
    """
    try:
        question = await generate_question(topic, difficulty)

        return {
            "topic": topic,
            "difficulty": difficulty,
            "question": question
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))