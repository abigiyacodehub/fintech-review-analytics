import pandas as pd

from scripts.validate_task_outputs import validate_outputs


def test_validate_outputs_accepts_required_columns_and_minimum_rows(tmp_path):
    clean_path = tmp_path / "clean_reviews.csv"
    sentiment_path = tmp_path / "reviews_with_sentiment.csv"
    rows = [
        {
            "review_id": f"r{i}",
            "review_text": "fast and reliable",
            "rating": 5,
            "date": "2026-05-17",
            "bank_name": "Dashen Bank",
            "source": "Google Play",
            "sentiment_label": "positive",
            "sentiment_score": 0.8,
            "identified_theme": "Transaction Performance",
        }
        for i in range(3)
    ]
    sentiment_df = pd.DataFrame(rows)
    sentiment_df.drop(columns=["sentiment_label", "sentiment_score"]).to_csv(clean_path, index=False)
    sentiment_df.to_csv(sentiment_path, index=False)

    counts = validate_outputs(clean_path, sentiment_path, min_reviews=3)

    assert counts == {"clean_reviews": 3, "sentiment_reviews": 3}


def test_validate_outputs_rejects_short_sentiment_file(tmp_path):
    clean_path = tmp_path / "clean_reviews.csv"
    sentiment_path = tmp_path / "reviews_with_sentiment.csv"
    row = {
        "review_id": "r1",
        "review_text": "slow login",
        "rating": 2,
        "date": "2026-05-17",
        "bank_name": "Commercial Bank of Ethiopia",
        "source": "Google Play",
        "sentiment_label": "negative",
        "sentiment_score": -0.6,
        "identified_theme": "Account Access",
    }
    sentiment_df = pd.DataFrame([row])
    sentiment_df.drop(columns=["sentiment_label", "sentiment_score"]).to_csv(clean_path, index=False)
    sentiment_df.to_csv(sentiment_path, index=False)

    try:
        validate_outputs(clean_path, sentiment_path, min_reviews=2)
    except ValueError as exc:
        assert "expected at least 2" in str(exc)
    else:
        raise AssertionError("Expected ValueError for insufficient sentiment rows")
