"""Add sentiment labels/scores and extract TF-IDF keywords from reviews."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
from nltk import download
from nltk.data import find
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sentiment and thematic analysis.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/clean_reviews.csv"),
        help="Clean review CSV path.",
    )
    parser.add_argument(
        "--sentiment-output",
        type=Path,
        default=Path("data/processed/reviews_with_sentiment.csv"),
        help="CSV with sentiment_label and sentiment_score columns.",
    )
    parser.add_argument(
        "--themes-output",
        type=Path,
        default=Path("data/processed/tfidf_keywords.csv"),
        help="CSV containing TF-IDF keyword evidence for theme grouping.",
    )
    parser.add_argument("--top-n", type=int, default=20, help="Top keywords per bank/sentiment group.")
    return parser.parse_args()


def get_vader_analyzer() -> SentimentIntensityAnalyzer:
    try:
        find("sentiment/vader_lexicon.zip")
    except LookupError:
        download("vader_lexicon", quiet=True)
    return SentimentIntensityAnalyzer()


def label_from_score(score: float) -> str:
    if score >= 0.05:
        return "positive"
    if score <= -0.05:
        return "negative"
    return "neutral"


def add_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    if "review_text" not in df.columns:
        raise ValueError("Input data must include a review_text column.")

    analyzer = get_vader_analyzer()
    analyzed = df.copy()
    analyzed["sentiment_score"] = analyzed["review_text"].fillna("").map(
        lambda text: analyzer.polarity_scores(str(text))["compound"]
    )
    analyzed["sentiment_label"] = analyzed["sentiment_score"].map(label_from_score)
    return analyzed


def extract_tfidf_keywords(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    required = {"bank_name", "sentiment_label", "review_text"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input data is missing required columns: {sorted(missing)}")

    keyword_rows: list[dict[str, object]] = []
    grouped = df.groupby(["bank_name", "sentiment_label"], dropna=False)

    for (bank_name, sentiment_label), group in grouped:
        texts = group["review_text"].dropna().astype(str)
        if texts.empty:
            continue

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_features=1000,
        )
        matrix = vectorizer.fit_transform(texts)
        scores = matrix.mean(axis=0).A1
        terms = vectorizer.get_feature_names_out()
        top_indices = scores.argsort()[::-1][:top_n]

        for rank, idx in enumerate(top_indices, start=1):
            keyword_rows.append(
                {
                    "bank_name": bank_name,
                    "sentiment_label": sentiment_label,
                    "keyword": terms[idx],
                    "tfidf_score": round(float(scores[idx]), 6),
                    "rank": rank,
                    "review_count": len(texts),
                }
            )

    return pd.DataFrame(keyword_rows)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    clean_reviews = pd.read_csv(args.input)
    analyzed = add_sentiment(clean_reviews)
    themes = extract_tfidf_keywords(analyzed, args.top_n)

    args.sentiment_output.parent.mkdir(parents=True, exist_ok=True)
    analyzed.to_csv(args.sentiment_output, index=False)
    themes.to_csv(args.themes_output, index=False)
    logging.info(
        "Wrote %s sentiment rows and %s keyword rows.",
        len(analyzed),
        len(themes),
    )


if __name__ == "__main__":
    main()
