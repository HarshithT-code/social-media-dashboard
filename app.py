import os
import csv
import io
import json
from flask import Flask, render_template, request, jsonify
import pandas as pd
from sentiment.analyzer import analyze, analyze_batch, aggregate_stats

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sample_posts.csv")


def load_posts() -> list[dict]:
    """Load the sample CSV into a list of dicts."""
    posts = []
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)
    return posts


# ── Routes ─────────────────────────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dashboard")
def api_dashboard():
    """
    Returns full analyzed dataset + aggregate stats.
    Optional query params:
      - platform: filter by 'Twitter' or 'Reddit'
      - keyword:  filter posts whose text contains this keyword (case-insensitive)
    """
    posts = load_posts()

    platform = request.args.get("platform", "").strip()
    keyword = request.args.get("keyword", "").strip().lower()

    if platform:
        posts = [p for p in posts if p["platform"].lower() == platform.lower()]
    if keyword:
        posts = [p for p in posts if keyword in p["text"].lower()]

    analyzed = analyze_batch(posts)
    stats = aggregate_stats(analyzed)

    # Build timeline: group by date, count sentiments
    timeline: dict[str, dict] = {}
    for p in analyzed:
        date = p["timestamp"][:10]  # YYYY-MM-DD
        if date not in timeline:
            timeline[date] = {"positive": 0, "neutral": 0, "negative": 0}
        timeline[date][p["label"]] += 1

    timeline_sorted = [
        {"date": d, **counts} for d, counts in sorted(timeline.items())
    ]

    # Top posts by likes for each sentiment
    top_posts = sorted(analyzed, key=lambda x: int(x.get("likes", 0)), reverse=True)[:10]

    return jsonify({
        "stats": stats,
        "posts": analyzed,
        "timeline": timeline_sorted,
        "top_posts": top_posts,
    })


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """
    Analyze a single piece of text submitted via JSON body:
      { "text": "your text here" }
    """
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400
    result = analyze(text)
    return jsonify(result)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """
    Accept a CSV file upload with a 'text' column (and optionally platform, username, timestamp).
    Returns analysis results + aggregate stats.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        content = file.read().decode("utf-8")
        df = pd.read_csv(io.StringIO(content))
        if "text" not in df.columns:
            return jsonify({"error": "CSV must contain a 'text' column"}), 400
        posts = df.to_dict(orient="records")
        analyzed = analyze_batch(posts)
        stats = aggregate_stats(analyzed)
        return jsonify({"stats": stats, "posts": analyzed})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/platforms")
def api_platforms():
    """Return available platforms in the dataset."""
    posts = load_posts()
    platforms = sorted(set(p["platform"] for p in posts))
    return jsonify({"platforms": platforms})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
