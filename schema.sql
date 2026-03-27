-- Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual quiz answers
CREATE TABLE IF NOT EXISTS quiz_results (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    topic VARCHAR(100) NOT NULL,
    question TEXT NOT NULL,
    student_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds INTEGER,
    ai_feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated performance (summary table)
CREATE TABLE IF NOT EXISTS performance_history (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id),
    topic VARCHAR(100) NOT NULL,
    total_attempts INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    average_score DECIMAL(5,2),
    average_time_seconds INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, topic)
);