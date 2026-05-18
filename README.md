# Fintech Review Analytics

This project turns Google Play reviews for three Ethiopian mobile banking apps
into a practical customer-experience readout. The workflow collects reviews,
cleans the data, assigns sentiment, extracts recurring keywords, and packages
the findings so a product team can see what customers appreciate and where they
are getting stuck.

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
|-- .github/workflows/unittests.yml
|-- data/
|   |-- raw/               # local-only scraped data
|   `-- processed/         # local-only cleaned/analyzed data
|-- docs/                  # reproducibility and output evidence
|-- notebooks/             # exploratory notebooks
|-- scripts/               # runnable scraping, cleaning, analysis scripts
|-- src/                   # importable project package
|-- tests/                 # unit tests
|-- requirements.txt
`-- README.md
```

CSV, database, and local environment files are excluded in `.gitignore`. The
data can be regenerated locally, but raw review files are not committed.

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

The scraper stores the fields needed for the assignment:

- `review_id`
- `review_text`
- `rating`
- `date`
- `bank_name`
- `source`

It also keeps useful context such as `app_id`, `user_name`, `thumbs_up`, and
`app_version`. The date range is the newest review window returned by Google
Play at runtime. Because `google-play-scraper` does not expose a stable date
filter, the exact start date can shift when the data is regenerated.

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
It also includes a draft `identified_theme` column to make early theme grouping
visible. With the recommended `--count 500` scrape setting, the pipeline can
cover up to 1,500 reviews across the three banks, which is comfortably above the
400-review threshold when Google Play returns enough reviews.

Validate the generated local outputs for the rubric-required columns and minimum
Task 2 row count:

```bash
python scripts/validate_task_outputs.py \
  --clean-input data/processed/clean_reviews.csv \
  --sentiment-input data/processed/reviews_with_sentiment.csv \
  --min-reviews 400
```

The thematic analysis output uses TF-IDF via scikit-learn and provides ranked
keywords by `bank_name` and `sentiment_label`, which can be grouped into final
themes such as login/access, transfer reliability, performance, UI/UX, and
customer support.

## Interim Due-Date Submission

The PDF's interim submission asks for the GitHub `main` branch plus a short
report covering scraping methodology, data quality, early sentiment findings,
at least one visualization, blockers, and the final-submission plan.

Submission-ready interim artifacts are in `reports/`:

- `reports/interim_report.md`
- `reports/interim_report.pdf`
- `reports/interim_sentiment_distribution.png`

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
