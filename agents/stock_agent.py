import os
from phi.agent import Agent
from phi.model.groq import Groq
from pydantic import model_validator

# Use our cached/retry-enabled YFinance wrapper instead of the stock phidata one
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from tools.yfinance_cached import YFinanceCachedTools


class StockAgent(Agent):
    """Stock agent with Groq + YFinance tools (rate-limit resilient)."""

    @model_validator(mode="after")
    def _validate_and_inject(self) -> "StockAgent":
        """
        Pydantic v2 model_validator (post-init callback).
        1. Validates GROQ_API_KEY is set — fails fast at startup, not at request time.
        2. Eagerly injects the API key into the Groq model instance.
        """
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. "
                "In Render: Dashboard → your service → Environment → add GROQ_API_KEY."
            )
        if self.model is not None:
            self.model.api_key = key  # type: ignore[attr-defined]
        return self


stock_agent = StockAgent(
    name="stock_agent",
    role="Analyze stocks, prices, and fundamentals",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        YFinanceCachedTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_news=True,
        )
    ],
    instructions=[
        "Use tables to display financial data when data is successfully retrieved.",
        "Highlight PE ratio, market cap, 52-week high/low.",
        "Summarize analyst recommendations clearly.",
        "Always include the data source.",
        "CRITICAL: If you receive an error or rate-limit message from a tool, DO NOT attempt to format it as a table. Simply explain the error to the user in plain text."
    ],
    show_tool_calls=True,
    markdown=True,
)