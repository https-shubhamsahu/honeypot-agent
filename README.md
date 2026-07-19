# Honeypot Agent

An agentic AI honeypot that detects scam attempts and engages the scammer in-character — wasting their time while extracting actionable intelligence.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=flat-square)

## Overview

Honeypot Agent sits behind a chat endpoint and does two things automatically: it classifies incoming messages for scam intent, and — once a scam is detected — engages the sender as "Grandma Betty," a non-tech-savvy, polite, easily-confused persona designed to keep scammers talking (and wasting effort) while the system quietly extracts identifying details from the conversation (phone numbers, bank/account references, links, and other indicators).

## Features

- **Scam detection** — LLM-based classification of whether an incoming message has scam intent (`ScamDetector`)
- **Persona-driven engagement** — an in-character agent (`agent_engine.py`) strings the scammer along without revealing it's an AI
- **Intelligence extraction** — pulls structured indicators (contact info, financial details, links) out of the conversation history (`intelligence_extractor.py`)
- **Admin dashboard** — reviewable log of conversations with the AI's reasoning exposed
- **Stats dashboard** — aggregate engagement/detection metrics
- **Endpoint tester** — built-in tool to validate the API surface

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Uvicorn |
| LLM | Groq (OpenAI-compatible API), via `openai` SDK |
| Validation | Pydantic |
| Testing | pytest, pytest-asyncio |

## Getting Started

### Prerequisites
- Python 3.10+
- A Groq API key

### Installation

```bash
git clone https://github.com/https-shubhamsahu/honeypot-agent.git
cd honeypot-agent
pip install -r requirements.txt
```

### Configuration

Set the following environment variables (e.g. in a `.env` file):

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key used for scam detection, persona engagement, and intelligence extraction |
| `HONEYPOT_API_KEY` | API key required to authenticate requests to this service |
| `GUVI_CALLBACK_URL` | Callback URL for the GUVI evaluation harness |

### Run locally

```bash
uvicorn main:app --reload
```

## API Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| `POST` | `/chat` | Main honeypot endpoint | `x-api-key` header |
| `GET` | `/dashboard` | Stats dashboard | — |
| `GET` | `/admin` | Admin panel with AI reasoning | — |
| `GET` | `/tester` | Endpoint validation tool | — |

## Project Structure

```
app/
├── api/
│   ├── routes.py             # /chat endpoint
│   ├── dashboard.py           # Stats dashboard
│   └── admin.py                # Admin panel
├── core/
│   └── config.py                # Settings (API keys, callback URL)
├── models.py                    # Message / conversation models
└── services/
    ├── agent_engine.py           # Persona-driven scammer engagement
    ├── scam_detector.py           # Scam-intent classification
    ├── intelligence_extractor.py  # Structured indicator extraction
    ├── reporting.py
    ├── admin_logger.py
    └── data_store.py

static/
├── admin.html
├── dashboard.html
└── tester.html

tests/
├── test_api.py
└── manual_test.py
```

## Deployment

Configured for Render (`render.yaml`, `Procfile`, `runtime.txt`).

## Contributing

Fork the repository, create a feature branch, and open a pull request.

## License

No license file is currently present in this repository.
