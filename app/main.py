from fastapi import FastAPI
from app.database import Base, engine
from app.models.quiz import StudentAnswer 
from app.routers import quiz  # import your quiz router here
from app.database.base import init_db

app = FastAPI(title="Adaptive Learning System")

init_db()

# ✅ Include the quiz router
app.include_router(quiz.router)

# Health check endpoint
@app.get("/health")
async def health_check():
    async with db.pool.acquire() as conn:
        result = await conn.fetchval("SELECT 1")
        return {"status": "healthy", "db": result == 1}