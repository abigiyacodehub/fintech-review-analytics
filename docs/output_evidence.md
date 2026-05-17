# Output Evidence

The repository intentionally excludes generated data files with `.gitignore`.
Run the commands below to reproduce the Task 1 and Task 2 outputs locally:

```bash
python scripts/scrape_reviews.py --count 500 --output data/raw/google_play_reviews.csv
python scripts/preprocess_reviews.py --input data/raw/google_play_reviews.csv --output data/processed/clean_reviews.csv
python scripts/analyze_sentiment_themes.py --input data/processed/clean_reviews.csv --sentiment-output data/processed/reviews_with_sentiment.csv --themes-output data/processed/tfidf_keywords.csv
```

Expected `data/processed/reviews_with_sentiment.csv` columns include:

- `review_id`
- `review_text`
- `rating`
- `date`
- `bank_name`
- `source`
- `sentiment_label`
- `sentiment_score`

The configured scrape count requests 500 reviews per bank across CBE, BOA, and
Dashen Bank, so the documented analysis output is intended to cover at least 400
reviews when Google Play returns sufficient review volume.
