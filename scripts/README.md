# Scripts

Runnable project scripts are separated by pipeline stage:

- `scrape_reviews.py`: collects Google Play reviews for CBE, BOA, and Dashen.
- `preprocess_reviews.py`: removes duplicates, handles missing values, and normalizes dates.
- `analyze_sentiment_themes.py`: adds VADER sentiment and keyword-based theme labels, then extracts TF-IDF keywords.
- `validate_task_outputs.py`: checks local Task 1 and Task 2 output evidence without committing CSV files.
- `generate_insights.py`: creates later-stage charts and recommendation summaries.
