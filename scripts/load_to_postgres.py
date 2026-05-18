"""Load processed reviews into PostgreSQL database."""

import logging
import os
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_to_postgres(csv_file: str, schema_file: str = None):
    """
    Load reviews CSV into PostgreSQL database.
    
    Args:
        csv_file: Path to processed reviews CSV
        schema_file: Optional path to schema.sql for initialization
    """
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "fintech_reviews")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    try:
        # Connect to PostgreSQL
        logger.info(f"Connecting to PostgreSQL: {db_host}:{db_port}/{db_name}")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Initialize schema if provided
        if schema_file and os.path.exists(schema_file):
            logger.info("Initializing database schema...")
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            cursor.execute(schema_sql)
            conn.commit()
            logger.info("Schema initialized successfully")
        
        # Read CSV file
        logger.info(f"Reading reviews from {csv_file}")
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} reviews")
        
        # Map bank names to IDs
        bank_query = "SELECT bank_id, bank_name FROM banks"
        cursor.execute(bank_query)
        bank_map = {name: bid for bid, name in cursor.fetchall()}
        
        # Prepare data for insertion
        insert_query = """
            INSERT INTO reviews (
                review_id, bank_id, review_text, rating, review_date,
                sentiment_label, sentiment_score, identified_theme,
                source, user_name, thumbs_up, app_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (review_id) DO NOTHING
        """
        
        # Prepare batch data
        batch_data = []
        for _, row in df.iterrows():
            bank_name = row.get('bank_name', row.get('Bank', ''))
            bank_id = bank_map.get(bank_name)
            
            if not bank_id:
                logger.warning(f"Unknown bank: {bank_name}, skipping review")
                continue
            
            batch_data.append((
                str(row.get('review_id', '')),
                bank_id,
                str(row.get('review_text', row.get('Review', ''))),
                int(row.get('rating', row.get('Rating', 0))),
                pd.to_datetime(row.get('review_date', row.get('Date', None)), errors='coerce').date() if pd.notna(row.get('review_date', row.get('Date', None))) else None,
                str(row.get('sentiment_label', row.get('Sentiment', ''))).lower(),
                float(row.get('sentiment_score', row.get('Sentiment Score', 0))),
                str(row.get('identified_theme', row.get('Theme', ''))).lower() if pd.notna(row.get('identified_theme', row.get('Theme', None))) else None,
                'Google Play',
                str(row.get('user_name', row.get('User', ''))),
                int(row.get('thumbs_up', row.get('Thumbs Up', 0))),
                str(row.get('app_version', row.get('Version', '')))
            ))
        
        # Insert in batches
        logger.info(f"Inserting {len(batch_data)} reviews...")
        execute_batch(cursor, insert_query, batch_data, page_size=100)
        conn.commit()
        logger.info(f"Successfully inserted {len(batch_data)} reviews")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM reviews")
        count = cursor.fetchone()[0]
        logger.info(f"Total reviews in database: {count}")
        
        cursor.close()
        conn.close()
        logger.info("Database connection closed")
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_to_postgres.py <csv_file> [schema_file]")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    schema_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    load_to_postgres(csv_file, schema_file)
