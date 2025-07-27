-- Create saved_prompts table for PostgreSQL
DROP TABLE IF EXISTS saved_prompt;
CREATE TABLE saved_prompt (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    original_message TEXT NOT NULL,
    model VARCHAR(100) NOT NULL,
    prompt_content TEXT NOT NULL,
    prompt_type VARCHAR(100),
    provider VARCHAR(100),
    prompt_metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES "user" (id)
);

-- Create index for faster queries
DROP INDEX IF EXISTS idx_saved_prompt_user_id;
CREATE INDEX idx_saved_prompt_user_id ON saved_prompt(user_id);
DROP INDEX IF EXISTS idx_saved_prompt_created_at;
CREATE INDEX idx_saved_prompt_created_at ON saved_prompt(created_at); 