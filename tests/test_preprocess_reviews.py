import pandas as pd

from scripts.preprocess_reviews import preprocess_reviews


def test_preprocess_removes_duplicates_missing_values_and_normalizes_dates():
    raw = pd.DataFrame(
        [
            {
                "review_id": "r1",
                "review_text": " Works well ",
                "rating": "5",
                "date": "2026-05-17 10:11:12",
                "bank_name": "Commercial Bank of Ethiopia",
                "source": "Google Play",
            },
            {
                "review_id": "r1",
                "review_text": "duplicate",
                "rating": "1",
                "date": "2026-05-17",
                "bank_name": "Commercial Bank of Ethiopia",
                "source": "Google Play",
            },
            {
                "review_id": "r2",
                "review_text": None,
                "rating": "4",
                "date": "2026-05-16",
                "bank_name": "Dashen Bank",
                "source": "Google Play",
            },
            {
                "review_id": "r3",
                "review_text": "Missing rating",
                "rating": None,
                "date": "2026-05-15",
                "bank_name": "Bank of Abyssinia",
                "source": "Google Play",
            },
        ]
    )

    cleaned = preprocess_reviews(raw)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "review_id"] == "r1"
    assert cleaned.loc[0, "review_text"] == "Works well"
    assert cleaned.loc[0, "rating"] == 5
    assert cleaned.loc[0, "date"] == "2026-05-17"


def test_preprocess_requires_rubric_columns():
    raw = pd.DataFrame([{"review_text": "ok"}])

    try:
        preprocess_reviews(raw)
    except ValueError as exc:
        assert "missing required columns" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing columns")
