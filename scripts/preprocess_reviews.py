"""Clean raw Google Play review data for analysis."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {"review_id", "review_text", "rating", "date", "bank_name", "source"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess scraped review CSV data.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/google_play_reviews.csv"),
        help="Raw review CSV path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/clean_reviews.csv"),
        help="Clean review CSV path.",
    )
    return parser.parse_args()


def validate_columns(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Input data is missing required columns: {sorted(missing)}")


def preprocess_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate IDs, drop unusable records, and normalize dates."""
    validate_columns(df)
    cleaned = df.copy()

    cleaned["review_text"] = cleaned["review_text"].astype("string").str.strip()
    cleaned["rating"] = pd.to_numeric(cleaned["rating"], errors="coerce")
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    before = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["review_id"], keep="first")
    cleaned = cleaned.dropna(subset=["review_text", "rating"])
    cleaned = cleaned[cleaned["review_text"] != ""]
    cleaned = cleaned.dropna(subset=["date"])
    cleaned["rating"] = cleaned["rating"].astype(int)

    logging.info("Cleaned reviews: %s -> %s rows", before, len(cleaned))
    return cleaned.reset_index(drop=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    raw = pd.read_csv(args.input)
    cleaned = preprocess_reviews(raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(args.output, index=False)
    logging.info("Wrote cleaned data to %s", args.output)


if __name__ == "__main__":
    main()
