"""
NextRate AI — CrewAI Agents Module (Groq-Powered)
Uses Groq SDK directly for fast, intelligent chatbot and prediction responses.
"""

import os
import json
from groq import Groq

# ─── Configuration ───────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def get_groq_client():
    """Get Groq client instance."""
    if GROQ_API_KEY:
        return Groq(api_key=GROQ_API_KEY)
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Prediction Agent (via Groq direct)
# ═══════════════════════════════════════════════════════════════════════════════

PREDICTION_SYSTEM_PROMPT = """You are a world-class quantitative analyst with 20+ years at top hedge funds (Bridgewater, Renaissance Technologies, Citadel). You combine fundamental analysis, technical analysis, and macroeconomic modeling.

For CRYPTO currencies, you analyze:
- Market cap trends and dominance
- Supply/demand dynamics (circulating vs total supply, burn mechanisms, halving cycles)
- Trading volume patterns and liquidity
- Distance from ATH/ATL for mean reversion signals
- 24h momentum direction and strength

For FIAT currencies, you analyze:
- GDP growth trajectories and economic health
- Inflation differentials and central bank policy
- Interest rate expectations
- Trade balance and current account
- Debt sustainability (debt-to-GDP ratio)
- Per capita income as development indicator
- Business environment and FDI flows

You always provide structured predictions with quantified confidence levels and data-backed reasoning. You NEVER speculate without data. You provide your response strictly in the requested JSON format."""


def run_prediction_crew(currency, currency_type, current_price, market_data, econ_data=None):
    """Generate AI price predictions using Groq's LLM."""
    client = get_groq_client()
    if not client:
        return None

    if currency_type == "crypto":
        user_prompt = f"""Analyze {currency} cryptocurrency and generate a 30-day price prediction.

CURRENT MARKET DATA:
- Current Price: ${current_price}
- Market Cap: ${market_data.get('market_cap', 'N/A')}
- 24h Trading Volume: ${market_data.get('total_volume', 'N/A')}
- Circulating Supply: {market_data.get('circulating_supply', 'N/A')}
- Total Supply: {market_data.get('total_supply', 'N/A')}
- Max Supply: {market_data.get('max_supply', 'N/A')}
- 24h Price Change: {market_data.get('price_change_24h', 'N/A')}%
- All-Time High: ${market_data.get('ath', 'N/A')}
- All-Time Low: ${market_data.get('atl', 'N/A')}

Generate 30 daily predicted prices based on your analysis of market cap, supply dynamics, demand momentum, and technical factors.

Respond with ONLY this JSON (no explanation, no code fences):
{{"prediction_30d": [30 numbers representing daily predicted prices], "confidence": "high/medium/low", "trend": "bullish/bearish/neutral", "analysis": "2-3 sentence data-driven analysis", "factors": ["specific factor 1", "specific factor 2", "specific factor 3"]}}"""
    else:
        user_prompt = f"""Analyze {currency} fiat currency and predict 30-day exchange rate vs USD.

ECONOMIC DATA:
- Current Rate (vs USD): {current_price}
- GDP Growth: {econ_data.get('gdp_growth', 'N/A')}%
- Inflation Rate: {econ_data.get('inflation', 'N/A')}%
- GDP Per Capita: ${econ_data.get('per_capita', 'N/A')}
- Debt-to-GDP: {econ_data.get('debt_gdp', 'N/A')}%

Generate 30 daily predicted exchange rates based on country's economic growth, inflation, per capita income, businesses, and monetary policy.

Respond with ONLY this JSON (no explanation, no code fences):
{{"prediction_30d": [30 numbers representing daily predicted rates], "confidence": "high/medium/low", "trend": "strengthening/weakening/stable", "analysis": "2-3 sentence analysis grounded in economic fundamentals", "factors": ["specific factor 1", "specific factor 2", "specific factor 3"]}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": PREDICTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        text = response.choices[0].message.content.strip()
        # Clean any code fences
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"Groq prediction error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Chatbot Agent (via Groq direct, NLP-enhanced)
# ═══════════════════════════════════════════════════════════════════════════════

CHATBOT_SYSTEM_PROMPT = """You are **NextRate AI**, an elite financial intelligence assistant specializing in currencies. You are NOT a generic chatbot — you are a highly knowledgeable financial expert.

## Your Capabilities
1. **Currency Analysis**: Deep analysis of any fiat or cryptocurrency — price, market cap, supply, trading volume, economic indicators
2. **Price Predictions**: Informed forecasts based on market data and economic fundamentals
3. **Conversions**: Exchange rate information and conversion context
4. **Comparisons**: Side-by-side analysis of different currencies
5. **Education**: Clear explanations of financial concepts with real examples
6. **Market Insights**: Trends, sentiment, and macro overview

## Response Style
- Structure responses with markdown: **bold headers**, bullet points, emojis for visual clarity
- Include SPECIFIC numbers and data points — never be vague
- For crypto: always reference market cap, supply dynamics, volume, and recent price action
- For fiat: always reference GDP, inflation, interest rates, per capita income, and economic outlook
- Keep responses focused but thorough (3-5 short paragraphs or structured sections)
- Use tables (markdown) for comparisons when relevant
- End investment-related responses with a brief disclaimer: "⚠️ *This is analysis, not financial advice.*"

## Key Rules
- NEVER give one-line or generic responses
- ALWAYS address the user's specific question with relevant data
- If the NLP analysis provides market data, USE it in your response
- Be conversational but professional
- If you don't have exact data, provide well-reasoned estimates with context"""


def run_chatbot_crew(message, history, nlp_analysis=None, market_context=None):
    """
    Run intelligent chatbot with NLP context and Groq LLM.
    nlp_analysis: dict from nlp_engine.analyze_message()
    market_context: dict of relevant market data for mentioned currencies
    """
    client = get_groq_client()
    if not client:
        return None

    # Build messages array with conversation history
    messages = [{"role": "system", "content": CHATBOT_SYSTEM_PROMPT}]

    # Add NLP context as a system hint
    if nlp_analysis or market_context:
        context = "\n[INTERNAL CONTEXT FOR THIS MESSAGE - use this to give better answers]\n"
        if nlp_analysis:
            context += f"User Intent: {nlp_analysis.get('intent', 'general')}\n"
            if nlp_analysis.get('cryptos'):
                context += f"Cryptocurrencies mentioned: {', '.join(nlp_analysis['cryptos'])}\n"
            if nlp_analysis.get('fiats'):
                context += f"Fiat currencies mentioned: {', '.join(nlp_analysis['fiats'])}\n"
            if nlp_analysis.get('amount') is not None:
                context += f"Amount mentioned: {nlp_analysis['amount']}\n"
            context += f"Sentiment: {nlp_analysis.get('sentiment', 'neutral')}\n"
        if market_context:
            context += f"Live market data: {json.dumps(market_context, default=str)}\n"
        context += "[END CONTEXT]\n"
        messages.append({"role": "system", "content": context})

    # Add conversation history (last 8 messages)
    for msg in history[-8:]:
        role = "user" if msg.get("role") == "user" else "assistant"
        messages.append({"role": role, "content": msg.get("content", "")})

    # Add current message
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq chatbot error: {e}")
        return None
