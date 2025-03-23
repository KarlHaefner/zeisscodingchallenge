"""
URL configuration for the `chat` app.

This file maps URL paths to view classes/functions within the `chat` application.
"""

from django.urls import path

from .views import ChatStreamView, ModelConfigView, PdfView

urlpatterns = [
    path("chat/stream", ChatStreamView.as_view(), name="chat_stream"),
    path("model-config/", ModelConfigView.as_view(), name="model-config"),
    path("pdf/<str:entry_id>/", PdfView.as_view(), name="pdf_viewer"),
]
