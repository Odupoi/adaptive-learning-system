from app.config import get_settings
from groq import Groq
import asyncio
from sqlalchemy.orm import Session
from app.models.quiz import StudentAnswer

settings = get_settings()
client = Groq(api_key=settings.groq_api_key)


# ✅ Move OUTSIDE (global function)
def get_next_difficulty(current: str, is_correct: bool) -> str:
    levels = ["easy", "medium", "hard"]

    if current not in levels:
        return "medium"

    index = levels.index(current)

    if is_correct and index < 2:
        return levels[index + 1]  # harder
    elif not is_correct and index > 0:
        return levels[index - 1]  # easier

    return current


# ✅ Feedback generator
async def generate_feedback(answer, db: Session) -> str:
    """
    Generate AI feedback and save to database.
    """
    if answer.is_correct:
        prompt = f"""
        The student answered correctly.
        Topic: {answer.topic}
        Question: {answer.question}
        Student Answer: {answer.student_answer}

        Write:
        1. Praise the student.
        2. Give a slightly harder follow-up question.
        Respond in plain text.
        """
    else:
        prompt = f"""
        The student answered incorrectly.
        Topic: {answer.topic}
        Question: {answer.question}
        Student Answer: {answer.student_answer}
        Correct Answer: {answer.correct_answer}

        Write a detailed, step-by-step explanation of why the student's answer is wrong.
        Include:
        1. Correct solution method.
        2. Encouragement.
        3. A follow-up practice question.
        Respond in plain text.
        """

    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
        )

        feedback_text = response.choices[0].message.content.strip()

        # ✅ Save to DB
        db_answer = StudentAnswer(
            topic=answer.topic,
            question=answer.question,
            student_answer=answer.student_answer,
            correct_answer=answer.correct_answer,
            is_correct=answer.is_correct,
            feedback=feedback_text
        )

        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)

        return feedback_text

    except Exception as e:
        print("Error generating AI feedback:", e)
        return "AI feedback unavailable at the moment."


# ✅ Question generator
async def generate_question(topic: str, difficulty: str = "medium") -> str:
    prompt = f"""
    Generate a {difficulty} difficulty question for the topic: "{topic}".
    Provide only the question text (no answer or explanation).
    Respond in plain text.
    """

    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Error generating AI question:", e)
        return "Unable to generate a question."