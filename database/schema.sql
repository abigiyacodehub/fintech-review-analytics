-- ============================================================================
-- Fintech Review Analytics: PostgreSQL Schema
-- Ethiopian Banks Mobile App Review Analysis
-- ============================================================================

-- Drop existing tables if needed (caution: removes data)
-- DROP TABLE IF EXISTS reviews CASCADE;
-- DROP TABLE IF EXISTS banks CASCADE;

-- ============================================================================
-- BANKS TABLE: Metadata about the three Ethiopian banks
-- ============================================================================
CREATE TABLE IF NOT EXISTS banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_name VARCHAR(100),
    package_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add initial bank records
INSERT INTO banks (bank_name, app_name, package_id) VALUES
    ('Commercial Bank of Ethiopia', 'CBE Mobile Banking', 'com.combanketh.mobilebanking'),
    ('Bank of Abyssinia', 'BOA Mobile Banking', 'com.boa.boaMobileBanking'),
    ('Dashen Bank', 'Dashen SuperApp', 'com.dashen.dashensuperapp')
ON CONFLICT (bank_name) DO NOTHING;

-- ============================================================================
-- REVIEWS TABLE: Scraped and processed Google Play reviews
-- ============================================================================
CREATE TABLE IF NOT EXISTS reviews (
    review_id VARCHAR(255) PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id) ON DELETE CASCADE,
    review_text TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_date DATE,
    sentiment_label VARCHAR(20),
    sentiment_score FLOAT CHECK (sentiment_score >= -1.0 AND sentiment_score <= 1.0),
    identified_theme VARCHAR(100),
    source VARCHAR(50) DEFAULT 'Google Play',
    user_name VARCHAR(255),
    thumbs_up INTEGER DEFAULT 0,
    app_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES: Optimize query performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_reviews_bank_id 
    ON reviews(bank_id);

CREATE INDEX IF NOT EXISTS idx_reviews_sentiment 
    ON reviews(sentiment_label);

CREATE INDEX IF NOT EXISTS idx_reviews_rating 
    ON reviews(rating);

CREATE INDEX IF NOT EXISTS idx_reviews_theme 
    ON reviews(identified_theme);

CREATE INDEX IF NOT EXISTS idx_reviews_date 
    ON reviews(review_date);

CREATE INDEX IF NOT EXISTS idx_reviews_bank_date 
    ON reviews(bank_id, review_date);

-- ============================================================================
-- VERIFICATION: Useful queries for data quality checks
-- ============================================================================

-- Query 1: Count reviews per bank
-- SELECT b.bank_name, COUNT(r.review_id) as review_count
-- FROM banks b LEFT JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_id, b.bank_name;

-- Query 2: Average rating by bank
-- SELECT b.bank_name, ROUND(AVG(r.rating)::NUMERIC, 2) as avg_rating
-- FROM banks b JOIN reviews r ON b.bank_id = r.bank_id
-- GROUP BY b.bank_id, b.bank_name;

-- Query 3: Sentiment distribution
-- SELECT sentiment_label, COUNT(*) as count
-- FROM reviews
-- GROUP BY sentiment_label;

-- Query 4: Most common themes
-- SELECT identified_theme, COUNT(*) as count
-- FROM reviews
-- WHERE identified_theme IS NOT NULL
-- GROUP BY identified_theme
-- ORDER BY count DESC;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
