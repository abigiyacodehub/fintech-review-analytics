# Task 1 and Task 2 Output Evidence

The repository intentionally excludes generated data files with `.gitignore`.
Run the commands below to reproduce the Task 1 and Task 2 outputs locally:

```bash
python scripts/scrape_reviews.py --count 500 --output data/raw/google_play_reviews.csv
python scripts/preprocess_reviews.py --input data/raw/google_play_reviews.csv --output data/processed/clean_reviews.csv
python scripts/analyze_sentiment_themes.py --input data/processed/clean_reviews.csv --sentiment-output data/processed/reviews_with_sentiment.csv --themes-output data/processed/tfidf_keywords.csv
python scripts/validate_task_outputs.py --clean-input data/processed/clean_reviews.csv --sentiment-input data/processed/reviews_with_sentiment.csv --min-reviews 400
```

The validation command confirms that generated local CSV outputs include the
rubric-required fields while keeping those reproducible data files out of git.

Latest local validation evidence for the interim submission:

- Run date: 2026-05-18.
- Raw reviews collected: 1,500.
- Clean reviews after preprocessing: 1,500.
- Reviews with sentiment output: 1,500.
- Bank coverage: 500 reviews each for Commercial Bank of Ethiopia, Bank of Abyssinia, and Dashen Bank.
- Missing `review_text` after preprocessing: 0.
- Missing `rating` after preprocessing: 0.

Expected `data/processed/clean_reviews.csv` Task 1 columns include:

- `review_id`
- `review_text`
- `rating`
- `date`
- `bank_name`
- `source`

Expected `data/processed/reviews_with_sentiment.csv` Task 2 columns include all
Task 1 columns plus:

- `sentiment_label`
- `sentiment_score`
- `identified_theme`

The configured scrape count requests 500 reviews per bank across CBE, BOA, and
Dashen Bank, for up to 1,500 raw reviews. The validator fails unless
`reviews_with_sentiment.csv` contains at least 400 rows, which provides the
documented output evidence required by the Task 2 rubric without committing CSV
data.
