import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

LLM_MODEL = os.getenv("LLM_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model=LLM_MODEL, temperature=0, api_key=OPENAI_API_KEY)