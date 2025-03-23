"""Unit tests for the ArxivService service methods.

Tests include:
  - search: Verifies that the JSON response contains the expected keys.
  - fetch_paper_content: Uses mocking to bypass actual PDF download and text extraction.
  - download_and_store_pdf: Tests error handling when the paper is not found and the scenario when the PDF file already exists.
      
Notes:
    - Uses unittest.mock to simulate external API calls and file system operations.
    - Ensures that the arXivService methods behave as expected without side effects.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from chat.services import arxiv_service
from chat.services.arxiv_service import ArxivService


class DummyPaper:
    """A dummy paper object to simulate arXiv paper data."""

    def __init__(self):
        self.title = "Dummy Title"
        self.authors = [MagicMock(name="Author One")]
        self.authors[0].name = "Author One"
        self.summary = "This is a dummy abstract."
        self.published = __import__("datetime").datetime(2020, 1, 1)
        self.primary_category = "cs.AI"
        self.categories = ["cs.AI"]
        self.entry_id = "http://arxiv.org/abs/1234.56789v1"
        self.pdf_url = "http://arxiv.org/pdf/1234.56789v1"

    def download_pdf(self, filename: str):
        # Write a minimal PDF header to simulate a download.
        with open(filename, "wb") as f:
            f.write(b"%PDF-1.4 dummy content")


class TestArxivService(unittest.TestCase):
    @patch("chat.services.arxiv_service.arxiv.Client")
    def test_search(self, mock_client_cls):
        """Test the search method of ArxivService by patching arxiv.Client to return a dummy result."""
        # Create a dummy paper and simulate results iterator
        dummy_paper = DummyPaper()
        dummy_iterator = iter([dummy_paper])
        mock_client = MagicMock()
        mock_client.results.return_value = dummy_iterator
        mock_client_cls.return_value = mock_client

        # Call search with a query and parse JSON result
        result_json = ArxivService.search("dummy query", max_results=1)
        results = json.loads(result_json)

        # Verify that the expected keys exist in the result
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 1)
        paper_info = results[0]
        self.assertIn("title", paper_info)
        self.assertIn("authors", paper_info)
        self.assertIn("summary", paper_info)
        self.assertIn("published", paper_info)
        self.assertIn("primary_category", paper_info)
        self.assertIn("entry_id", paper_info)
        self.assertEqual(paper_info["entry_id"], "1234.56789v1")

    @patch("chat.services.arxiv_service.ArxivService._extract_text_from_pdf")
    @patch("chat.services.arxiv_service.arxiv.Search")
    def test_fetch_paper_content(self, mock_search_cls, mock_extract_text):
        """
        Test fetch_paper_content by patching arxiv.Search and _extract_text_from_pdf.
        """
        dummy_paper = DummyPaper()
        dummy_iterator = iter([dummy_paper])
        # Set up the search instance to yield the dummy paper.
        mock_search = MagicMock()
        mock_search.results.return_value = dummy_iterator
        mock_search_cls.return_value = mock_search

        # Patch _extract_text_from_pdf to return dummy content
        dummy_text = {"block_1": "Dummy extracted text"}
        mock_extract_text.return_value = dummy_text

        result_json = ArxivService.fetch_paper_content("1234.56789v1")
        result_data = json.loads(result_json)

        self.assertIn("title", result_data)
        self.assertEqual(result_data["title"], dummy_paper.title)
        self.assertIn("authors", result_data)
        self.assertIn("abstract", result_data)
        self.assertIn("content", result_data)
        self.assertEqual(result_data["content"], dummy_text)
        self.assertIn("file_pointer", result_data)

    @patch("chat.services.arxiv_service.os.path.exists")
    @patch("chat.services.arxiv_service.arxiv.Search")
    def test_download_and_store_pdf_not_found(self, mock_search_cls, mock_exists):
        """
        Test download_and_store_pdf when the paper is not found (should raise ValueError).
        """
        # Simulate that the file does not exist
        mock_exists.return_value = False

        # Setup the search to return no results
        dummy_iterator = iter([])  # empty iterator
        mock_search = MagicMock()
        mock_search.results.return_value = dummy_iterator
        mock_search_cls.return_value = mock_search

        with self.assertRaises(ValueError) as context:
            ArxivService.download_and_store_pdf("non-existent-id")
        self.assertIn("Paper with entry_id", str(context.exception))

    @patch("chat.services.arxiv_service.os.path.exists")
    @patch("chat.services.arxiv_service.arxiv.Search")
    def test_download_and_store_pdf_file_exists(self, mock_search_cls, mock_exists):
        """
        Test download_and_store_pdf when the file already exists (should return the existing file path).
        """
        # Simulate that the file already exists
        mock_exists.return_value = True
        # Construct the expected file path
        expected_file = os.path.join(os.getcwd(), "assets", "1234.56789v1.pdf")

        # Call the method and verify it returns the existing file path
        file_path = ArxivService.download_and_store_pdf("1234.56789v1")
        self.assertEqual(file_path, expected_file)


if __name__ == "__main__":
    unittest.main()
