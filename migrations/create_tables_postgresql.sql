-- Create tables for Pershing application (PostgreSQL version)
-- This SQL file creates all necessary tables for the Flask application

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS user_session CASCADE;
DROP TABLE IF EXISTS verification_code CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- Create user table
CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Create verification_code table
CREATE TABLE verification_code (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    code_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    attempts INTEGER DEFAULT 0,
    used BOOLEAN DEFAULT FALSE
);

-- Create user_session table
CREATE TABLE user_session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    device_info TEXT,
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_username ON "user"(username);
CREATE INDEX idx_verification_code_email ON verification_code(email);
CREATE INDEX idx_verification_code_expires ON verification_code(expires_at);
CREATE INDEX idx_user_session_user_id ON user_session(user_id);
CREATE INDEX idx_user_session_token ON user_session(session_token);
CREATE INDEX idx_user_session_expires ON user_session(expires_at);

-- Insert a default admin user (password: admin123)
-- You should change this password in production
INSERT INTO "user" (username, email, password_hash, is_admin) 
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:600000$your_salt_here$hash_here', TRUE);

-- Note: The password_hash above is a placeholder. In a real application,
-- you would generate this using the application's password hashing function.
-- For now, you can create an admin user through the application's registration process. 