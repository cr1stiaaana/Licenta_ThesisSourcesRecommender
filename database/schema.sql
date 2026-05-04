-- PostgreSQL Schema for Thesis Sources Recommender
-- Created: 2026-04-29

-- Drop existing tables if they exist
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS articles CASCADE;

-- Users table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Articles metadata table
CREATE TABLE articles (
    id VARCHAR(64) PRIMARY KEY,  -- SHA-256 hash of DOI or normalized title
    title TEXT NOT NULL,
    abstract TEXT,
    authors TEXT,  -- JSON array stored as text
    year INTEGER,
    doi VARCHAR(255),
    url TEXT,
    keywords TEXT,  -- JSON array stored as text
    language VARCHAR(10),  -- 'ro', 'en', or 'mixed'
    faiss_idx INTEGER,  -- Index in FAISS vector store
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ratings/Feedback table
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,  -- Article ID or web resource URL hash
    session_id VARCHAR(255),  -- User session ID or user ID if logged in
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,  -- Optional link to user
    query TEXT NOT NULL,  -- The search query that led to this result
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, session_id)
);

-- Saved items table (for user bookmarks)
CREATE TABLE saved_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),  -- For guest users
    item_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(20) NOT NULL,  -- 'article' or 'web'
    item_data JSONB NOT NULL,  -- Full item data as JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id),
    UNIQUE(session_id, item_id)
);

-- Indexes for performance
CREATE INDEX idx_articles_language ON articles(language);
CREATE INDEX idx_articles_year ON articles(year);
CREATE INDEX idx_articles_faiss_idx ON articles(faiss_idx);

CREATE INDEX idx_ratings_item_id ON ratings(item_id);
CREATE INDEX idx_ratings_session_id ON ratings(session_id);
CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_created_at ON ratings(created_at);

CREATE INDEX idx_saved_items_user_id ON saved_items(user_id);
CREATE INDEX idx_saved_items_session_id ON saved_items(session_id);
CREATE INDEX idx_saved_items_item_type ON saved_items(item_type);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to auto-update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ratings_updated_at BEFORE UPDATE ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing
-- (You can remove this in production)
INSERT INTO users (username, email, password_hash) VALUES
    ('test_user', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgXqf4.6i');  -- password: 'test123'

COMMENT ON TABLE users IS 'User accounts for authentication';
COMMENT ON TABLE articles IS 'Academic articles metadata (embeddings stored in FAISS)';
COMMENT ON TABLE ratings IS 'User ratings and feedback for articles and web resources';
COMMENT ON TABLE saved_items IS 'User bookmarked/saved items';
