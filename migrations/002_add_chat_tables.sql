-- Migration: Add chat tables
-- Description: Creates tables for chat conversations and messages

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversation (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    conversation_type VARCHAR(50) DEFAULT 'text'
);

-- Create messages table
CREATE TABLE IF NOT EXISTS message (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    file_path VARCHAR(500),
    file_name VARCHAR(255),
    file_size INTEGER,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tokens_used INTEGER,
    model_used VARCHAR(100),
    provider_used VARCHAR(100),
    response_time FLOAT,
    message_metadata TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON conversation(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_updated_at ON conversation(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_active ON conversation(is_active);

CREATE INDEX IF NOT EXISTS idx_message_conversation_id ON message(conversation_id);
CREATE INDEX IF NOT EXISTS idx_message_created_at ON message(created_at);
CREATE INDEX IF NOT EXISTS idx_message_role ON message(role);

-- Create trigger to update conversation updated_at timestamp
CREATE OR REPLACE FUNCTION update_conversation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_updated_at
    AFTER INSERT OR UPDATE ON message
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_updated_at();

-- Add comments for documentation
COMMENT ON TABLE conversation IS 'Stores chat conversations for users';
COMMENT ON TABLE message IS 'Stores individual messages within conversations';
COMMENT ON COLUMN conversation.conversation_type IS 'Type of conversation: text, image, multimodal';
COMMENT ON COLUMN message.role IS 'Message role: user, assistant, or system';
COMMENT ON COLUMN message.content_type IS 'Type of content: text, image, file';
COMMENT ON COLUMN message.message_metadata IS 'JSON string for additional message metadata'; 