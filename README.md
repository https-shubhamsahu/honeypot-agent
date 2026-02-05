# Honeypot Agent

Agentic AI-powered honeypot for scam detection and engagement.

## Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Environment Variables Required

Set these in your deployment platform:

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Your Groq API key for LLM |
| `HONEYPOT_API_KEY` | API key for authentication |
| `GUVI_CALLBACK_URL` | GUVI evaluation callback URL |

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Endpoints

- `POST /chat` - Main honeypot endpoint (requires x-api-key header)
- `GET /dashboard` - Stats dashboard
- `GET /admin` - Admin panel with AI reasoning
- `GET /tester` - Endpoint validation tool
