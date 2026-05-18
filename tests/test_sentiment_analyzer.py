"""Unit tests for sentiment analyzer module."""

import pytest

from src.sentiment_analyzer import SentimentAnalyzer, SentimentModel, SentimentResult


class TestSentimentAnalyzer:
    """Test sentiment analysis functionality."""

    @pytest.fixture
    def vader_analyzer(self):
        """Create VADER analyzer."""
        return SentimentAnalyzer(model_type=SentimentModel.VADER)

    @pytest.fixture
    def distilbert_analyzer(self):
        """Create Distilbert analyzer (if available)."""
        try:
            return SentimentAnalyzer(model_type=SentimentModel.DISTILBERT)
        except Exception:
            pytest.skip("Distilbert not available")

    def test_analyzer_initialization(self, vader_analyzer):
        """Test analyzer initializes correctly."""
        assert vader_analyzer is not None
        assert vader_analyzer.vader_analyzer is not None

    def test_positive_sentiment_vader(self, vader_analyzer):
        """Test positive sentiment detection with VADER."""
        result = vader_analyzer.analyze("I love this app! It's amazing!")
        assert result.label == "positive"
        assert result.score > 0
        assert 0 <= result.confidence <= 1
        assert result.model == "vader"

    def test_negative_sentiment_vader(self, vader_analyzer):
        """Test negative sentiment detection with VADER."""
        result = vader_analyzer.analyze("This app is terrible and broken")
        assert result.label == "negative"
        assert result.score < 0
        assert 0 <= result.confidence <= 1

    def test_neutral_sentiment_vader(self, vader_analyzer):
        """Test neutral sentiment detection with VADER."""
        result = vader_analyzer.analyze("The app has three menu items")
        assert result.label == "neutral"
        assert abs(result.score) < 0.05

    def test_empty_text(self, vader_analyzer):
        """Test handling of empty text."""
        result = vader_analyzer.analyze("")
        assert result.label == "neutral"
        assert result.score == 0.0

    def test_none_text(self, vader_analyzer):
        """Test handling of None input."""
        result = vader_analyzer.analyze(None)
        assert result.model == "error"

    def test_batch_analysis(self, vader_analyzer):
        """Test batch sentiment analysis."""
        texts = [
            "I love this app!",
            "This is terrible",
            "The screen has three buttons"
        ]
        results = vader_analyzer.batch_analyze(texts)
        assert len(results) == 3
        assert results[0].label == "positive"
        assert results[1].label == "negative"
        assert results[2].label == "neutral"

    def test_sentiment_result_namedtuple(self):
        """Test SentimentResult namedtuple."""
        result = SentimentResult(
            label="positive",
            score=0.8,
            confidence=0.9,
            model="test"
        )
        assert result.label == "positive"
        assert result.score == 0.8
        assert result.confidence == 0.9
        assert result.model == "test"

    def test_consistency_across_calls(self, vader_analyzer):
        """Test that same text produces same result."""
        text = "This is a consistent test"
        result1 = vader_analyzer.analyze(text)
        result2 = vader_analyzer.analyze(text)
        assert result1.label == result2.label
        assert result1.score == result2.score

    def test_long_text_handling(self, vader_analyzer):
        """Test handling of long text."""
        long_text = "This app is great! " * 100
        result = vader_analyzer.analyze(long_text)
        assert isinstance(result, SentimentResult)
        assert result.label in ["positive", "negative", "neutral"]


class TestSentimentModels:
    """Test sentiment model enum."""

    def test_model_enum_values(self):
        """Test SentimentModel enum values."""
        assert SentimentModel.VADER.value == "vader"
        assert SentimentModel.DISTILBERT.value == "distilbert"
        assert SentimentModel.ENSEMBLE.value == "ensemble"

    def test_model_enum_members(self):
        """Test all SentimentModel members exist."""
        assert len(SentimentModel) == 3
