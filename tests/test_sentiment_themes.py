import pandas as pd

from scripts.analyze_sentiment_themes import extract_tfidf_keywords, identify_theme, label_from_score


def test_label_from_score_uses_vader_thresholds():
    assert label_from_score(0.5) == "positive"
    assert label_from_score(0.0) == "neutral"
    assert label_from_score(-0.5) == "negative"


def test_extract_tfidf_keywords_returns_grouped_theme_terms():
    df = pd.DataFrame(
        [
            {
                "bank_name": "Dashen Bank",
                "sentiment_label": "negative",
                "review_text": "login failed transfer failed",
            },
            {
                "bank_name": "Dashen Bank",
                "sentiment_label": "negative",
                "review_text": "login error and network error",
            },
            {
                "bank_name": "Bank of Abyssinia",
                "sentiment_label": "positive",
                "review_text": "fast transfer and easy login",
            },
        ]
    )

    keywords = extract_tfidf_keywords(df, top_n=3)

    assert {"bank_name", "sentiment_label", "keyword", "tfidf_score", "rank", "review_count"}.issubset(
        keywords.columns
    )
    assert len(keywords) > 0
    assert keywords["review_count"].max() == 2


def test_identify_theme_maps_business_keywords():
    assert identify_theme("OTP not received during login") == "Account Access"
    assert identify_theme("Transfer failed because the app is slow") == "Transaction Performance"
    assert identify_theme("I like this mobile banking app") == "General Feedback"
