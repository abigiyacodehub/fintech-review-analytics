# Fintech Review Analytics

Customer experience analytics for Ethiopian fintech banking apps. The project
collects Google Play reviews, cleans them, applies sentiment analysis, extracts
keywords for thematic grouping, and generates insight artifacts for product
recommendations.

## Target Banks

The scraping configuration in [scripts/scrape_reviews.py](scripts/scrape_reviews.py)
targets these Android apps:

| Bank | Google Play package |
| --- | --- |
| Commercial Bank of Ethiopia | `com.combanketh.mobilebanking` |
| Bank of Abyssinia | `com.boa.boaMobileBanking` |
| Dashen Bank | `com.dashen.dashensuperapp` |

## Repository Structure

```text
.
├── .github/workflows/unittests.yml
├── data/                  # local-only scraped and processed data
├── notebooks/             # exploratory notebooks
├── scripts/               # runnable scraping, cleaning, analysis scripts
├── src/                   # importable project package
├── tests/                 # unit tests
├── requirements.txt
└── README.md
```

CSV, database, and local environment files are excluded in `.gitignore`; generated
review datasets should be kept under `data/` and should not be committed.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Task 1: Data Collection and Preprocessing

Collect newest available Google Play reviews for the three target banks:

```bash
python scripts/scrape_reviews.py --count 500 --output data/raw/google_play_reviews.csv
```

The scraper stores the rubric-required fields:

- `review_id`
- `review_text`
- `rating`
- `date`
- `bank_name`
- `source`

It also keeps useful context such as `app_id`, `user_name`, `thumbs_up`, and
`app_version`. The date range is the newest review window returned by Google Play
at runtime; because Google Play does not expose a stable date-range filter through
`google-play-scraper`, the exact start date depends on the most recent reviews
available when the command is run.

Clean the raw data:

```bash
python scripts/preprocess_reviews.py \
  --input data/raw/google_play_reviews.csv \
  --output data/processed/clean_reviews.csv
```

Preprocessing performs duplicate removal by `review_id`, drops rows missing
`review_text` or `rating`, removes blank review text, and normalizes dates to
`YYYY-MM-DD`.

Scraping limitations:

- Google Play review availability can vary by region, language, and app.
- Network or parser failures are logged and do not stop collection for other banks.
- CSV outputs are reproducible local artifacts and are intentionally ignored by git.

## Task 2: Sentiment and Thematic Analysis

Run VADER sentiment analysis and TF-IDF keyword extraction:

```bash
python scripts/analyze_sentiment_themes.py \
  --input data/processed/clean_reviews.csv \
  --sentiment-output data/processed/reviews_with_sentiment.csv \
  --themes-output data/processed/tfidf_keywords.csv
```

The sentiment output includes `sentiment_label` and `sentiment_score` columns.
With the recommended `--count 500` scrape setting, the pipeline is designed to
cover up to 1,500 reviews across the three banks, satisfying the rubric threshold
of at least 400 reviews when enough reviews are returned by Google Play.

The thematic analysis output uses TF-IDF via scikit-learn and provides ranked
keywords by `bank_name` and `sentiment_label`, which can be grouped into final
themes such as login/access, transfer reliability, performance, UI/UX, and
customer support.

## Task 4: Insights and Recommendations

After sentiment and TF-IDF outputs exist locally, generate charts and a concise
recommendation report:

```bash
python scripts/generate_insights.py \
  --input data/processed/reviews_with_sentiment.csv \
  --themes data/processed/tfidf_keywords.csv \
  --output-dir reports
```

This creates local charts under `reports/figures/` and a generated
`reports/task_4_insights.md` report summarizing average rating, average sentiment,
negative sentiment share, low-rating share, and priority keywords per bank.

## CI/CD

The GitHub Actions workflow at `.github/workflows/unittests.yml` runs on pushes
and pull requests to `main`. It installs dependencies with:

```bash
pip install -r requirements.txt
```

and then runs:

```bash
pytest
```
