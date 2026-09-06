from typing import Dict, Generator, List

from groq import Groq

from app.config.settings import settings
from app.utils.logger import logger


class GroqLLMClient:

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def stream_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
    ) -> Generator[str, None, None]:
        """Stream response tokens in real-time."""
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=1024,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            logger.error(f"Groq Streaming Error: {e}")
            yield f"\n[Streaming Error: {str(e)}]"