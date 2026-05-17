"""Validate local Task 1 and Task 2 CSV outputs without committing data."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TASK1_COLUMNS = {"review_id", "review_text", "rating", "date", "bank_name", "source"}
TASK2_COLUMNS = TASK1_COLUMNS | {"sentiment_label", "sentiment_score"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated rubric output files.")
    parser.add_argument(
        "--clean-input",
        type=Path,
        default=Path("data/processed/clean_reviews.csv"),
        help="Clean Task 1 output CSV.",
    )
    parser.add_argument(
        "--sentiment-input",
        type=Path,
        default=Path("data/processed/reviews_with_sentiment.csv"),
        help="Task 2 sentiment output CSV.",
    )
    parser.add_argument(
        "--min-reviews",
        type=int,
        default=400,
        help="Minimum review rows expected for Task 2 evidence.",
    )
    return parser.parse_args()


def require_columns(df: pd.DataFrame, required: set[str], label: str) -> None:
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"{label} is missing required columns: {sorted(missing)}")


def validate_outputs(clean_path: Path, sentiment_path: Path, min_reviews: int = 400) -> dict[str, int]:
    if not clean_path.exists():
        raise FileNotFoundError(f"Clean review output not found: {clean_path}")
    if not sentiment_path.exists():
        raise FileNotFoundError(f"Sentiment output not found: {sentiment_path}")

    clean_df = pd.read_csv(clean_path)
    sentiment_df = pd.read_csv(sentiment_path)
    require_columns(clean_df, TASK1_COLUMNS, "Task 1 clean output")
    require_columns(sentiment_df, TASK2_COLUMNS, "Task 2 sentiment output")

    if len(sentiment_df) < min_reviews:
        raise ValueError(
            f"Task 2 sentiment output has {len(sentiment_df)} rows; expected at least {min_reviews}."
        )

    return {"clean_reviews": len(clean_df), "sentiment_reviews": len(sentiment_df)}


def main() -> None:
    args = parse_args()
    counts = validate_outputs(args.clean_input, args.sentiment_input, args.min_reviews)
    print(
        "Validated Task 1/2 outputs: "
        f"{counts['clean_reviews']} clean reviews, "
        f"{counts['sentiment_reviews']} sentiment reviews."
    )


if __name__ == "__main__":
    main()
