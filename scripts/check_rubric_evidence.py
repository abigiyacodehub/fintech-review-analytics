"""Fail fast if repository-visible rubric evidence is missing."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    scrape = read_text("scripts/scrape_reviews.py")
    preprocess = read_text("scripts/preprocess_reviews.py")
    analysis = read_text("scripts/analyze_sentiment_themes.py")
    gitignore = read_text(".gitignore")
    workflow = read_text(".github/workflows/unittests.yml")
    requirements = read_text("requirements.txt")

    for expected in ["google_play_scraper", "review_text", "rating", "date", "bank_name", "source"]:
        require(expected in scrape, f"Scraper evidence missing {expected}")
    for expected in ["Commercial Bank of Ethiopia", "Bank of Abyssinia", "Dashen Bank"]:
        require(expected in scrape, f"Scraper target missing {expected}")

    for expected in ["drop_duplicates", "review_id", "dropna", "%Y-%m-%d"]:
        require(expected in preprocess, f"Preprocessing evidence missing {expected}")

    for expected in ["data/", "*.csv", "*.db", ".venv/"]:
        require(expected in gitignore, f".gitignore evidence missing {expected}")

    require("pip install -r requirements.txt" in workflow, "CI install command is missing")
    require("branches:" in workflow and "main" in workflow, "CI is not configured for main")

    for expected in ["google-play-scraper", "pandas", "scikit-learn", "nltk", "pytest"]:
        require(expected in requirements, f"requirements.txt missing {expected}")

    for expected in ["SentimentIntensityAnalyzer", "sentiment_label", "sentiment_score", "TfidfVectorizer"]:
        require(expected in analysis, f"Task 2 analysis evidence missing {expected}")

    require((ROOT / "notebooks/task_2_sentiment_thematic_analysis.ipynb").exists(), "Task 2 notebook is missing")
    require((ROOT / "docs/rubric_evidence.md").exists(), "Rubric evidence checklist is missing")
    print("Repository rubric evidence check passed.")


if __name__ == "__main__":
    main()
