-- Create tables for Pershing application
-- This SQL file creates all necessary tables for the Flask application

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS user_session;
DROP TABLE IF EXISTS verification_code;
DROP TABLE IF EXISTS user;

-- Create users table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    is_admin BOOLEAN DEFAULT 0
);

-- Create verification_codes table
CREATE TABLE IF NOT EXISTS verification_code (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL,
    code_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    attempts INTEGER DEFAULT 0,
    used BOOLEAN DEFAULT 0
);

-- Create user_sessions table
CREATE TABLE IF NOT EXISTS user_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    device_info TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Create saved_prompts table for PostgreSQL
CREATE TABLE IF NOT EXISTS saved_prompt (
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
CREATE INDEX IF NOT EXISTS idx_saved_prompt_user_id ON saved_prompt(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_prompt_created_at ON saved_prompt(created_at); 

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_verification_codes_email ON verification_codes(email);
CREATE INDEX IF NOT EXISTS idx_verification_codes_expires ON verification_codes(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at);

-- Insert a default admin user (password: admin123)
-- You should change this password in production
INSERT INTO user (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:600000$your_salt_here$hash_here', TRUE);

-- Note: The password_hash above is a placeholder. In a real application,
-- you would generate this using the application's password hashing function.
-- For now, you can create an admin user through the application's registration process. 