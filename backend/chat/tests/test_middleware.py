"""
Unit tests for the PdfFrameMiddleware middleware in the chat application.

These tests simulate requests passing through the middleware to verify that:
- The X-Frame-Options header is removed for requests to /api/pdf/
- The Content-Disposition header is set to 'inline'
- The Content-Security-Policy header is added with the proper value
Also, tests verify that requests that do not target /api/pdf/ remain unchanged.

Usage:
    Run the tests using Django's test runner:
    python manage.py test chat.tests.test_middleware
"""

from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from chat.middleware import PdfFrameMiddleware


class DummyView:
    """A dummy view to simulate a basic HTTP response.
    
    This view returns an HttpResponse with a preset X-Frame-Options header,
    which should be removed by the middleware for PDF requests.
    """

    def __call__(self, request):
        response = HttpResponse("Dummy content")
        # Initially set the X-Frame-Options header to simulate a restrictive setting.
        response["X-Frame-Options"] = "DENY"
        return response


class PdfFrameMiddlewareTest(TestCase):
    """Test cases for PdfFrameMiddleware."""

    def setUp(self):
        """Initialize the RequestFactory and the middleware instance with the dummy view."""
        self.factory = RequestFactory()
        self.dummy_view = DummyView()
        self.middleware = PdfFrameMiddleware(get_response=self.dummy_view)

    def test_middleware_modifies_pdf_path(self):
        """Verify that the middleware correctly modifies headers for PDF paths.
        
        The middleware should:
          - Remove the X-Frame-Options header
          - Set the Content-Disposition header to 'inline'
          - Add the correct Content-Security-Policy header
        """
        # Create a GET request with path matching /api/pdf/
        request = self.factory.get("/api/pdf/test-entry/")
        response = self.middleware(request)

        # X-Frame-Options should be removed by the middleware.
        self.assertNotIn("X-Frame-Options", response)
        # Check that Content-Disposition is set to 'inline'.
        self.assertEqual(response.get("Content-Disposition"), "inline")
        # Check that the Content-Security-Policy header is correctly set.
        expected_csp = "frame-ancestors 'self' http://localhost:* http://127.0.0.1:*;"
        self.assertEqual(response.get("Content-Security-Policy"), expected_csp)

    def test_middleware_does_not_modify_non_pdf_path(self):
        """Verify that the middleware does not modify headers for non-PDF paths."""
        # Create a GET request with a non-PDF path.
        request = self.factory.get("/api/other/test-entry/")
        response = self.middleware(request)

        # X-Frame-Options should remain as set by the dummy view.
        self.assertEqual(response.get("X-Frame-Options"), "DENY")
        # The middleware should not add Content-Disposition or Content-Security-Policy headers.
        self.assertIsNone(response.get("Content-Disposition"))
        self.assertIsNone(response.get("Content-Security-Policy"))
