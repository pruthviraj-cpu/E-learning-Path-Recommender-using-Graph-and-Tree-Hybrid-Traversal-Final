CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100),
  password VARCHAR(100),
  path JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE paths (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    type VARCHAR(50),
    estimated_time FLOAT,
    load VARCHAR(50),
    difficulty INT,
    resources JSON,
    embedding JSON,
    prerequisites JSON,
    subnodes JSON
);

CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    type VARCHAR(50),
    estimated_time FLOAT,
    load VARCHAR(50),
    difficulty INT,
    resources JSON,
    embedding JSON,
    prerequisites JSON,
    subtopics JSON
);
