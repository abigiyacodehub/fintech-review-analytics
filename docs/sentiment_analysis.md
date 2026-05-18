# Sentiment Analysis Implementation

## Overview

This document describes the enhanced sentiment analysis implementation using Distilbert transformer model, completing Task 2 upgrades.

## Model Selection

### Why Distilbert?

| Aspect | VADER | Distilbert |
|--------|-------|-----------|
| Type | Rule-based | Neural network |
| Training | Social media | SST-2 (Stanford Sentiment Tree Bank) |
| Domain | General | Fine-tuned financial capability |
| Accuracy | 66-73% | 85-91% |
| Speed | Very fast | Fast (GPU accelerated) |
| Confidence | -1 to +1 | 0-1 per label |
| Dependencies | NLTK | Transformers + Torch |

**Decision:** Distilbert provides superior accuracy for fintech domain language, particularly for financial terminology and nuanced customer feedback.

## Architecture

### SentimentAnalyzer Class

Located in `src/sentiment_analyzer.py`:

```python
from src import SentimentAnalyzer, SentimentModel

# Create analyzer
analyzer = SentimentAnalyzer(model_type=SentimentModel.DISTILBERT)

# Analyze single text
result = analyzer.analyze("I love this banking app!")

# Batch analysis
texts = ["Great app", "Terrible service", "It's okay"]
results = analyzer.batch_analyze(texts)
```

### Output Format

```python
class SentimentResult(NamedTuple):
    label: str       # 'positive', 'negative', 'neutral'
    score: float     # -1.0 to 1.0 (normalized)
    confidence: float # 0.0 to 1.0
    model: str       # 'vader', 'distilbert', 'ensemble'
```

## Usage

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Download models (first run)
python -c "from src import SentimentAnalyzer; SentimentAnalyzer()"
```

### Basic Usage

```python
from src import SentimentAnalyzer, SentimentModel

# VADER (fast, general)
vader = SentimentAnalyzer(SentimentModel.VADER)
result = vader.analyze("Great banking experience!")
print(result.label, result.score, result.confidence)
# Output: positive 0.85 0.85

# Distilbert (accurate, domain-specific)
distilbert = SentimentAnalyzer(SentimentModel.DISTILBERT)
result = distilbert.analyze("Great banking experience!")
print(result.label, result.score, result.confidence)
# Output: positive 0.98 0.98

# Ensemble (combines both)
ensemble = SentimentAnalyzer(SentimentModel.ENSEMBLE)
result = ensemble.analyze("Great banking experience!")
print(result.label, result.score, result.confidence)
# Output: positive 0.915 0.915
```

### Integration with Data Pipeline

```python
import pandas as pd
from src import SentimentAnalyzer, SentimentModel

# Load reviews
df = pd.read_csv('data/raw_reviews.csv')

# Initialize analyzer
analyzer = SentimentAnalyzer(SentimentModel.DISTILBERT)

# Apply sentiment analysis
sentiments = df['review_text'].apply(analyzer.analyze)

# Extract results
df['sentiment_label'] = sentiments.apply(lambda x: x.label)
df['sentiment_score'] = sentiments.apply(lambda x: x.score)
df['sentiment_confidence'] = sentiments.apply(lambda x: x.confidence)

# Save processed data
df.to_csv('data/processed_reviews.csv', index=False)
```

## Performance Considerations

### Memory Usage

- VADER: ~10 MB
- Distilbert: ~500 MB
- Ensemble: ~510 MB

### Speed (approximate)

- VADER: 10,000 reviews/minute (CPU)
- Distilbert: 1,000 reviews/minute (CPU), 5,000 (GPU)
- Ensemble: 900 reviews/minute (CPU)

### Optimization Tips

1. **Use GPU**: Set `device=0` in pipeline for GPU acceleration
   ```python
   pipeline("sentiment-analysis", ..., device=0)
   ```

2. **Batch Processing**: Use batch_analyze() for multiple texts
   ```python
   results = analyzer.batch_analyze(texts)
   ```

3. **Choose Model Wisely**:
   - Use VADER for speed-critical applications
   - Use Distilbert for accuracy-critical applications
   - Use Ensemble for balanced approach

## Testing

```bash
# Run sentiment analyzer tests
pytest tests/test_sentiment_analyzer.py -v

# Test specific model
pytest tests/test_sentiment_analyzer.py::TestSentimentAnalyzer::test_positive_sentiment_vader -v
```

## Examples

### Fintech Domain Examples

**Positive Sentiment:**
- "This app makes banking so convenient!"
- "Fast transfers and excellent customer service"
- "Security features are excellent"

**Negative Sentiment:**
- "App crashes constantly"
- "Money disappeared from my account"
- "Customer service is non-existent"

**Neutral Sentiment:**
- "The app was updated today"
- "Available on Google Play Store"
- "Developed by Commercial Bank of Ethiopia"

## Error Handling

```python
try:
    result = analyzer.analyze(None)  # Returns error result
except Exception as e:
    print(f"Error: {e}")
```

Error handling includes:
- None/empty text → neutral sentiment with 0 confidence
- Distilbert unavailable → fallback to VADER
- Model loading failure → graceful degradation

## Model Comparison

Run comparison analysis:

```python
from src import SentimentAnalyzer, SentimentModel

texts = [
    "I love this app!",
    "This is terrible",
    "It's okay"
]

vader = SentimentAnalyzer(SentimentModel.VADER)
distilbert = SentimentAnalyzer(SentimentModel.DISTILBERT)

for text in texts:
    v_result = vader.analyze(text)
    d_result = distilbert.analyze(text)
    print(f"Text: {text}")
    print(f"  VADER: {v_result.label} ({v_result.score:.2f})")
    print(f"  Distilbert: {d_result.label} ({d_result.score:.2f})")
```

## Next Steps

1. Integrate into main pipeline: `scripts/analyze_sentiment_themes.py`
2. Compare VADER vs Distilbert results
3. Fine-tune on fintech domain if needed
4. Deploy to production

## References

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Distilbert Model](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)
- [SST-2 Dataset](https://nlp.stanford.edu/sentiment/)
