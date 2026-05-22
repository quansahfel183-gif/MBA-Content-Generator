# Edenbrook Villa — AI Marketing OS

A full-stack AI-powered marketing dashboard for **Qluxe Homes** and the **Edenbrook Villa** luxury development in Tse Addo, Accra, Ghana.

## Setup

### 1. Install dependencies

```bash
cd edenbrook-marketing-os
pip install -r requirements.txt
```

### 2. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

Or create a `.env` file and load it (requires `python-dotenv`):

```
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. Run the server

```bash
uvicorn main:app --reload --port 8000
```

### 4. Open the app

Visit [http://localhost:8000](http://localhost:8000)

---

## Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | **Content Generator** | Generate social posts by pillar, format, and tone. Batch 7-day content. |
| 2 | **Post Scheduler** | Monthly calendar, post queue, SQLite storage. |
| 3 | **Competitor Analysis** | Radar chart vs. 6 Accra luxury developers. AI counter-content. |
| 4 | **Lookalike Content Engine** | 6 inspiration posts with Edenbrook adaptations and AI regeneration. |
| 5 | **SEO + Blog Generator** | 10 target keywords, outline, full 1,500-word articles, meta tags. |
| 6 | **Google Ads Builder** | 3 ad variations, previews, more variations, landing page copy. |

## Tech Stack

- **Backend:** FastAPI + Python
- **Database:** SQLite via SQLAlchemy
- **AI:** Anthropic Claude (`claude-sonnet-4-6`)
- **Frontend:** Single HTML/CSS/JS file — no build step
- **Charts:** Chart.js (CDN)
- **Icons/Fonts:** Font Awesome + Google Fonts (CDN)
