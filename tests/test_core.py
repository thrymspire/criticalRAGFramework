import unittest

from core.agent_loader import load_agent
from core.stream_bridge import calculate_entropy
from core.verification import verify_citations


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.retrieved = [{"id": "CHK-ONE"}, {"id": "CHK-TWO"}]

    def test_valid_retrieved_citation_passes(self):
        result = verify_citations("Evidence [CHK-ONE]", self.retrieved)
        self.assertTrue(result["citation_valid"])
        self.assertEqual(result["cited_ids"], ["CHK-ONE"])

    def test_missing_citation_fails_closed(self):
        self.assertFalse(verify_citations("Evidence", self.retrieved)["citation_valid"])

    def test_unknown_citation_fails_closed(self):
        result = verify_citations("Evidence [CHK-NOT-RETRIEVED]", self.retrieved)
        self.assertFalse(result["citation_valid"])
        self.assertEqual(result["unknown_citations"], ["CHK-NOT-RETRIEVED"])


class RuntimeTests(unittest.TestCase):
    def test_agent_loader_requires_no_optional_frontmatter_package(self):
        agent = load_agent("engineer")
        self.assertEqual(agent["name"], "engineer")
        self.assertTrue(agent["system_prompt"])

    def test_entropy_math(self):
        self.assertAlmostEqual(calculate_entropy([{"prob": 0.5}, {"prob": 0.25}, {"prob": 0.25}]), 1.5)


class ServerDefaultsTests(unittest.TestCase):
    def test_server_is_loopback_by_default(self):
        from core.server import start_harness_server
        import inspect
        self.assertEqual(inspect.signature(start_harness_server).parameters["host"].default, "127.0.0.1")

    def test_chat_endpoint_does_not_call_missing_method(self):
        from pathlib import Path
        source = Path("core/server.py").read_text(encoding="utf-8")
        self.assertNotIn("orchestrator.step(", source)
