# PostgreSQL Database Implementation

## Overview

This document describes the PostgreSQL database implementation for the Fintech Review Analytics project, completing Task 3 of the requirements.

## Schema Design

### Tables

#### banks
Stores metadata about the three Ethiopian banks being analyzed.

```sql
CREATE TABLE banks (
    bank_id SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL UNIQUE,
    app_name VARCHAR(100),
    package_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Records:**
- Commercial Bank of Ethiopia
- Bank of Abyssinia
- Dashen Bank

#### reviews
Stores all scraped and processed reviews from Google Play Store.

```sql
CREATE TABLE reviews (
    review_id VARCHAR(255) PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(bank_id),
    review_text TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
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
```

### Indexes

Performance-optimized indexes on:
- `bank_id` - For bank-specific queries
- `sentiment_label` - For sentiment-based filtering
- `rating` - For rating analysis
- `identified_theme` - For theme-based queries
- `review_date` - For time-series analysis
- `(bank_id, review_date)` - For combined queries

## Setup Instructions

### 1. Install PostgreSQL

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### 2. Create Database

```bash
createdb fintech_reviews
```

### 3. Initialize Schema

```bash
psql fintech_reviews < database/schema.sql
```

### 4. Load Data

```bash
# Install dependencies
pip install -r requirements.txt

# Load reviews from CSV
python scripts/load_to_postgres.py data/processed_reviews.csv database/schema.sql
```

### 5. Verify Setup

```bash
python scripts/verify_database.py
```

## Usage Examples

### Connect to Database

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
```

### Query Examples

#### Count reviews per bank

```python
cursor = conn.cursor()
cursor.execute("""
    SELECT b.bank_name, COUNT(r.review_id) as count
    FROM banks b
    LEFT JOIN reviews r ON b.bank_id = r.bank_id
    GROUP BY b.bank_id, b.bank_name
    ORDER BY count DESC
""")
for bank, count in cursor.fetchall():
    print(f"{bank}: {count} reviews")
```

#### Average rating by bank

```python
cursor.execute("""
    SELECT b.bank_name, ROUND(AVG(r.rating)::NUMERIC, 2) as avg_rating
    FROM banks b
    JOIN reviews r ON b.bank_id = r.bank_id
    GROUP BY b.bank_id, b.bank_name
""")
for bank, rating in cursor.fetchall():
    print(f"{bank}: {rating}★")
```

#### Sentiment distribution

```python
cursor.execute("""
    SELECT sentiment_label, COUNT(*) as count
    FROM reviews
    GROUP BY sentiment_label
    ORDER BY count DESC
""")
for sentiment, count in cursor.fetchall():
    print(f"{sentiment}: {count}")
```

#### Most common themes

```python
cursor.execute("""
    SELECT identified_theme, COUNT(*) as count
    FROM reviews
    WHERE identified_theme IS NOT NULL
    GROUP BY identified_theme
    ORDER BY count DESC
    LIMIT 10
""")
for theme, count in cursor.fetchall():
    print(f"{theme}: {count}")
```

#### Reviews by rating and sentiment

```python
cursor.execute("""
    SELECT b.bank_name, r.rating, r.sentiment_label, COUNT(*) as count
    FROM reviews r
    JOIN banks b ON r.bank_id = b.bank_id
    GROUP BY b.bank_id, b.bank_name, r.rating, r.sentiment_label
    ORDER BY b.bank_name, r.rating DESC, r.sentiment_label
""")
```

## Data Load Script

The `scripts/load_to_postgres.py` script:
1. Connects to PostgreSQL using environment variables
2. Initializes schema from `database/schema.sql`
3. Reads processed reviews from CSV
4. Maps bank names to bank IDs
5. Inserts reviews in batches (100 per batch)
6. Handles duplicates (ON CONFLICT DO NOTHING)
7. Provides detailed logging

## Verification Script

The `scripts/verify_database.py` script:
1. Connects to database
2. Lists all tables
3. Counts records in each table
4. Shows distribution by:
   - Bank
   - Rating
   - Sentiment
   - Theme
5. Checks data quality (null values)
6. Shows date range
7. Displays sample reviews

## Environment Configuration

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Then fill in your values:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fintech_reviews
DB_USER=postgres
DB_PASSWORD=your_password
```

## Backup and Restore

### Backup

```bash
pg_dump fintech_reviews > backup.sql
```

### Restore

```bash
psql fintech_reviews < backup.sql
```

## Performance Notes

- Indexes significantly speed up queries on common filter columns
- The `ON CONFLICT DO NOTHING` clause prevents duplicate insertions
- Foreign key constraints maintain data integrity
- The schema supports batch queries efficiently

## Troubleshooting

### Connection refused
- Ensure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Check DB_HOST and DB_PORT in `.env`

### Table doesn't exist
- Run schema initialization: `psql fintech_reviews < database/schema.sql`

### Permission denied
- Check DB_USER has correct permissions
- Grant permissions: `ALTER ROLE db_user WITH CREATEDB;`

### Duplicate key error
- Data already loaded; use `ON CONFLICT DO NOTHING` to skip duplicates

## Next Steps

1. Load production data using `scripts/load_to_postgres.py`
2. Verify data using `scripts/verify_database.py`
3. Run queries for analytics and visualization
4. Set up automated backups
5. Monitor database performance
