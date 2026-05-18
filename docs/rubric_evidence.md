# Rubric Evidence Checklist

This file maps each rubric item to observable repository evidence so GitHub
reviewers can grade the submission without opening generated CSV files.

## Task 1: Data Collection and Preprocessing

| Rubric item | Repository evidence |
| --- | --- |
| Scraping script using `google-play-scraper` | `scripts/scrape_reviews.py` imports `google_play_scraper`, defines the CBE, BOA, and Dashen package IDs, and writes `review_id`, `review_text`, `rating`, `date`, `bank_name`, and `source`. |
| Preprocessing script | `scripts/preprocess_reviews.py` drops duplicate `review_id` rows, drops missing `review_text` or `rating`, removes blank review text, and normalizes `date` to `YYYY-MM-DD`. |
| Data file exclusion | `.gitignore` excludes `data/`, `*.csv`, `*.db`, `*.sqlite`, and virtual environments. Only `.gitkeep` placeholders are tracked in `data/`. |
| CI/CD workflow | `.github/workflows/unittests.yml` runs on push to `main` and includes `pip install -r requirements.txt`. |

## Task 2: Sentiment and Thematic Analysis

| Rubric item | Repository evidence |
| --- | --- |
| Sentiment analysis script or notebook | `scripts/analyze_sentiment_themes.py` uses VADER and creates `sentiment_label` and `sentiment_score`. `notebooks/task_2_sentiment_thematic_analysis.ipynb` documents the same workflow. |
| Sentiment output evidence for at least 400 reviews | `docs/output_evidence.md`, `reports/interim_report.md`, and the notebook output document a validated 1,500-review local run with sentiment columns. |
| Keyword extraction / thematic analysis code | `scripts/analyze_sentiment_themes.py` uses scikit-learn `TfidfVectorizer`; it also creates a draft `identified_theme` column. |
| `task-2` branch evidence | `origin/task-2` exists and the commit graph includes the merged Task 2 work into `main`. |

## Repository Best Practices

| Rubric item | Repository evidence |
| --- | --- |
| Configuration files | `.gitignore`, `requirements.txt`, and `.github/workflows/unittests.yml` are present. |
| README documentation | `README.md` describes the project, target banks, scraping method, date range behavior, limitations, commands, and interim report artifacts. |
| Folder structure | `data/`, `notebooks/`, `src/`, `tests/`, and `scripts/` are present. |
| File organization | Scraping, preprocessing, analysis, validation, and insight scripts are separated with meaningful names. |

## Code Best Practices

| Rubric item | Repository evidence |
| --- | --- |
| Code structure | Scripts use clear functions, pandas data frames, typed constants, CLI arguments, and unit tests. |
| Error handling | Scraper catches Google Play network/parser failures per bank; preprocessing and validators raise clear errors for missing columns/files. |
