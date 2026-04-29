# Couples Bucket List

A shared bucket list app where two partners can add, vote on, and complete goals together — built with Streamlit and SQLite.

## Features

- **Two-Profile System** — Each partner has their own name, avatar, and PIN-protected login
- **Goal Management** — Add goals across 6 categories: Travel, Food, Experience, Life, Challenges, Romance
- **Two-Vote Approval** — Goals need both partners to approve before they become active
- **Together & Solo Goals** — Some goals need both partners, some are supportive solo goals
- **Date Night Generator** — Pick a random approved goal when you can't decide what to do
- **Couples Dashboard** — Track progress with stats and charts

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Tech Stack

- **Streamlit** — UI framework
- **SQLite** — Local database (auto-created on first run)
- **Pandas** — Data handling for dashboard charts
