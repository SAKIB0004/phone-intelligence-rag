from typing import Dict, Generator, Tuple
from app.agents.review_agent import ReviewGenerationAgent
from app.agents.spec_agent import SpecRetrievalAgent
from app.utils.logger import logger


class SamsungReviewOrchestrator:

    def __init__(self):
        self.spec_agent = SpecRetrievalAgent()
        self.review_agent = ReviewGenerationAgent()

    def stream_phone_review(self, phone_name, review_focus = "Comprehensive Assessment"):
        """Core method: Retrieves specs and yields review tokens in real time."""
        logger.info(f"Starting review stream for: {phone_name}")

        spec_dossier = self.spec_agent.run(f"Retrieve full technical specifications for Samsung {phone_name}")
        review_stream = self.review_agent.stream_review(spec_dossier=spec_dossier, focus_instructions=review_focus)

        return spec_dossier, review_stream

    def generate_phone_review(self, phone_name, review_focus = "Comprehensive Assessment"):
        """Convenience wrapper for tests, APIs, and batch tasks."""
        spec_dossier, review_stream = self.stream_phone_review(phone_name=phone_name, review_focus=review_focus)

        full_review = "".join(review_stream)

        return {
            "phone_name": phone_name,
            "technical_dossier": spec_dossier,
            "final_review": full_review,
        }