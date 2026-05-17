"""Generate Task 4 visual summaries and recommendation inputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create charts and a concise insights report.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/reviews_with_sentiment.csv"),
        help="Sentiment-enriched reviews CSV.",
    )
    parser.add_argument(
        "--themes",
        type=Path,
        default=Path("data/processed/tfidf_keywords.csv"),
        help="TF-IDF keyword CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports"),
        help="Directory for charts and markdown report.",
    )
    return parser.parse_args()


def save_rating_chart(df: pd.DataFrame, figure_dir: Path) -> Path:
    path = figure_dir / "average_rating_by_bank.png"
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x="bank_name", y="rating", errorbar=None)
    plt.title("Average App Rating by Bank")
    plt.xlabel("")
    plt.ylabel("Average rating")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return path


def save_sentiment_chart(df: pd.DataFrame, figure_dir: Path) -> Path:
    path = figure_dir / "sentiment_distribution_by_bank.png"
    counts = df.groupby(["bank_name", "sentiment_label"]).size().reset_index(name="reviews")
    plt.figure(figsize=(9, 5))
    sns.barplot(data=counts, x="bank_name", y="reviews", hue="sentiment_label")
    plt.title("Sentiment Distribution by Bank")
    plt.xlabel("")
    plt.ylabel("Review count")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return path


def build_recommendations(df: pd.DataFrame, themes: pd.DataFrame) -> list[str]:
    recommendations: list[str] = []
    for bank_name, group in df.groupby("bank_name"):
        negative_share = (group["sentiment_label"] == "negative").mean()
        low_rating_share = (group["rating"] <= 2).mean()
        keywords = themes[
            (themes["bank_name"] == bank_name) & (themes["sentiment_label"] == "negative")
        ]["keyword"].head(5)
        keyword_text = ", ".join(keywords) if not keywords.empty else "no dominant negative keywords"
        recommendations.append(
            f"- {bank_name}: prioritize fixes tied to {keyword_text}. "
            f"Negative sentiment share is {negative_share:.1%}; low-rating share is {low_rating_share:.1%}."
        )
    return recommendations


def write_report(df: pd.DataFrame, themes: pd.DataFrame, output_dir: Path, charts: list[Path]) -> Path:
    report_path = output_dir / "task_4_insights.md"
    bank_summary = (
        df.groupby("bank_name")
        .agg(
            reviews=("review_id", "count"),
            average_rating=("rating", "mean"),
            average_sentiment=("sentiment_score", "mean"),
        )
        .round(3)
        .reset_index()
    )

    lines = [
        "# Task 4: Insights and Recommendations",
        "",
        "This report is generated from the sentiment-enriched review dataset.",
        "",
        "## Summary by bank",
        "",
        bank_summary.to_markdown(index=False),
        "",
        "## Charts",
        "",
    ]
    lines.extend(f"- {chart.as_posix()}" for chart in charts)
    lines.extend(["", "## Recommended actions", ""])
    lines.extend(build_recommendations(df, themes))
    lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input)
    themes = pd.read_csv(args.themes)
    figure_dir = args.output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    charts = [save_rating_chart(df, figure_dir), save_sentiment_chart(df, figure_dir)]
    report_path = write_report(df, themes, args.output_dir, charts)
    print(f"Wrote insights report to {report_path}")


if __name__ == "__main__":
    main()
