import unittest

from answer_question import find_relevant_sections
from model_client import call_model
from read_markdown import load_markdown
from split_markdown import split_by_headings


class PipelineTests(unittest.TestCase):
    def setUp(self):
        markdown = load_markdown("sample_notes.md")
        self.sections = split_by_headings(markdown)

    def test_markdown_is_split_into_three_sections(self):
        self.assertEqual(len(self.sections), 3)

    def test_section_titles(self):
        titles = [
            section["title"]
            for section in self.sections
        ]

        self.assertEqual(
            titles,
            ["HTTP", "JSON", "RAG"],
        )

    def test_find_rag_section(self):
        results = find_relevant_sections(
            self.sections,
            "RAG 的基本流程是什么？",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "RAG")

    def test_unknown_topic_returns_empty_list(self):
        results = find_relevant_sections(
            self.sections,
            "Docker 是什么？",
        )

        self.assertEqual(results, [])

    def test_empty_prompt_is_rejected(self):
        with self.assertRaises(ValueError):
            call_model("")


if __name__ == "__main__":
    unittest.main()