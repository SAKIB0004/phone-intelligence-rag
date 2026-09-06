from typing import Dict, List


class ConversationMemory:
	"""Store the recent chat messages included in the next prompt."""

	def __init__(self, max_messages: int = 6):
		self.max_messages = max_messages
		self._messages: List[Dict[str, str]] = []

	def clear(self) -> None:
		"""Remove all conversation history."""
		self._messages.clear()

	def recent_messages(self) -> List[Dict[str, str]]:
		"""Return a copy of the recent messages for prompt construction."""
		return list(self._messages[-self.max_messages :])

	def add_turn(self, user_query: str, assistant_response: str) -> None:
		"""Append one completed user/assistant exchange."""
		self._messages.extend(
			[
				{"role": "user", "content": user_query},
				{"role": "assistant", "content": assistant_response},
			]
		)
