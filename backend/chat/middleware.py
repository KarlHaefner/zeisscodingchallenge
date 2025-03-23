"""
Middleware for the chat app.
"""


class PdfFrameMiddleware:
    """
    Custom middleware to allow PDF files to be embedded in iframes.
    Removes X-Frame-Options for PDF endpoints and adds proper content headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith("/api/pdf/"):
            # Remove X-Frame-Options header
            if "X-Frame-Options" in response:
                del response["X-Frame-Options"]

            # Set proper Content-Disposition header
            response["Content-Disposition"] = "inline"

            # Add Content-Security-Policy to be more secure than simply removing X-Frame-Options
            response[
                "Content-Security-Policy"
            ] = "frame-ancestors 'self' http://localhost:* http://127.0.0.1:*;"

        return response
