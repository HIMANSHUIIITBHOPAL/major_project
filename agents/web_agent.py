from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo

web_agent = Agent(
    name="web_agent",
    role="Search the web for latest stock news and market updates",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[DuckDuckGo()],
    instructions=[
        "Always include sources and URLs",
        "Focus on financial and market news",
        "Be concise and structured"
    ],
    show_tool_calls=True,
    markdown=True,
)