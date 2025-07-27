-- Migration: Rename metadata column to message_metadata
-- Description: Fixes SQLAlchemy reserved word conflict by renaming metadata column

-- Rename the metadata column to message_metadata
ALTER TABLE message RENAME COLUMN metadata TO message_metadata;

-- Update the comment
COMMENT ON COLUMN message.message_metadata IS 'JSON string for additional message metadata'; 