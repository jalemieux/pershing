-- Migration: Create Buddy tables
-- Date: 2024-01-01

-- Create buddy table
CREATE TABLE IF NOT EXISTS buddy (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    initial_prompt TEXT NOT NULL,
    memory_type VARCHAR(50) NOT NULL DEFAULT 'short_term',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create buddy_tool table
CREATE TABLE IF NOT EXISTS buddy_tool (
    id SERIAL PRIMARY KEY,
    buddy_id INTEGER NOT NULL REFERENCES buddy(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    tool_type VARCHAR(100) NOT NULL,
    tool_config TEXT,
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create buddy_memory table
CREATE TABLE IF NOT EXISTS buddy_memory (
    id SERIAL PRIMARY KEY,
    buddy_id INTEGER NOT NULL REFERENCES buddy(id) ON DELETE CASCADE,
    memory_type VARCHAR(50) NOT NULL,
    memory_key VARCHAR(255) NOT NULL,
    memory_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Add buddy_id column to existing conversation table
ALTER TABLE conversation ADD COLUMN IF NOT EXISTS buddy_id INTEGER REFERENCES buddy(id) ON DELETE SET NULL;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_buddy_user_id ON buddy(user_id);
CREATE INDEX IF NOT EXISTS idx_buddy_tool_buddy_id ON buddy_tool(buddy_id);
CREATE INDEX IF NOT EXISTS idx_buddy_memory_buddy_id ON buddy_memory(buddy_id);
CREATE INDEX IF NOT EXISTS idx_buddy_memory_type ON buddy_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_buddy_memory_expires_at ON buddy_memory(expires_at);
CREATE INDEX IF NOT EXISTS idx_conversation_buddy_id ON conversation(buddy_id); 