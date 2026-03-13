# 📡 AI Brand Monitor

A local, privacy-first brand monitoring dashboard that pulls mentions from **Hacker News**, classifies them with a **local LLM** (via Ollama), and surfaces sentiment trends, topic breakdowns, and an AI-written summary — all in a Streamlit UI.

---

## Features

- **Fetch** the latest Hacker News stories mentioning any brand
- **Sentiment analysis** — classifies each mention as `positive`, `negative`, or `neutral`
- **Topic classification** — buckets mentions into `product_feedback`, `bug_report`, `pricing`, `feature_request`, or `general_discussion`
- **AI summary** — a 2–3 sentence LLM-generated overview of the brand's current online perception
- **Charts** — donut chart for sentiment, horizontal bar chart for topics
- **Mentions table** — sortable, with clickable links, scores, and comment counts
- **Fully local** — no data leaves your machine; the LLM runs via Ollama

---

## Project Structure

```
project/
├── app.py                  # Streamlit UI entry point
├── backend/
│   ├── config.py           # Environment-based configuration
│   ├── database.py         # SQLite CRUD operations
│   ├── data_sources.py     # Hacker News API fetching
│   ├── ai_analysis.py      # Sentiment & topic classification
│   └── reporting.py        # Aggregations & AI summary for UI
├── data/
│   └── brand_monitor.db    # SQLite database (auto-created)
├── .env                    # Your environment variables (see below)
└── requirements.txt
```

---

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running locally
- The model you intend to use pulled in Ollama (default: `mistral:7b`)

```bash
ollama pull mistral:7b
```

---

## Setup

**1. Clone the repo**

```bash
git clone https://github.com/your-username/ai-brand-monitor.git
cd ai-brand-monitor
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:

```env
LLM_MODEL=mistral:7b
DB_PATH=data/brand_monitor.db
HN_API_BASE=https://hacker-news.firebaseio.com/v0
```

All three keys have sensible defaults, so `.env` is optional unless you want to change them.

**5. Run the app**

```bash
streamlit run app.py
```

---

## Usage

1. Enter a brand name in the sidebar (e.g. `Supabase`, `OpenAI`, `Linear`)
2. Click **🔍 Fetch Mentions** — pulls the 50 latest HN stories and stores matching ones
3. Click **🤖 Run AI Analysis** — classifies each unanalysed mention with the local LLM
4. Explore the **Charts** tab for sentiment and topic distributions
5. Open the **Details** tab for the AI summary and the full mentions table

> Switching to a new brand automatically resets state and clears the cache.

---

## Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `LLM_MODEL` | `mistral:7b` | Any Ollama-compatible model name |
| `DB_PATH` | `data/brand_monitor.db` | Path to the SQLite database file |
| `HN_API_BASE` | `https://hacker-news.firebaseio.com/v0` | Hacker News Firebase API base URL |

---

## Requirements

```
streamlit
requests
python-dotenv
langchain-ollama
pandas
plotly
```

---

## Limitations

- **Hacker News only** — the current data source fetches the 50 most recent stories. Other platforms (Reddit, Twitter/X) can be added by extending `data_sources.py` and calling `insert_mention()`.
- **LLM speed** — analysis time scales with the number of unanalysed mentions and your hardware. A GPU-accelerated Ollama setup is recommended for large batches.
- **Single-user** — the SQLite database is not designed for concurrent multi-user access.

---

## Extending the Project

**Add a new data source**
Implement a `fetch_<platform>_mentions(brand)` function in `data_sources.py` that calls `insert_mention()` for each hit. Hook it into `app.py` alongside `fetch_hackernews_mentions`.

**Add a new topic category**
Update the allowed set in `get_topic()` inside `ai_analysis.py` and update the prompt accordingly.

**Swap the LLM**
Change `LLM_MODEL` in `.env` to any model available in your Ollama instance (e.g. `llama3`, `gemma:7b`).

---

## License

MIT