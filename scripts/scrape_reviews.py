"""Collect Google Play reviews for Ethiopian banking apps.

The script writes raw review data to data/raw/google_play_reviews.csv by default.
CSV outputs are ignored by git so the repository keeps reproducible code without
committing scraped data.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from time import sleep
from typing import Any

import pandas as pd
from google_play_scraper import Sort, reviews


SOURCE = "Google Play"
BANK_APPS = {
    "Commercial Bank of Ethiopia": "com.combanketh.mobilebanking",
    "Bank of Abyssinia": "com.boa.boaMobileBanking",
    "Dashen Bank": "com.dashen.dashensuperapp",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Google Play reviews for target banks.")
    parser.add_argument("--count", type=int, default=500, help="Reviews to request per bank.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/google_play_reviews.csv"),
        help="Destination CSV path.",
    )
    parser.add_argument("--lang", default="en", help="Review language passed to google-play-scraper.")
    parser.add_argument("--country", default="et", help="Country passed to google-play-scraper.")
    parser.add_argument("--sleep", type=float, default=1.0, help="Pause between app requests.")
    return parser.parse_args()


def normalize_review(raw_review: dict[str, Any], bank_name: str, app_id: str) -> dict[str, Any]:
    """Map google-play-scraper output to the rubric-required schema."""
    return {
        "review_id": raw_review.get("reviewId"),
        "review_text": raw_review.get("content"),
        "rating": raw_review.get("score"),
        "date": raw_review.get("at"),
        "bank_name": bank_name,
        "source": SOURCE,
        "app_id": app_id,
        "user_name": raw_review.get("userName"),
        "thumbs_up": raw_review.get("thumbsUpCount"),
        "app_version": raw_review.get("reviewCreatedVersion"),
    }


def collect_bank_reviews(
    bank_name: str,
    app_id: str,
    count: int,
    lang: str,
    country: str,
) -> list[dict[str, Any]]:
    try:
        batch, _ = reviews(
            app_id,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=count,
        )
    except Exception as exc:  # google-play-scraper raises broad network/parser errors.
        logging.exception("Failed to scrape %s (%s): %s", bank_name, app_id, exc)
        return []

    return [normalize_review(item, bank_name, app_id) for item in batch]


def scrape_reviews(
    count: int = 500,
    lang: str = "en",
    country: str = "et",
    pause_seconds: float = 1.0,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for bank_name, app_id in BANK_APPS.items():
        logging.info("Scraping %s from %s", bank_name, app_id)
        rows.extend(collect_bank_reviews(bank_name, app_id, count, lang, country))
        sleep(pause_seconds)

    columns = [
        "review_id",
        "review_text",
        "rating",
        "date",
        "bank_name",
        "source",
        "app_id",
        "user_name",
        "thumbs_up",
        "app_version",
    ]
    return pd.DataFrame(rows, columns=columns)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    df = scrape_reviews(args.count, args.lang, args.country, args.sleep)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    logging.info("Wrote %s reviews to %s", len(df), args.output)


if __name__ == "__main__":
    main()
