from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.yfinance import YFinanceTools

stock_agent = Agent(
    name="stock_agent",
    role="Analyze stocks, prices, and fundamentals",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[
        YFinanceTools(
            stock_price=True,
            analyst_recommendations=True,
            stock_fundamentals=True,
            company_news=True,
        )
    ],
    instructions=[
        "Use tables to display financial data",
        "Highlight PE ratio, market cap, 52-week high/low",
        "Summarize analyst recommendations clearly",
        "Always include the data source"
    ],
    show_tool_calls=True,
    markdown=True,
)