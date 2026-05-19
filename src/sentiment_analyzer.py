"""Sentiment analysis using VADER and/or Distilbert models."""

from __future__ import annotations

import logging
from enum import Enum
from typing import NamedTuple

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("transformers not installed; distilbert unavailable")

from nltk.sentiment import SentimentIntensityAnalyzer


class SentimentModel(Enum):
    """Available sentiment analysis models."""
    VADER = "vader"
    DISTILBERT = "distilbert"
    ENSEMBLE = "ensemble"


class SentimentResult(NamedTuple):
    """Sentiment analysis result with model information."""
    label: str  # positive, negative, neutral
    score: float  # -1 to 1 (VADER) or 0-1 per label (distilbert)
    confidence: float  # confidence score 0-1
    model: str  # which model produced this result


class SentimentAnalyzer:
    """Unified sentiment analysis interface supporting multiple models."""

    def __init__(self, model_type: SentimentModel = SentimentModel.DISTILBERT):
        """
        Initialize sentiment analyzer.

        Args:
            model_type: Which model to use (VADER, DISTILBERT, or ENSEMBLE)
        """
        self.model_type = model_type
        self.vader_analyzer = None
        self.distilbert_pipeline = None

        # Initialize VADER (always available)
        try:
            from nltk.data import find
            find('vader_lexicon')
        except LookupError:
            import nltk
            nltk.download('vader_lexicon', quiet=True)
        
        self.vader_analyzer = SentimentIntensityAnalyzer()

        # Initialize Distilbert if available and requested
        if TRANSFORMERS_AVAILABLE and model_type != SentimentModel.VADER:
            try:
                self.distilbert_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=-1  # Use CPU by default
                )
                logging.info("Distilbert model loaded successfully")
            except Exception as e:
                logging.warning(f"Failed to load distilbert: {e}")
                if model_type == SentimentModel.DISTILBERT:
                    logging.info("Falling back to VADER")
                    self.model_type = SentimentModel.VADER

    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            SentimentResult with label, score, and confidence
        """
        if not text or not isinstance(text, str):
            return SentimentResult("neutral", 0.0, 0.0, "error")

        if self.model_type == SentimentModel.VADER:
            return self._analyze_vader(text)
        elif self.model_type == SentimentModel.DISTILBERT:
            return self._analyze_distilbert(text)
        elif self.model_type == SentimentModel.ENSEMBLE:
            return self._analyze_ensemble(text)

    def _analyze_vader(self, text: str) -> SentimentResult:
        """Analyze using VADER."""
        scores = self.vader_analyzer.polarity_scores(text)
        compound = scores['compound']

        # Convert to label
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        confidence = abs(compound)

        return SentimentResult(
            label=label,
            score=compound,
            confidence=confidence,
            model="vader"
        )

    def _analyze_distilbert(self, text: str) -> SentimentResult:
        """Analyze using Distilbert."""
        if not self.distilbert_pipeline:
            logging.warning("Distilbert not available, using VADER")
            return self._analyze_vader(text)

        try:
            results = self.distilbert_pipeline(text, truncation=True)
            result = results[0]

            label = result['label'].lower()
            score = result['score']

            # Normalize score to -1 to 1 range for consistency with VADER
            if label == "positive":
                normalized_score = score
            else:
                normalized_score = -score

            return SentimentResult(
                label=label,
                score=normalized_score,
                confidence=score,
                model="distilbert"
            )
        except Exception as e:
            logging.error(f"Distilbert error: {e}, falling back to VADER")
            return self._analyze_vader(text)

    def _analyze_ensemble(self, text: str) -> SentimentResult:
        """Analyze using both models and average results."""
        vader_result = self._analyze_vader(text)

        if not self.distilbert_pipeline:
            return vader_result

        distilbert_result = self._analyze_distilbert(text)

        # Average scores
        avg_score = (vader_result.score + distilbert_result.score) / 2

        # Determine label from average score
        if avg_score >= 0.05:
            label = "positive"
        elif avg_score <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        avg_confidence = (vader_result.confidence + distilbert_result.confidence) / 2

        return SentimentResult(
            label=label,
            score=avg_score,
            confidence=avg_confidence,
            model="ensemble (vader + distilbert)"
        )

    def batch_analyze(self, texts: list[str]) -> list[SentimentResult]:
        """Analyze multiple texts."""
        return [self.analyze(text) for text in texts]
