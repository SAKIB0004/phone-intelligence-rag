import unittest
from app.agents.tools import get_phone_specs_from_db, list_available_phones
from app.agents.workflow import SamsungReviewOrchestrator


class TestMultiAgentSystem(unittest.TestCase):

    def test_list_available_phones_tool(self):
        result = list_available_phones.invoke({})
        self.assertIn("available_phones", result)

    def test_spec_tool_lookup(self):
        result = get_phone_specs_from_db.invoke({"model_name": "Galaxy S23"})
        self.assertTrue(len(result) > 0)

    def test_orchestrator_pipeline(self):
        orchestrator = SamsungReviewOrchestrator()
        result = orchestrator.generate_phone_review(
            phone_name="Galaxy S23",
            review_focus="Performance and Battery Focus",
        )
        self.assertIn("technical_dossier", result)
        self.assertIn("final_review", result)
        self.assertTrue(len(result["final_review"]) > 100)


if __name__ == "__main__":
    unittest.main()