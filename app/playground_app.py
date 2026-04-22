import phi
from phi.playground import Playground, serve_playground_app

from agents.stock_agent import stock_agent
from agents.web_agent import web_agent
from core.config import PHI_API_KEY

phi.api = PHI_API_KEY

app = Playground(
    agents=[stock_agent, web_agent]
).get_app()

if __name__ == "__main__":
    serve_playground_app("app.playground_app:app", reload=True)