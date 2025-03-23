"""
File: test_views.py
Description:
    Unit tests for the view endpoints in the chat application.
    This file tests:
    - ChatStreamView: Ensures that a valid POST request returns a streaming response and logs the interaction.
    - ModelConfigView: Verifies that a GET request returns model configuration data.
    - PdfView: Checks both successful PDF retrieval and error handling when a PDF cannot be found.
Author: ChatGPT
Date: 2025-03-13
"""

import json
import os
import tempfile
from unittest.mock import patch

from django.test import Client, TestCase

from chat.models import UsageLog


class ChatStreamViewTest(TestCase):
    """Test cases for the ChatStreamView endpoint.
    
    Simulates POST requests to test streaming responses and logging behavior.
    """

    def setUp(self):
        """Set up the test client and the URL for ChatStreamView."""
        self.client = Client()
        # ChatStreamView is available at /api/chat/stream as per urls.py
        self.url = "/api/chat/stream"
        self.payload = {
            "thread_id": "test-thread-1",
            "model": "gpt-4o",
            "temperature": 0.5,
            "message": "Hello, AI!",
        }

    @patch("chat.services.llm_service.LLMService.generate_stream")
    @patch("chat.models.UsageLog.log_interaction")
    def test_chat_stream_view_success(self, mock_log_interaction, mock_generate_stream):
        """Test ChatStreamView with a valid POST request.
        
        The LLMService.generate_stream is patched to yield a simulated streaming response.
        Verifies that the streaming response contains the expected content and that 
        logging is invoked.
        """
        # Define a fake stream generator function to simulate a streaming response.
        def fake_stream(app, input_messages, thread_id):
            yield ("Test streaming response", {})

        mock_generate_stream.side_effect = fake_stream

        response = self.client.post(
            self.url, data=json.dumps(self.payload), content_type="application/json"
        )

        # Verify that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)
        # Verify that the response is a StreamingHttpResponse with streaming_content attribute.
        self.assertTrue(hasattr(response, "streaming_content"))
        # Collect all the streaming content and decode it.
        content = b"".join(list(response.streaming_content)).decode("utf-8")
        self.assertIn("Test streaming response", content)

        # Check that the logging method was called after streaming.
        self.assertTrue(
            mock_log_interaction.called,
            "UsageLog.log_interaction should be called to log the interaction",
        )

    def test_chat_stream_view_invalid_payload(self):
        """Test ChatStreamView with an invalid payload (missing required fields).
        
        Expects a 400 response with appropriate error messages.
        """
        invalid_payload = {
            # Missing 'thread_id' and 'message'
            "model": "gpt-4o",
            "temperature": 0.5,
        }
        response = self.client.post(
            self.url, data=json.dumps(invalid_payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("thread_id", data)
        self.assertIn("message", data)


class ModelConfigViewTest(TestCase):
    """Test cases for the ModelConfigView endpoint.
    
    Verifies that a GET request returns model configuration data in JSON format.
    """

    def setUp(self):
        """Set up the test client and the URL for ModelConfigView."""
        self.client = Client()
        self.url = "/api/model-config/"

    def test_model_config_view(self):
        """Test that a GET request to ModelConfigView returns expected data.
        
        Verifies that the response has a 200 status and contains 'models' in the JSON data.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("models", data)


class PdfViewTest(TestCase):
    """Test cases for the PdfView endpoint.
    
    Tests both the success scenario where a PDF is successfully retrieved and 
    the failure scenario where an error occurs.
    """

    def setUp(self):
        """Set up the test client and URL for PdfView."""
        self.client = Client()
        self.entry_id = "test-entry"
        self.url = f"/api/pdf/{self.entry_id}/"

    @patch("chat.services.arxiv_service.ArxivService.download_and_store_pdf")
    def test_pdf_view_success(self, mock_download_pdf):
        """Test PdfView for a successful PDF retrieval.
        
        Patches ArxivService.download_and_store_pdf to return the path of a temporary PDF file.
        Verifies that the response is served as a PDF.
        """
        # Create a temporary PDF file with minimal PDF header and content.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(b"%PDF-1.4 test pdf content")
            tmp_pdf_path = tmp_pdf.name

        # Patch the download method to return the temporary file path.
        mock_download_pdf.return_value = tmp_pdf_path

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get("Content-Type"), "application/pdf")

        # Read from streaming_content instead of content
        content = b"".join(response.streaming_content)
        self.assertTrue(content.startswith(b"%PDF-1.4"))

        # Close the response to release the file handle
        response.close()

        # Clean up the temporary file after we're done with the response
        os.unlink(tmp_pdf_path)

    @patch("chat.services.arxiv_service.ArxivService.download_and_store_pdf")
    def test_pdf_view_failure(self, mock_download_pdf):
        """Test PdfView for the error scenario.
        
        Patches ArxivService.download_and_store_pdf to raise an exception.
        Expects a JSON error response with a 400 status code.
        """
        mock_download_pdf.side_effect = Exception("PDF not found")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "PDF not found")
