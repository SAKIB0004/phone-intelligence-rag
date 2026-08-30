from typing import Dict, Generator, List

from app.rag.groq_client import GroqLLMClient
from app.rag.prompts import QA_PROMPT_TEMPLATE, SYSTEM_PROMPT
from app.rag.retriever import SamsungRAGRetriever
from app.utils.logger import logger


class SamsungChatEngine:

    def __init__(self):
        self.retriever = SamsungRAGRetriever()
        self.llm = GroqLLMClient()
        self.history: List[Dict[str, str]] = []
        self._initialize_index()

    def _initialize_index(self):
        """Auto-index on engine startup if not already indexed."""
        try:
            count = self.retriever.index_database(force_refresh=False)
            logger.info(f"ChatEngine ready with {count} indexed devices.")
        except Exception as e:
            logger.error(f"Error during index initialization: {e}")

    def reset_chat(self):
        """Reset conversation memory."""
        self.history = []

    def answer_query_stream(
        self, user_query: str
    ) -> Generator[str, None, None]:
        """Retrieve dynamic DB specs and stream the conversational answer."""
        # 1. Fetch relevant specs via RAG
        context = self.retriever.retrieve(user_query, top_k=4)

        # 2. Construct dynamic prompt
        formatted_user_prompt = QA_PROMPT_TEMPLATE.format(
            context=context, query=user_query
        )

        # 3. Assemble chat payload with conversation memory
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Append previous turns (keep last 6 turns for context budget)
        for msg in self.history[-6:]:
            messages.append(msg)

        messages.append({"role": "user", "content": formatted_user_prompt})

        # 4. Stream response and capture full reply for memory
        full_reply = []
        for chunk in self.llm.stream_response(messages):
            full_reply.append(chunk)
            yield chunk

        # 5. Persist to conversational history
        complete_text = "".join(full_reply)
        self.history.append({"role": "user", "content": user_query})
        self.history.append({"role": "assistant", "content": complete_text})