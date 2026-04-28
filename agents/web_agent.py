import os
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from pydantic import model_validator


class WebAgent(Agent):
    """Web agent with Groq + DuckDuckGo search."""

    @model_validator(mode="after")
    def _validate_groq_key(self) -> "WebAgent":
        """
        Pydantic v2 model_validator (post-init callback).
        Eagerly validates GROQ_API_KEY and pushes it into the Groq model.
        """
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError(
                "GROQ_API_KEY environment variable is not set. "
                "Add it in Render → Environment → GROQ_API_KEY."
            )
        if self.model is not None:
            self.model.api_key = key  # type: ignore[attr-defined]
        return self


web_agent = WebAgent(
    name="web_agent",
    role="Search the web for latest stock news and market updates",
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[DuckDuckGo()],
    instructions=[
        "Always include sources and URLs",
        "Focus on financial and market news",
        "Be concise and structured",
    ],
    show_tool_calls=True,
    markdown=True,
)