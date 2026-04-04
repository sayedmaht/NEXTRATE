"""
NextRate AI - Real-time Currency Converter Backend
Flask server with Gemma 4 AI agents (Groq-powered) + NLP for intelligent chatbot.
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from agents import run_prediction_crew, run_chatbot_crew
from nlp_engine import analyze_message, build_context_prompt

app = Flask(__name__)
CORS(app)

# ─── Configuration ───────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
EXCHANGERATE_BASE = "https://open.er-api.com/v6"

# ─── In-Memory Cache ─────────────────────────────────────────────────────────
cache = {}
CACHE_TTL = 300  # 5 minutes


def get_cached(key):
    if key in cache and time.time() - cache[key]["ts"] < CACHE_TTL:
        return cache[key]["data"]
    return None


def set_cache(key, data):
    cache[key] = {"data": data, "ts": time.time()}


# ═══════════════════════════════════════════════════════════════════════════════
# FIAT CURRENCIES DATA
# ═══════════════════════════════════════════════════════════════════════════════

FIAT_CURRENCIES = [
    {"code": "USD", "name": "US Dollar", "country": "United States", "symbol": "$", "flag": "🇺🇸"},
    {"code": "EUR", "name": "Euro", "country": "Eurozone", "symbol": "€", "flag": "🇪🇺"},
    {"code": "GBP", "name": "British Pound", "country": "United Kingdom", "symbol": "£", "flag": "🇬🇧"},
    {"code": "JPY", "name": "Japanese Yen", "country": "Japan", "symbol": "¥", "flag": "🇯🇵"},
    {"code": "AUD", "name": "Australian Dollar", "country": "Australia", "symbol": "A$", "flag": "🇦🇺"},
    {"code": "CAD", "name": "Canadian Dollar", "country": "Canada", "symbol": "C$", "flag": "🇨🇦"},
    {"code": "CHF", "name": "Swiss Franc", "country": "Switzerland", "symbol": "CHF", "flag": "🇨🇭"},
    {"code": "CNY", "name": "Chinese Yuan", "country": "China", "symbol": "¥", "flag": "🇨🇳"},
    {"code": "INR", "name": "Indian Rupee", "country": "India", "symbol": "₹", "flag": "🇮🇳"},
    {"code": "MXN", "name": "Mexican Peso", "country": "Mexico", "symbol": "$", "flag": "🇲🇽"},
    {"code": "BRL", "name": "Brazilian Real", "country": "Brazil", "symbol": "R$", "flag": "🇧🇷"},
    {"code": "KRW", "name": "South Korean Won", "country": "South Korea", "symbol": "₩", "flag": "🇰🇷"},
    {"code": "SGD", "name": "Singapore Dollar", "country": "Singapore", "symbol": "S$", "flag": "🇸🇬"},
    {"code": "HKD", "name": "Hong Kong Dollar", "country": "Hong Kong", "symbol": "HK$", "flag": "🇭🇰"},
    {"code": "NOK", "name": "Norwegian Krone", "country": "Norway", "symbol": "kr", "flag": "🇳🇴"},
    {"code": "SEK", "name": "Swedish Krona", "country": "Sweden", "symbol": "kr", "flag": "🇸🇪"},
    {"code": "DKK", "name": "Danish Krone", "country": "Denmark", "symbol": "kr", "flag": "🇩🇰"},
    {"code": "NZD", "name": "New Zealand Dollar", "country": "New Zealand", "symbol": "NZ$", "flag": "🇳🇿"},
    {"code": "ZAR", "name": "South African Rand", "country": "South Africa", "symbol": "R", "flag": "🇿🇦"},
    {"code": "RUB", "name": "Russian Ruble", "country": "Russia", "symbol": "₽", "flag": "🇷🇺"},
    {"code": "TRY", "name": "Turkish Lira", "country": "Turkey", "symbol": "₺", "flag": "🇹🇷"},
    {"code": "PLN", "name": "Polish Zloty", "country": "Poland", "symbol": "zł", "flag": "🇵🇱"},
    {"code": "THB", "name": "Thai Baht", "country": "Thailand", "symbol": "฿", "flag": "🇹🇭"},
    {"code": "IDR", "name": "Indonesian Rupiah", "country": "Indonesia", "symbol": "Rp", "flag": "🇮🇩"},
    {"code": "MYR", "name": "Malaysian Ringgit", "country": "Malaysia", "symbol": "RM", "flag": "🇲🇾"},
    {"code": "PHP", "name": "Philippine Peso", "country": "Philippines", "symbol": "₱", "flag": "🇵🇭"},
    {"code": "CZK", "name": "Czech Koruna", "country": "Czech Republic", "symbol": "Kč", "flag": "🇨🇿"},
    {"code": "ILS", "name": "Israeli Shekel", "country": "Israel", "symbol": "₪", "flag": "🇮🇱"},
    {"code": "CLP", "name": "Chilean Peso", "country": "Chile", "symbol": "$", "flag": "🇨🇱"},
    {"code": "PEN", "name": "Peruvian Sol", "country": "Peru", "symbol": "S/.", "flag": "🇵🇪"},
    {"code": "COP", "name": "Colombian Peso", "country": "Colombia", "symbol": "$", "flag": "🇨🇴"},
    {"code": "SAR", "name": "Saudi Riyal", "country": "Saudi Arabia", "symbol": "﷼", "flag": "🇸🇦"},
    {"code": "AED", "name": "UAE Dirham", "country": "UAE", "symbol": "د.إ", "flag": "🇦🇪"},
    {"code": "EGP", "name": "Egyptian Pound", "country": "Egypt", "symbol": "£", "flag": "🇪🇬"},
    {"code": "NGN", "name": "Nigerian Naira", "country": "Nigeria", "symbol": "₦", "flag": "🇳🇬"},
    {"code": "KES", "name": "Kenyan Shilling", "country": "Kenya", "symbol": "KSh", "flag": "🇰🇪"},
    {"code": "GHS", "name": "Ghanaian Cedi", "country": "Ghana", "symbol": "₵", "flag": "🇬🇭"},
    {"code": "PKR", "name": "Pakistani Rupee", "country": "Pakistan", "symbol": "₨", "flag": "🇵🇰"},
    {"code": "BDT", "name": "Bangladeshi Taka", "country": "Bangladesh", "symbol": "৳", "flag": "🇧🇩"},
    {"code": "VND", "name": "Vietnamese Dong", "country": "Vietnam", "symbol": "₫", "flag": "🇻🇳"},
    {"code": "HUF", "name": "Hungarian Forint", "country": "Hungary", "symbol": "Ft", "flag": "🇭🇺"},
    {"code": "RON", "name": "Romanian Leu", "country": "Romania", "symbol": "lei", "flag": "🇷🇴"},
    {"code": "BGN", "name": "Bulgarian Lev", "country": "Bulgaria", "symbol": "лв", "flag": "🇧🇬"},
    {"code": "HRK", "name": "Croatian Kuna", "country": "Croatia", "symbol": "kn", "flag": "🇭🇷"},
    {"code": "ISK", "name": "Icelandic Krona", "country": "Iceland", "symbol": "kr", "flag": "🇮🇸"},
    {"code": "UAH", "name": "Ukrainian Hryvnia", "country": "Ukraine", "symbol": "₴", "flag": "🇺🇦"},
    {"code": "ARS", "name": "Argentine Peso", "country": "Argentina", "symbol": "$", "flag": "🇦🇷"},
    {"code": "TWD", "name": "Taiwan Dollar", "country": "Taiwan", "symbol": "NT$", "flag": "🇹🇼"},
    {"code": "QAR", "name": "Qatari Riyal", "country": "Qatar", "symbol": "﷼", "flag": "🇶🇦"},
    {"code": "KWD", "name": "Kuwaiti Dinar", "country": "Kuwait", "symbol": "د.ك", "flag": "🇰🇼"},
    {"code": "BHD", "name": "Bahraini Dinar", "country": "Bahrain", "symbol": ".د.ب", "flag": "🇧🇭"},
    {"code": "OMR", "name": "Omani Rial", "country": "Oman", "symbol": "﷼", "flag": "🇴🇲"},
    {"code": "JOD", "name": "Jordanian Dinar", "country": "Jordan", "symbol": "د.ا", "flag": "🇯🇴"},
    {"code": "LKR", "name": "Sri Lankan Rupee", "country": "Sri Lanka", "symbol": "₨", "flag": "🇱🇰"},
    {"code": "MAD", "name": "Moroccan Dirham", "country": "Morocco", "symbol": "د.م.", "flag": "🇲🇦"},
    {"code": "TND", "name": "Tunisian Dinar", "country": "Tunisia", "symbol": "د.ت", "flag": "🇹🇳"},
]

# Economic indicators for fiat predictions (reference data for AI context)
FIAT_ECONOMICS = {
    "USD": {"gdp_growth": 2.5, "inflation": 3.2, "per_capita": 76330, "debt_gdp": 123},
    "EUR": {"gdp_growth": 1.2, "inflation": 2.4, "per_capita": 38230, "debt_gdp": 85},
    "GBP": {"gdp_growth": 1.4, "inflation": 4.0, "per_capita": 46510, "debt_gdp": 101},
    "JPY": {"gdp_growth": 1.0, "inflation": 3.3, "per_capita": 33950, "debt_gdp": 263},
    "INR": {"gdp_growth": 7.2, "inflation": 5.5, "per_capita": 2410, "debt_gdp": 83},
    "CNY": {"gdp_growth": 5.2, "inflation": 0.2, "per_capita": 12720, "debt_gdp": 77},
    "AUD": {"gdp_growth": 1.5, "inflation": 3.6, "per_capita": 65100, "debt_gdp": 52},
    "CAD": {"gdp_growth": 1.1, "inflation": 2.8, "per_capita": 52960, "debt_gdp": 107},
    "CHF": {"gdp_growth": 0.7, "inflation": 1.4, "per_capita": 93260, "debt_gdp": 41},
    "BRL": {"gdp_growth": 2.9, "inflation": 4.6, "per_capita": 8920, "debt_gdp": 74},
    "KRW": {"gdp_growth": 1.4, "inflation": 3.6, "per_capita": 32250, "debt_gdp": 54},
    "MXN": {"gdp_growth": 3.2, "inflation": 4.7, "per_capita": 10940, "debt_gdp": 53},
    "SGD": {"gdp_growth": 1.1, "inflation": 4.8, "per_capita": 65230, "debt_gdp": 134},
    "TRY": {"gdp_growth": 4.5, "inflation": 64.8, "per_capita": 10670, "debt_gdp": 32},
    "ZAR": {"gdp_growth": 0.6, "inflation": 5.4, "per_capita": 6010, "debt_gdp": 73},
    "RUB": {"gdp_growth": 3.6, "inflation": 7.4, "per_capita": 12580, "debt_gdp": 17},
}


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Pages
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Crypto API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/crypto/list")
def crypto_list():
    """Get top 120 cryptocurrencies with market data."""
    cached = get_cached("crypto_list")
    if cached:
        return jsonify(cached)

    try:
        resp = requests.get(
            f"{COINGECKO_BASE}/coins/markets",
            params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 120,
                "page": 1,
                "sparkline": True,
                "price_change_percentage": "1h,24h,7d",
            },
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            result = []
            for coin in data:
                result.append({
                    "id": coin.get("id"),
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name"),
                    "image": coin.get("image"),
                    "current_price": coin.get("current_price", 0),
                    "market_cap": coin.get("market_cap", 0),
                    "market_cap_rank": coin.get("market_cap_rank", 0),
                    "total_volume": coin.get("total_volume", 0),
                    "price_change_24h": coin.get("price_change_percentage_24h", 0),
                    "price_change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
                    "circulating_supply": coin.get("circulating_supply", 0),
                    "total_supply": coin.get("total_supply", 0),
                    "max_supply": coin.get("max_supply"),
                    "ath": coin.get("ath", 0),
                    "atl": coin.get("atl", 0),
                    "sparkline": coin.get("sparkline_in_7d", {}).get("price", []),
                })
            set_cache("crypto_list", result)
            # Also update chatbot's market data cache
            global cryptoData_cache
            cryptoData_cache = result
            return jsonify(result)
        else:
            return jsonify({"error": "CoinGecko API error", "status": resp.status_code}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/crypto/<coin_id>/history")
def crypto_history(coin_id):
    """Get 30-day price history for a cryptocurrency."""
    days = request.args.get("days", "30")
    cache_key = f"crypto_history_{coin_id}_{days}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)

    try:
        resp = requests.get(
            f"{COINGECKO_BASE}/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            prices = [{"date": p[0], "price": p[1]} for p in data.get("prices", [])]
            set_cache(cache_key, prices)
            return jsonify(prices)
        else:
            return jsonify({"error": "CoinGecko API error"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Fiat API
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/fiat/rates")
def fiat_rates():
    """Get all fiat exchange rates relative to USD."""
    cached = get_cached("fiat_rates")
    if cached:
        return jsonify(cached)

    try:
        resp = requests.get(f"{EXCHANGERATE_BASE}/latest/USD", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            rates = data.get("rates", {})
            result = []
            for cur in FIAT_CURRENCIES:
                code = cur["code"]
                rate = rates.get(code, 1.0)
                result.append({
                    **cur,
                    "rate": rate,
                    "price_usd": round(1.0 / rate, 6) if rate > 0 else 0,
                })
            set_cache("fiat_rates", result)
            return jsonify(result)
        else:
            return jsonify({"error": "ExchangeRate API error"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/fiat/history/<base_currency>/<target_currency>")
def fiat_history(base_currency, target_currency):
    """Get real historical exchange rates for a fiat pair using ExchangeRate API."""
    cache_key = f"fiat_history_{base_currency}_{target_currency}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached)

    prices = []
    now = datetime.now()

    # Fetch real historical rates for each day from the API
    for i in range(30, -1, -1):
        date = now - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        try:
            resp = requests.get(
                f"{EXCHANGERATE_BASE}/historical/{date_str}/{base_currency}",
                timeout=10,
            )
            if resp.status_code == 200:
                rate = resp.json().get("rates", {}).get(target_currency)
                if rate is not None:
                    prices.append({
                        "date": int(date.timestamp() * 1000),
                        "price": round(rate, 6),
                    })
        except Exception:
            continue

    # If historical API returned no data, fallback to current rate as single point
    if not prices:
        try:
            resp = requests.get(f"{EXCHANGERATE_BASE}/latest/{base_currency}", timeout=15)
            if resp.status_code == 200:
                rate = resp.json().get("rates", {}).get(target_currency, 1.0)
                prices.append({
                    "date": int(now.timestamp() * 1000),
                    "price": round(rate, 6),
                })
        except Exception:
            return jsonify({"error": "Could not fetch exchange rate data"}), 502

    set_cache(cache_key, prices)
    return jsonify(prices)


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Converter
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/convert")
def convert():
    """Convert between any two currencies (fiat or crypto).
    
    Strategy: Convert FROM currency → USD → TO currency.
    - from_price_usd = how much 1 unit of FROM costs in USD
    - to_price_usd = how much 1 unit of TO costs in USD
    - rate = from_price_usd / to_price_usd
    """
    from_c = request.args.get("from", "USD").upper()
    to_c = request.args.get("to", "EUR").upper()
    amount = float(request.args.get("amount", 1))

    fiat_codes = [c["code"] for c in FIAT_CURRENCIES]
    from_is_fiat = from_c in fiat_codes
    to_is_fiat = to_c in fiat_codes

    try:
        # === CASE 1: Fiat → Fiat (direct API) ===
        if from_is_fiat and to_is_fiat:
            resp = requests.get(f"{EXCHANGERATE_BASE}/latest/{from_c}", timeout=10)
            if resp.status_code == 200:
                rates = resp.json().get("rates", {})
                rate = rates.get(to_c, 1)
                return jsonify({
                    "from": from_c, "to": to_c,
                    "amount": amount, "rate": round(rate, 8),
                    "result": round(amount * rate, 6)
                })

        # === CASE 2: Involves at least one crypto ===
        # Step A: Get FROM price in USD
        from_price_usd = 1.0  # Default for USD
        if not from_is_fiat:
            from_price_usd = _get_crypto_price_usd(from_c)
        elif from_c != "USD":
            from_price_usd = _get_fiat_price_usd(from_c)

        # Step B: Get TO price in USD
        to_price_usd = 1.0  # Default for USD
        if not to_is_fiat:
            to_price_usd = _get_crypto_price_usd(to_c)
        elif to_c != "USD":
            to_price_usd = _get_fiat_price_usd(to_c)

        # Step C: Calculate rate (how many TO units you get per 1 FROM unit)
        if to_price_usd > 0:
            rate = from_price_usd / to_price_usd
        else:
            rate = 0

        return jsonify({
            "from": from_c, "to": to_c,
            "amount": amount, "rate": round(rate, 8),
            "result": round(amount * rate, 6)
        })

    except Exception as e:
        print(f"Conversion error: {e}")
        return jsonify({"error": str(e)}), 500


def _get_crypto_price_usd(symbol):
    """Get the USD price of a crypto from cache or CoinGecko API."""
    # Try cache first (from the crypto list endpoint)
    for coin in cryptoData_cache:
        if coin.get("symbol", "").upper() == symbol:
            return coin.get("current_price", 0) or 0

    # Fallback: search CoinGecko
    try:
        search_resp = requests.get(
            f"{COINGECKO_BASE}/search",
            params={"query": symbol}, timeout=10,
        )
        if search_resp.status_code == 200:
            for coin in search_resp.json().get("coins", []):
                if coin.get("symbol", "").upper() == symbol:
                    price_resp = requests.get(
                        f"{COINGECKO_BASE}/simple/price",
                        params={"ids": coin["id"], "vs_currencies": "usd"},
                        timeout=10,
                    )
                    if price_resp.status_code == 200:
                        return price_resp.json().get(coin["id"], {}).get("usd", 0)
                    break
    except Exception:
        pass
    return 0


def _get_fiat_price_usd(currency_code):
    """Get how much 1 unit of a fiat currency is worth in USD."""
    try:
        resp = requests.get(f"{EXCHANGERATE_BASE}/latest/USD", timeout=10)
        if resp.status_code == 200:
            rates = resp.json().get("rates", {})
            fiat_per_usd = rates.get(currency_code, 1)
            # rates gives "how many FIAT per 1 USD", so invert:
            # 1 unit of FIAT = 1/fiat_per_usd USD
            return 1.0 / fiat_per_usd if fiat_per_usd > 0 else 0
    except Exception:
        pass
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — AI Prediction
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/predict", methods=["POST"])
def predict():
    """Generate AI prediction using Gemma 4 Prediction Agent."""
    data = request.json or {}
    currency = data.get("currency", "")
    currency_type = data.get("type", "crypto")  # crypto or fiat
    current_price = data.get("current_price", 0)
    market_data = data.get("market_data", {})

    # Try Gemma 4 Prediction Agent first
    econ_data = FIAT_ECONOMICS.get(currency, {}) if currency_type == "fiat" else None
    result = run_prediction_crew(currency, currency_type, current_price, market_data, econ_data)
    if result:
        return jsonify(result)

    # AI prediction unavailable
    return jsonify({"error": "AI prediction is currently unavailable. Please ensure the Groq API key is configured."}), 503


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTES — Chatbot (NLP-Enhanced + Groq)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/api/chat", methods=["POST"])
def chat():
    """AI chatbot with NLP intent detection and Gemma 4 agent (Groq-powered)."""
    data = request.json or {}
    message = data.get("message", "")
    history = data.get("history", [])

    # Step 1: NLP Analysis — understand intent, extract entities
    nlp_analysis = analyze_message(message)
    print(f"NLP Analysis: intent={nlp_analysis['intent']}, cryptos={nlp_analysis['cryptos']}, fiats={nlp_analysis['fiats']}, sentiment={nlp_analysis['sentiment']}")

    # Step 2: Gather relevant market data for mentioned currencies
    market_context = {}
    try:
        # If user mentioned crypto, fetch live data
        if nlp_analysis['cryptos'] and cryptoData_cache:
            for symbol in nlp_analysis['cryptos'][:3]:  # max 3 to avoid overload
                coin = next((c for c in cryptoData_cache if c.get('symbol') == symbol), None)
                if coin:
                    market_context[symbol] = {
                        "price": coin.get('current_price'),
                        "market_cap": coin.get('market_cap'),
                        "24h_change": coin.get('price_change_24h'),
                        "volume": coin.get('total_volume'),
                        "rank": coin.get('market_cap_rank'),
                    }
        # If user mentioned fiat, include economic data
        if nlp_analysis['fiats']:
            for code in nlp_analysis['fiats'][:3]:
                econ = FIAT_ECONOMICS.get(code, {})
                if econ:
                    market_context[code] = econ
    except Exception:
        pass

    # Step 3: Run Gemma 4 Chatbot Agent with NLP context
    result = run_chatbot_crew(message, history, nlp_analysis, market_context)
    if result and not str(result).startswith("ERROR:"):
        return jsonify({"response": result, "nlp": {"intent": nlp_analysis['intent'], "entities": nlp_analysis['all_currencies']}})

    # Show actual error to help debug
    error_detail = str(result).replace("ERROR: ", "") if result else "Groq API key not configured"
    return jsonify({"response": f"⚠️ AI Error: {error_detail}", "nlp": {"intent": nlp_analysis['intent'], "entities": nlp_analysis['all_currencies']}})


# Simple cache for sharing crypto data with chat
cryptoData_cache = []


# ═══════════════════════════════════════════════════════════════════════════════
# Run
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n🚀 NextRate AI Server Starting...")
    print(f"   Groq API: {'✅ Configured' if GROQ_API_KEY else '⚠️  Not set — AI features disabled'}")
    print(f"   NLP Engine: Intent Classification + Entity Extraction")
    print(f"   Gemma 4 Agents: Prediction Specialist, Chatbot Assistant")
    print(f"   Open: http://localhost:5000\n")
    app.run(debug=True, port=5000)
