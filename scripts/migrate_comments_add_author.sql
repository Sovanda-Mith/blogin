-- Migration: Add author caching fields to comments table
-- Run this against the blogin database

-- Add new columns to the comments.comments table
ALTER TABLE comments.comments ADD COLUMN IF NOT EXISTS author_username VARCHAR(50);
ALTER TABLE comments.comments ADD COLUMN IF NOT EXISTS author_display_name VARCHAR(100);
ALTER TABLE comments.comments ADD COLUMN IF NOT EXISTS author_avatar_url VARCHAR(500);

-- Update existing comments with author info from users.profiles
UPDATE comments.comments c
SET 
    author_username = p.username,
    author_display_name = p.display_name,
    author_avatar_url = p.avatar_url
FROM users.profiles p
WHERE c.author_id = p.user_id
  AND c.author_username IS NULL;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_comments_author_username ON comments.comments(author_username);

-- Verify the migration
SELECT 
    id,
    author_username,
    author_display_name,
    author_avatar_url IS NOT NULL as has_avatar
FROM comments.comments
LIMIT 10;
