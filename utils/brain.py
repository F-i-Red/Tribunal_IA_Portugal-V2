# utils/brain.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(temperature=0.3, model="openai/gpt-3.5-turbo"):  # <--- ALTERA AQUI
    """Configuração central do LLM via OpenRouter (fácil trocar modelo)."""
    return ChatOpenAI(
        model_name=model,
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Tribunal IA Portugal"
        },
        temperature=temperature,
    )
