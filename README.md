# AI-Brand-Monitor

AI-Brand-Monitor is an AI-powered monitoring system that tracks developer discussions about a brand on Hacker News and analyzes them using a local LLM.
The system collects mentions of a brand, stores them in a database, performs AI-based sentiment and topic analysis, and displays insights through a Streamlit dashboard.

---

# Project Structure

```
AI-Brand-Monitor/
│
├── backend/
│   ├── database.py
│   │   Handles database operations such as creating tables,
│   │   inserting brand mentions, and retrieving stored data.
│   │
│   ├── data_sources.py
│   │   Contains functions responsible for fetching brand mentions
│   │   from external sources such as the Hacker News API.
│   │
│   ├── ai_analysis.py
│   │   Performs AI-powered analysis on mentions including
│   │   sentiment classification, topic categorization,
│   │   and urgency detection using a local LLM.
│   │
│   ├── reporting.py
│   │   Generates AI summaries and insights from analyzed data,
│   │   such as summaries of positive or negative feedback.
│   │
│   └── config.py
│       Stores project configuration values such as
│       model names, database paths, and API constants.
│
├── frontend/
│   └── app.py
│       Streamlit dashboard that provides the user interface.
│       Displays sentiment charts, topic distributions,
│       raw data tables, and AI-generated summaries.
│
├── data/
│   └── brand_monitor.db
│       SQLite database file that stores collected mentions
│       and their AI analysis results.
│
├── tests/
│   └── test_backend.py
│       Contains scripts used to test backend functionality.
│
├── requirements.txt
│   Lists all Python dependencies required for the project.
│
└── README.md
│   Documentation describing the project and how to run it.
```

---

# Main Features

* Fetch brand mentions from Hacker News
* Store mentions in a SQLite database
* Perform AI-based sentiment, topic, and urgency classification
* Visualize insights with a Streamlit dashboard
* Generate AI summaries of customer feedback

---

# Tech Stack

* Python
* Streamlit
* SQLite
* Ollama (Local LLM)
* LangChain
* Pandas
* Plotly

---

# Running the Project

Install dependencies:

```
pip install -r requirements.txt
```

Run the dashboard:

```
streamlit run frontend/app.py
```

---

This project demonstrates how AI models can be combined with real-world data sources to build an intelligent brand monitoring and analytics system.
