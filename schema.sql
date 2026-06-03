CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    student_name VARCHAR(120) NOT NULL,
    prediction VARCHAR(8) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
