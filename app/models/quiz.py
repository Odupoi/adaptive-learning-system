from sqlalchemy import Column, Integer, String, Boolean, Text
from app.database.base import Base
#from sqlalchemy.orm import declarative_base
#Base = declarative_base()

class StudentAnswer(Base):
    __tablename__ = "student_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    feedback = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium")