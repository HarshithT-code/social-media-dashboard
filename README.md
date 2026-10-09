# Sentiment Analysis Dashboard for Social Media Platform

A full-stack web application that performs real-time sentiment analysis on social media posts using NLP (VADER). Built with **Python/Flask** on the backend and a clean dark-mode dashboard on the frontend.

---

## Features

- **Dashboard** — KPI cards, doughnut chart, timeline line chart, platform bar chart, top posts chart, and a full posts table
- **Filters** — filter by platform (Twitter / Reddit) and keyword
- **Analyze Text** — paste any text and get an instant positive/neutral/negative score with visual score bars
- **Upload CSV** — upload your own dataset (must have a `text` column) and get instant analysis + stats
- **REST API** — all analysis logic is exposed as clean JSON endpoints

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11+, Flask 3 |
| NLP | VADER Sentiment, TextBlob |
| Data | Pandas |
| Frontend | HTML5, CSS3, Vanilla JS |
| Charts | Chart.js 4 |

---

## Project Structure

```
social_media_dashboard/
├── app.py                   # Flask application + API routes
├── sentiment/
│   ├── __init__.py
│   └── analyzer.py          # VADER-based sentiment engine
├── data/
│   └── sample_posts.csv     # 25 sample social media posts
├── static/
│   ├── css/style.css        # Dark-mode dashboard styles
│   └── js/dashboard.js      # Chart rendering + API calls
├── templates/
│   └── index.html           # Main dashboard HTML
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard` | Full analyzed dataset + stats. Supports `?platform=Twitter&keyword=game` |
| `POST` | `/api/analyze` | Analyze a single text. Body: `{"text": "..."}` |
| `POST` | `/api/upload` | Upload a CSV file for batch analysis |
| `GET` | `/api/platforms` | List available platforms in the dataset |

---

## CSV Upload Format

Your CSV must include at minimum a `text` column:

```csv
text,platform,username
"I love this product!",Twitter,@user1
"Terrible experience.",Reddit,u/user2
```

---

## Sentiment Labels

| Label | Compound Score Range |
|---|---|
| Positive | ≥ 0.05 |
| Neutral | −0.05 to 0.05 |
| Negative | ≤ −0.05 |
