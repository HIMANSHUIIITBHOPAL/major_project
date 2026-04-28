"""
YFinanceCachedTools — drop-in replacement for phi's YFinanceTools.

Fixes:
  - Adds retry with exponential backoff for Yahoo Finance 429 / "Too Many Requests"
  - Sets a browser-like User-Agent so Yahoo Finance doesn't block the request
  - Caches Ticker objects per symbol to avoid redundant session creation
  - Falls back gracefully with a readable error instead of crashing the agent
  - Strips massive metadata from news articles to prevent LLM token limits
"""

import json
import time
import random
import logging
from functools import wraps
from typing import Optional

import requests as _requests
import yfinance as yf
from phi.tools.yfinance import YFinanceTools

logger = logging.getLogger(__name__)

# Browser-like headers — avoids Yahoo Finance bot detection
_YF_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

_TICKER_CACHE: dict = {}


def _get_ticker(symbol: str) -> yf.Ticker:
    """Return a cached Ticker instance with a real browser User-Agent."""
    symbol = symbol.upper()
    if symbol not in _TICKER_CACHE:
        try:
            s = _requests.Session()
            s.headers.update(_YF_HEADERS)
            _TICKER_CACHE[symbol] = yf.Ticker(symbol, session=s)
        except Exception:
            _TICKER_CACHE[symbol] = yf.Ticker(symbol)
    return _TICKER_CACHE[symbol]


def _retry(max_tries: int = 3, base_delay: float = 2.0):
    """Decorator: retries on rate-limit errors with exponential back-off + jitter."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(self_arg, symbol: str, *args, **kwargs):
            last_exc: Optional[Exception] = None
            for attempt in range(max_tries):
                try:
                    result = fn(self_arg, symbol, *args, **kwargs)
                    # YFinanceTools returns error strings — detect rate-limit text
                    if isinstance(result, str) and (
                        "Too Many Requests" in result or "Rate limited" in result
                    ):
                        raise RuntimeError(result)
                    return result
                except Exception as exc:
                    last_exc = exc
                    if attempt < max_tries - 1:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(
                            "YFinance rate-limited (%s). Retry %d/%d in %.1fs…",
                            exc, attempt + 1, max_tries - 1, delay,
                        )
                        time.sleep(delay)
                        # Evict cached ticker so a fresh session is used
                        _TICKER_CACHE.pop(symbol.upper(), None)
            return (
                f"Yahoo Finance is currently rate-limiting requests for {symbol}. "
                f"Last error: {last_exc}. Please retry in a few seconds."
            )
        return wrapper
    return decorator


class YFinanceCachedTools(YFinanceTools):
    """
    Drop-in replacement for YFinanceTools with:
    - Browser User-Agent to avoid 403/429 from Yahoo Finance
    - Automatic retry (3x) with exponential back-off
    - Graceful error messages instead of crashing the agent
    """

    @_retry(max_tries=3, base_delay=2.0)
    def get_current_stock_price(self, symbol: str) -> str:
        ticker = _get_ticker(symbol)
        try:
            # fast_info is lighter-weight and less prone to rate limits
            price = ticker.fast_info.last_price
        except Exception:
            info = ticker.info
            price = info.get("regularMarketPrice") or info.get("currentPrice")
        return f"{price:.4f}" if price else f"Could not fetch current price for {symbol}"

    @_retry(max_tries=3, base_delay=2.0)
    def get_stock_fundamentals(self, symbol: str) -> str:
        info = _get_ticker(symbol).info
        fundamentals = {
            "symbol": symbol,
            "company_name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("forwardPE", "N/A"),
            "pb_ratio": info.get("priceToBook", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "eps": info.get("trailingEps", "N/A"),
            "beta": info.get("beta", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
        return json.dumps(fundamentals, indent=2)

    @_retry(max_tries=3, base_delay=2.0)
    def get_analyst_recommendations(self, symbol: str) -> str:
        recs = _get_ticker(symbol).recommendations
        if recs is None or recs.empty:
            return f"No analyst recommendations available for {symbol}"
        return recs.tail(10).to_json(orient="index")

    @_retry(max_tries=3, base_delay=2.0)
    def get_company_news(self, symbol: str, num_stories: int = 3) -> str:
        news = _get_ticker(symbol).news
        if not news:
            return f"No recent news found for {symbol}"

        # FIX: Strip massive metadata to save Groq tokens and prevent TPM limits
        clean_news = []
        for n in news[:num_stories]:
            clean_news.append({
                "title": n.get("title", "No Title"),
                "publisher": n.get("publisher", "Unknown"),
                "link": n.get("link", "")
            })

        return json.dumps(clean_news, indent=2)