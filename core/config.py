import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PHI_API_KEY  = os.getenv("PHI_API_KEY")