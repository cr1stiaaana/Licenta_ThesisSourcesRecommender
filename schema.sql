-- PostgreSQL Schema for Thesis Sources Recommender

DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS saved_items CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS articles CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE articles (
    id VARCHAR(64) PRIMARY KEY,
    title TEXT NOT NULL,
    abstract TEXT,
    authors TEXT,
    year INTEGER,
    doi VARCHAR(255),
    url TEXT,
    keywords TEXT,
    language VARCHAR(10),
    faiss_idx INTEGER
);

CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    item_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    user_id INTEGER REFERENCES users(id),
    query TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, session_id)
);

CREATE TABLE saved_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    item_id VARCHAR(255) NOT NULL,
    item_type VARCHAR(20) NOT NULL,
    item_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ratings_item_id ON ratings(item_id);
CREATE INDEX idx_saved_items_user_id ON saved_items(user_id);
