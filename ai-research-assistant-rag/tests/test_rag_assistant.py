import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))
from src.rag_assistant import ResearchAssistant, chunk_text


class ChunkingTests(unittest.TestCase):
    def test_empty_text_returns_no_chunks(self):
        self.assertEqual(chunk_text("  \n  "), [])

    def test_long_text_is_split_with_overlap(self):
        text = " ".join(f"token{i}" for i in range(300))
        chunks = chunk_text(text, chunk_size=120, overlap=20)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 120 for chunk in chunks))
        self.assertTrue(all(chunks[i].split()[-1] == chunks[i + 1].split()[0]
                            for i in range(len(chunks) - 1)))


class RetrievalTests(unittest.TestCase):
    def test_retrieves_relevant_passage_with_source_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "retrieval.md").write_text(
                "TF-IDF retrieval ranks text passages by lexical overlap with a query. "
                "Source citations help readers check the evidence.", encoding="utf-8"
            )
            (root / "gardening.txt").write_text(
                "Tomatoes need sunlight, water and well-drained soil to grow well.", encoding="utf-8"
            )
            assistant = ResearchAssistant(root, chunk_size=400, overlap=30)
            results = assistant.retrieve("How does TF-IDF rank text passages?", top_k=2)
            self.assertTrue(results)
            self.assertIn("retrieval.md", results[0].source)
            self.assertGreater(results[0].score, 0)

    def test_unknown_query_returns_no_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "one.txt").write_text("Cellular respiration converts nutrients into usable energy.", encoding="utf-8")
            assistant = ResearchAssistant(root)
            self.assertEqual(assistant.retrieve("quasar telescope nebula", top_k=3), [])

    def test_answer_includes_citation_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence.txt").write_text(
                "Retrieval augmented generation connects a language model with retrieved external context.", encoding="utf-8"
            )
            assistant = ResearchAssistant(root)
            result = assistant.answer("What does retrieval augmented generation connect?", use_llm=False)
            self.assertIn("[S1]", result["answer"])
            self.assertEqual(result["mode"], "local extractive retrieval")

    def test_empty_directory_is_handled(self):
        with tempfile.TemporaryDirectory() as tmp:
            assistant = ResearchAssistant(Path(tmp) / "empty")
            result = assistant.answer("Any question", use_llm=False)
            self.assertEqual(result["sources"], [])
            self.assertIn("couldn't find", result["answer"])


if __name__ == "__main__":
    unittest.main()
