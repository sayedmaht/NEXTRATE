# NEXTRATE

### Real-Time Currency Converter with AI-Powered Predictions

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-F55036?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-22d3ee?style=for-the-badge)](LICENSE)

A premium dark-themed web application that converts currencies in real-time, provides AI-driven price predictions, and features an intelligent NLP-powered financial chatbot — all powered by **Groq's blazing-fast LLM inference**.

[Features](#-features) · [Screenshots](#-screenshots) · [Quick Start](#-quick-start) · [API Keys](#-api-keys) · [Tech Stack](#-tech-stack) · [Deployment](#-deployment)

</div>

---

## ✨ Features

### 💱 Real-Time Currency Conversion
- **56 fiat currencies** — USD, EUR, GBP, JPY, INR, and more
- **120+ cryptocurrencies** — BTC, ETH, SOL, DOGE, and every major coin
- Cross-conversion between fiat ↔ crypto with live exchange rates
- Powered by **CoinGecko** and **ExchangeRate API**

### 🔮 AI Price Predictions
- **30-day price forecasts** for any currency
- **Crypto analysis**: market cap, supply dynamics, volume, momentum
- **Fiat analysis**: GDP growth, inflation, per capita income, debt-to-GDP
- Confidence levels and key driving factors
- Powered by **Groq LLM** (LLaMA 3.3 70B)

### 🤖 NLP-Powered AI Chatbot
- **Intent classification** — detects price checks, conversions, predictions, comparisons, education queries
- **Entity extraction** — recognizes 80+ currency aliases (e.g., "Bitcoin" → BTC, "Rupee" → INR)
- **Sentiment detection** — understands bullish/bearish context
- **Live market data injection** — feeds real-time prices into AI responses
- Detailed, markdown-formatted financial analysis

### 📊 Market Dashboard
- Live stats: total market cap, top gainers, currency counts
- Trending cryptocurrency cards with 24h change
- Popular fiat currencies with exchange rates
- Historical price charts (7D, 30D, 90D, 1Y)

### 🎨 Premium UI
- **Aurora mesh gradient** dark backgrounds
- **Glassmorphism** cards with ambient corner glow
- **Neon gradient borders** (purple → cyan) on hover
- **Outfit + JetBrains Mono** typography
- Spring physics animations
- Fully responsive (desktop, tablet, mobile)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nextrate-ai.git
cd nextrate-ai

# Install dependencies
pip install -r requirements.txt

# Set your Groq API key
# Windows:
set GROQ_API_KEY=your_groq_api_key_here
# Linux/Mac:
export GROQ_API_KEY=your_groq_api_key_here

# Run the application
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 🔑 API Keys

| API | Purpose | Required? | Get Key |
|-----|---------|:---------:|---------|
| **Groq** | AI chatbot & predictions | Optional* | [console.groq.com](https://console.groq.com) |
| CoinGecko | Crypto prices & data | Free (no key) | — |
| ExchangeRate | Fiat exchange rates | Free (no key) | — |

> \* Without a Groq API key, AI features fall back to intelligent mock responses. All other features (converter, charts, market data) work fully without any API key.

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **Flask** | Web server & REST API |
| **Groq SDK** | LLM inference (LLaMA 3.3 70B) |
| **Custom NLP Engine** | Intent classification, entity extraction, sentiment detection |
| **CoinGecko API** | Cryptocurrency market data |
| **ExchangeRate API** | Fiat currency exchange rates |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **Vanilla JS** | Application logic, DOM manipulation |
| **Chart.js** | Historical & prediction charts |
| **CSS3** | Premium dark theme with glassmorphism |
| **Outfit Font** | Modern typography |

---

## 📁 Project Structure

```
nextrate-ai/
├── app.py              # Flask server, API routes, caching
├── agents.py           # Groq-powered AI agents (chatbot + predictions)
├── nlp_engine.py       # NLP intent classifier & entity extractor
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Single-page application
└── static/
    ├── css/
    │   └── style.css   # Premium dark theme (800+ lines)
    └── js/
        ├── app.js      # Core app logic, navigation, data fetching
        ├── charts.js   # Chart.js configuration & rendering
        └── chatbot.js  # Chatbot UI & message handling
```

---

## 🌐 Deployment

### Render (Recommended — Free)

1. Push to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add environment variable: `GROQ_API_KEY`
6. Deploy!

> Add `gunicorn` to `requirements.txt` before deploying:
> ```
> gunicorn==23.0.0
> ```

### Other Options
- **Railway.app** — Auto-detects Flask, free tier
- **PythonAnywhere** — Upload files directly, no Git needed
- **DigitalOcean/AWS** — VPS with gunicorn + nginx

### 📱 Mobile Access
The app is fully responsive. After deploying, open the URL on your phone and **Add to Home Screen** for an app-like experience.

---

## 🧠 NLP Pipeline

```
User Message
    │
    ├─→ Intent Classification (8 intents: price_check, conversion, prediction, etc.)
    ├─→ Currency Entity Extraction (80+ aliases mapped to symbols)
    ├─→ Amount Parsing (extracts numeric values)
    └─→ Sentiment Detection (positive/negative/neutral)
           │
           ▼
    Context Builder → Injects live market data
           │
           ▼
    Groq LLM (LLaMA 3.3 70B) → Rich markdown response
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ⚡ by NextRate AI**

*Real-time data • AI predictions • Smart chatbot*

</div>
