data base sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  password VARCHAR(100),
  path JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CREATE TABLE paths (
--     id SERIAL PRIMARY KEY,
--     title VARCHAR(100),
--     type VARCHAR(50),
--     estimated_time FLOAT,
--     load VARCHAR(50),
--     difficulty INT,
--     resources JSON,
--     embedding JSON,
--     prerequisites JSON,
--     subnodes JSON
-- );

-- CREATE TABLE topics (
--     id SERIAL PRIMARY KEY,
--     title VARCHAR(100),
--     type VARCHAR(50),
--     estimated_time FLOAT,
--     load VARCHAR(50),
--     difficulty INT,
--     resources JSON,
--     embedding JSON,
--     prerequisites JSON,
--     subtopics JSON
-- );


CREATE TABLE user_learning_paths (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    learner_type VARCHAR(50) NOT NULL,
    time_availability VARCHAR(50) NOT NULL,
    learning_domain VARCHAR(50) NOT NULL,
    study_weeks INTEGER DEFAULT 12,
    path_data JSON NOT NULL,
    weekly_schedule JSON NOT NULL,
    stats JSON NOT NULL,
    current_week INTEGER DEFAULT 1,
    completed_nodes JSON DEFAULT '[]',
    progress_percentage INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);


--------For Storing user activity----------
CREATE TABLE user_activity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,      
    description TEXT,                       
    duration_seconds INTEGER DEFAULT 0,     
    created_at TIMESTAMP DEFAULT NOW()      
);

CREATE TABLE quiz_results (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    module_id VARCHAR(100) NOT NULL,
    topic VARCHAR(200) NOT NULL,
    num_questions INTEGER NOT NULL,
    difficulty_level VARCHAR(50) NOT NULL,
    score INTEGER NOT NULL,
    correct_answers INTEGER NOT NULL,
    completion_status VARCHAR(20) DEFAULT 'completed',
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quiz_data JSONB, -- Store the complete quiz questions and answers
    user_answers JSONB, -- Store what user selected for each question
    time_taken_seconds INTEGER, -- Time taken to complete the quiz
    confidence_rating INTEGER, -- User's confidence before/after quiz
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);