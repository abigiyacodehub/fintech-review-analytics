"""Verify PostgreSQL database setup and data integrity."""

import logging
import os

import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_database():
    """Verify database schema and data integrity."""
    from dotenv import load_dotenv
    load_dotenv()
    
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "fintech_reviews")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        logger.info("=" * 70)
        logger.info("DATABASE VERIFICATION REPORT")
        logger.info("=" * 70)
        
        # 1. Check tables exist
        logger.info("\n1. CHECKING TABLES...")
        cursor.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        logger.info(f"Found tables: {', '.join(tables)}")
        
        # 2. Check banks table
        logger.info("\n2. BANKS TABLE:")
        cursor.execute("SELECT COUNT(*) FROM banks")
        bank_count = cursor.fetchone()[0]
        logger.info(f"Total banks: {bank_count}")
        
        cursor.execute("SELECT bank_id, bank_name, app_name FROM banks ORDER BY bank_id")
        for bank_id, bank_name, app_name in cursor.fetchall():
            logger.info(f"  - [{bank_id}] {bank_name} ({app_name})")
        
        # 3. Check reviews table
        logger.info("\n3. REVIEWS TABLE:")
        cursor.execute("SELECT COUNT(*) FROM reviews")
        review_count = cursor.fetchone()[0]
        logger.info(f"Total reviews: {review_count}")
        
        # 4. Reviews by bank
        logger.info("\n4. REVIEWS BY BANK:")
        cursor.execute("""
            SELECT b.bank_name, COUNT(r.review_id) as count
            FROM banks b LEFT JOIN reviews r ON b.bank_id = r.bank_id
            GROUP BY b.bank_id, b.bank_name
            ORDER BY count DESC
        """)
        for bank_name, count in cursor.fetchall():
            logger.info(f"  - {bank_name}: {count} reviews")
        
        # 5. Rating distribution
        logger.info("\n5. RATING DISTRIBUTION:")
        cursor.execute("""
            SELECT rating, COUNT(*) as count
            FROM reviews
            WHERE rating IS NOT NULL
            GROUP BY rating
            ORDER BY rating
        """)
        for rating, count in cursor.fetchall():
            logger.info(f"  - {rating} stars: {count} reviews")
        
        # 6. Sentiment distribution
        logger.info("\n6. SENTIMENT DISTRIBUTION:")
        cursor.execute("""
            SELECT sentiment_label, COUNT(*) as count
            FROM reviews
            WHERE sentiment_label IS NOT NULL
            GROUP BY sentiment_label
            ORDER BY count DESC
        """)
        for sentiment, count in cursor.fetchall():
            logger.info(f"  - {sentiment}: {count} reviews")
        
        # 7. Theme distribution
        logger.info("\n7. THEME DISTRIBUTION:")
        cursor.execute("""
            SELECT identified_theme, COUNT(*) as count
            FROM reviews
            WHERE identified_theme IS NOT NULL
            GROUP BY identified_theme
            ORDER BY count DESC
            LIMIT 10
        """)
        for theme, count in cursor.fetchall():
            logger.info(f"  - {theme}: {count} reviews")
        
        # 8. Data quality checks
        logger.info("\n8. DATA QUALITY CHECKS:")
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE review_text IS NULL")
        null_text = cursor.fetchone()[0]
        logger.info(f"  - Null review texts: {null_text}")
        
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE sentiment_label IS NULL")
        null_sentiment = cursor.fetchone()[0]
        logger.info(f"  - Null sentiment labels: {null_sentiment}")
        
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE identified_theme IS NULL")
        null_theme = cursor.fetchone()[0]
        logger.info(f"  - Null themes: {null_theme}")
        
        # 9. Date range
        logger.info("\n9. DATE RANGE:")
        cursor.execute("""
            SELECT MIN(review_date), MAX(review_date)
            FROM reviews WHERE review_date IS NOT NULL
        """)
        min_date, max_date = cursor.fetchone()
        logger.info(f"  - From: {min_date}")
        logger.info(f"  - To: {max_date}")
        
        # 10. Sample reviews
        logger.info("\n10. SAMPLE REVIEWS (First 3):")
        cursor.execute("""
            SELECT b.bank_name, r.rating, r.sentiment_label, r.review_text
            FROM reviews r
            JOIN banks b ON r.bank_id = b.bank_id
            LIMIT 3
        """)
        for bank_name, rating, sentiment, text in cursor.fetchall():
            text_preview = text[:80] + "..." if len(text) > 80 else text
            logger.info(f"  - [{bank_name}] {rating}★ ({sentiment}): {text_preview}")
        
        logger.info("\n" + "=" * 70)
        logger.info("VERIFICATION COMPLETE")
        logger.info("=" * 70)
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    verify_database()
