"""
NextRate AI — NLP Engine
Natural Language Processing for understanding user queries about currencies.
Uses spaCy for entity extraction and custom intent classification.
"""

import re

# ═══════════════════════════════════════════════════════════════════════════════
# Currency Knowledge Base (for NLP entity matching)
# ═══════════════════════════════════════════════════════════════════════════════

CRYPTO_ALIASES = {
    "bitcoin": "BTC", "btc": "BTC",
    "ethereum": "ETH", "eth": "ETH", "ether": "ETH",
    "solana": "SOL", "sol": "SOL",
    "cardano": "ADA", "ada": "ADA",
    "polkadot": "DOT", "dot": "DOT",
    "dogecoin": "DOGE", "doge": "DOGE",
    "shiba": "SHIB", "shib": "SHIB", "shiba inu": "SHIB",
    "ripple": "XRP", "xrp": "XRP",
    "avalanche": "AVAX", "avax": "AVAX",
    "chainlink": "LINK", "link": "LINK",
    "polygon": "MATIC", "matic": "MATIC",
    "litecoin": "LTC", "ltc": "LTC",
    "uniswap": "UNI", "uni": "UNI",
    "tron": "TRX", "trx": "TRX",
    "stellar": "XLM", "xlm": "XLM",
    "cosmos": "ATOM", "atom": "ATOM",
    "near": "NEAR", "near protocol": "NEAR",
    "algorand": "ALGO", "algo": "ALGO",
    "fantom": "FTM", "ftm": "FTM",
    "tether": "USDT", "usdt": "USDT",
    "usdc": "USDC", "usd coin": "USDC",
    "binance coin": "BNB", "bnb": "BNB",
    "pepe": "PEPE",
    "sui": "SUI",
    "aptos": "APT", "apt": "APT",
    "arbitrum": "ARB", "arb": "ARB",
    "optimism": "OP", "op": "OP",
}

FIAT_ALIASES = {
    "dollar": "USD", "us dollar": "USD", "usd": "USD", "american dollar": "USD",
    "euro": "EUR", "eur": "EUR",
    "pound": "GBP", "british pound": "GBP", "sterling": "GBP", "gbp": "GBP",
    "yen": "JPY", "japanese yen": "JPY", "jpy": "JPY",
    "rupee": "INR", "indian rupee": "INR", "inr": "INR",
    "yuan": "CNY", "chinese yuan": "CNY", "renminbi": "CNY", "rmb": "CNY", "cny": "CNY",
    "ruble": "RUB", "russian ruble": "RUB", "rub": "RUB",
    "real": "BRL", "brazilian real": "BRL", "brl": "BRL",
    "won": "KRW", "korean won": "KRW", "krw": "KRW",
    "lira": "TRY", "turkish lira": "TRY", "try": "TRY",
    "peso": "MXN", "mexican peso": "MXN", "mxn": "MXN",
    "rand": "ZAR", "south african rand": "ZAR", "zar": "ZAR",
    "franc": "CHF", "swiss franc": "CHF", "chf": "CHF",
    "canadian dollar": "CAD", "cad": "CAD",
    "australian dollar": "AUD", "aud": "AUD", "aussie dollar": "AUD",
    "dirham": "AED", "uae dirham": "AED", "aed": "AED",
    "riyal": "SAR", "saudi riyal": "SAR", "sar": "SAR",
    "naira": "NGN", "nigerian naira": "NGN", "ngn": "NGN",
    "pkr": "PKR", "pakistani rupee": "PKR",
    "taka": "BDT", "bangladeshi taka": "BDT", "bdt": "BDT",
    "dong": "VND", "vietnamese dong": "VND", "vnd": "VND",
    "baht": "THB", "thai baht": "THB", "thb": "THB",
    "ringgit": "MYR", "malaysian ringgit": "MYR", "myr": "MYR",
    "shekel": "ILS", "israeli shekel": "ILS", "ils": "ILS",
    "dinar": "KWD", "kuwaiti dinar": "KWD", "kwd": "KWD",
}

# ═══════════════════════════════════════════════════════════════════════════════
# Intent Classification
# ═══════════════════════════════════════════════════════════════════════════════

INTENT_PATTERNS = {
    "price_check": [
        r"\b(?:what(?:'?s| is)(?: the)? (?:price|value|cost|rate|worth))",
        r"\b(?:how much (?:is|does|for))",
        r"\b(?:price of|rate of|value of)",
        r"\b(?:current (?:price|rate|value))",
        r"\b(?:what (?:is|are) .+ (?:trading|priced|worth))",
    ],
    "conversion": [
        r"\b(?:convert|exchange|swap|change)\b",
        r"\b(?:how (?:many|much) .+ (?:in|to|for) )",
        r"\b\d+\.?\d*\s*\w+\s+(?:to|in|into)\s+\w+",
        r"\b(?:what(?:'?s| is) \d+ .+ in .+)",
    ],
    "prediction": [
        r"\b(?:predict|prediction|forecast|future|will .+ go (?:up|down))",
        r"\b(?:what will .+ be (?:worth|priced))",
        r"\b(?:where (?:is|will) .+ (?:heading|going))",
        r"\b(?:price (?:target|prediction|forecast))",
        r"\b(?:bull(?:ish)?|bear(?:ish)?|moon|crash|dump|pump)\b",
        r"\b(?:should i (?:buy|sell|invest|hold))",
    ],
    "comparison": [
        r"\b(?:compare|vs|versus|better|difference between)",
        r"\b(?:which (?:is|one) (?:better|stronger|safer))",
        r"\b(?:.+ or .+\?)",
    ],
    "education": [
        r"\b(?:what (?:is|are) (?:a |an )?(?:cryptocurrency|blockchain|defi|nft|staking|mining))",
        r"\b(?:explain|how (?:does|do) .+ work)",
        r"\b(?:what (?:is|are) .+\??$)",
        r"\b(?:tell me about|teach me|learn about)",
        r"\b(?:definition of|meaning of)",
    ],
    "market_analysis": [
        r"\b(?:market (?:cap|analysis|overview|trend|sentiment))",
        r"\b(?:top (?:coins|crypto|currencies|gainers|losers))",
        r"\b(?:best .+ to (?:buy|invest))",
        r"\b(?:market (?:is|looks) (?:good|bad|bullish|bearish))",
        r"\b(?:economy|gdp|inflation|interest rate)",
    ],
    "greeting": [
        r"\b(?:hello|hi|hey|greetings|good (?:morning|afternoon|evening))\b",
        r"\b(?:what(?:'?s| is) up|sup|howdy)\b",
        r"\b(?:how are you|how(?:'?re| are) you doing)\b",
    ],
    "help": [
        r"\b(?:help|what can you do|features|capabilities)\b",
        r"\b(?:how (?:do i|to) use)",
    ],
}


def classify_intent(text):
    """Classify the intent of a user message."""
    text_lower = text.lower().strip()

    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, text_lower):
                score += 1
        if score > 0:
            scores[intent] = score

    if not scores:
        return "general"

    return max(scores, key=scores.get)


# ═══════════════════════════════════════════════════════════════════════════════
# Entity Extraction
# ═══════════════════════════════════════════════════════════════════════════════

def extract_currencies(text):
    """Extract currency mentions from text."""
    text_lower = text.lower()
    found_cryptos = []
    found_fiats = []

    # Check crypto aliases (longest match first)
    for alias in sorted(CRYPTO_ALIASES.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
            symbol = CRYPTO_ALIASES[alias]
            if symbol not in found_cryptos:
                found_cryptos.append(symbol)

    # Check fiat aliases (longest match first)
    for alias in sorted(FIAT_ALIASES.keys(), key=len, reverse=True):
        if re.search(r'\b' + re.escape(alias) + r'\b', text_lower):
            symbol = FIAT_ALIASES[alias]
            if symbol not in found_fiats:
                found_fiats.append(symbol)

    return found_cryptos, found_fiats


def extract_amount(text):
    """Extract numeric amount from text."""
    match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.?\d*)', text)
    if match:
        return float(match.group(1).replace(',', ''))
    return None


def analyze_message(text):
    """
    Full NLP analysis of a user message.
    Returns intent, entities (cryptos, fiats), amount, and sentiment keywords.
    """
    intent = classify_intent(text)
    cryptos, fiats = extract_currencies(text)
    amount = extract_amount(text)

    # Detect sentiment keywords
    positive_words = ["good", "great", "bullish", "moon", "pump", "growth", "strong", "up", "buy", "invest", "best"]
    negative_words = ["bad", "bearish", "crash", "dump", "weak", "down", "sell", "worst", "risk", "danger"]

    text_lower = text.lower()
    sentiment = "neutral"
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"

    return {
        "intent": intent,
        "cryptos": cryptos,
        "fiats": fiats,
        "all_currencies": cryptos + fiats,
        "amount": amount,
        "sentiment": sentiment,
        "original_text": text,
    }


def build_context_prompt(analysis, market_data=None):
    """
    Build a rich context prompt from NLP analysis to feed to the LLM.
    This helps the LLM give much more relevant and specific answers.
    """
    context_parts = []

    context_parts.append(f"User Intent: {analysis['intent']}")

    if analysis['cryptos']:
        context_parts.append(f"Mentioned Cryptocurrencies: {', '.join(analysis['cryptos'])}")
    if analysis['fiats']:
        context_parts.append(f"Mentioned Fiat Currencies: {', '.join(analysis['fiats'])}")
    if analysis['amount'] is not None:
        context_parts.append(f"Amount Mentioned: {analysis['amount']}")
    context_parts.append(f"User Sentiment: {analysis['sentiment']}")

    if market_data:
        context_parts.append(f"\nLive Market Data Available:")
        for key, val in market_data.items():
            context_parts.append(f"  - {key}: {val}")

    return "\n".join(context_parts)
