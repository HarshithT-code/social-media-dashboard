from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

_analyzer = SentimentIntensityAnalyzer()


def clean_text(text: str) -> str:
    """Remove URLs, mentions, and extra whitespace."""
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#(\w+)", r"\1", text)
    return text.strip()


def analyze(text: str) -> dict:
    """
    Returns a dict with:
      - label:    'positive' | 'neutral' | 'negative'
      - score:    compound score in [-1, 1]
      - positive: positive component (0-1)
      - neutral:  neutral component (0-1)
      - negative: negative component (0-1)
    """
    cleaned = clean_text(text)
    scores = _analyzer.polarity_scores(cleaned)
    compound = scores["compound"]

    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return {
        "label": label,
        "score": round(compound, 4),
        "positive": round(scores["pos"], 4),
        "neutral": round(scores["neu"], 4),
        "negative": round(scores["neg"], 4),
        "text": text,
        "cleaned": cleaned,
    }


def analyze_batch(posts: list[dict], text_key: str = "text") -> list[dict]:
    """
    Accepts a list of dicts, each having at least `text_key`.
    Returns the same list with sentiment fields merged in.
    """
    results = []
    for post in posts:
        sentiment = analyze(post.get(text_key, ""))
        results.append({**post, **sentiment})
    return results


def aggregate_stats(analyzed_posts: list[dict]) -> dict:
    """
    Returns summary counts and average scores across analyzed posts.
    """
    total = len(analyzed_posts)
    if total == 0:
        return {"total": 0, "positive": 0, "neutral": 0, "negative": 0, "avg_score": 0}

    counts = {"positive": 0, "neutral": 0, "negative": 0}
    score_sum = 0.0
    for p in analyzed_posts:
        counts[p["label"]] += 1
        score_sum += p["score"]

    return {
        "total": total,
        "positive": counts["positive"],
        "neutral": counts["neutral"],
        "negative": counts["negative"],
        "avg_score": round(score_sum / total, 4),
        "positive_pct": round(counts["positive"] / total * 100, 1),
        "neutral_pct": round(counts["neutral"] / total * 100, 1),
        "negative_pct": round(counts["negative"] / total * 100, 1),
    }
