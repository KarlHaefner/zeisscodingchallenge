"""
This module contains the view classes for handling chat interactions and additional features
such as PDF retrieval for the ChallengeChat application.

It includes:
- ChatStreamView: Streams chat responses from the LLM.
- ModelConfigView: Returns the model configuration.
- PdfView: A new view to download and serve PDFs from arXiv.
"""

import traceback
from typing import Generator

from django.http import FileResponse, JsonResponse, StreamingHttpResponse
from django.conf import settings
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UsageLog
from .serializers import ChatRequestSerializer
from .services.arxiv_service import ArxivService
from .services.llm_service import LLMService
from .utils.llm_helpers import load_model_config


# Decorate methods for tool calling as tools
@tool
def search_arxiv(query: str) -> str:
    """Search the arXiv database for papers matching the given query.

    Args:
        query: The search query string.

    Returns:
        str: JSON string with search results.
    """
    return ArxivService.search(query)


@tool
def summarize_papers_for_conversation(entry_ids_to_summarize: list[str], chat_summarization: str, user_question: str) -> str:
    """Summarizes up to three arXiv papers with context from the current conversation.
    
    Fetches each paper's content, processes it, and produces summaries focused on the user's
    current question, considering the conversation context.
    
    Args:
        entry_ids_to_summarize: List of arXiv paper IDs (e.g., ["2403.12345v1", "2406.67890v1"]). Should have a max length of 3.
        chat_summarization: A summary of the chat history so far to provide context.
        user_question: The current question from the user to focus the summaries on.
        
    Returns:
        str: JSON string containing summaries for each paper keyed by their IDs.
    """
    return ArxivService.summarize_papers(entry_ids_to_summarize, chat_summarization, user_question)


@tool
def fetch_content_from_arxiv_paper(entry_id: str) -> str:
    """Fetches an arXiv paper using the API, downloads the PDF, extracts text, and returns data as JSON.
    
    Args:
        entry_id: The arXiv paper ID (e.g., "2403.12345v1").
        
    Returns:
        str: JSON string with paper content.
    """
    return ArxivService.fetch_paper_content(entry_id)


class ChatStreamView(APIView):
    """ChatStreamView handles chat requests by receiving a minimal payload from the frontend,
    invoking the LangChain pipeline for processing, and streaming token-by-token responses
    back to the client. It also logs the usage of the conversation using the provided thread_id.
    """

    def post(self, request, *args, **kwargs) -> StreamingHttpResponse:
        """Processes a chat request and returns a streaming response.
        
        Args:
            request: The HTTP request object containing chat data.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            StreamingHttpResponse: A streaming response with chat tokens.
        """
        # Validate request data
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        thread_id = serializer.validated_data["thread_id"]
        deployment_name = serializer.validated_data["model"]
        temperature = serializer.validated_data["temperature"]
        user_message = serializer.validated_data["message"]

        # Create input message
        input_messages = [HumanMessage(content=user_message)]

        # Define tools
        # See README.md for more information on the tools used in the workflow
        use_summarization = settings.USE_SUMMARIZATION
        if use_summarization:
            tools = [search_arxiv, summarize_papers_for_conversation]
        else:
            tools = [search_arxiv, fetch_content_from_arxiv_paper]


        # Set up LLM and workflow
        llm = LLMService.create_llm(deployment_name, temperature)
        app = LLMService.create_chat_workflow(llm, tools, use_summarization)

        # Stream generator function
        def stream_generator() -> Generator[str, None, None]:
            """Generates a stream of response tokens from the LLM.
            
            Yields:
                str: Response tokens.
            """
            ai_response = ""
            stop_reason = None
            error_message = None

            try:
                # Generate streaming response
                for content, metadata in LLMService.generate_stream(
                    app, input_messages, thread_id
                ):
                    ai_response += content
                    stop_reason = metadata.get("finish_reason")
                    yield content

            except Exception as exc:
                error_message = str(exc)
                yield "An internal error occurred. Please try again later."
            finally:
                # Log the interaction after streaming is complete
                try:
                    UsageLog.log_interaction(
                        user_identifier=None,  # No authentication for MVP
                        model=deployment_name,
                        temperature=float(temperature),
                        prompt_text=user_message,
                        ai_response=ai_response,
                        stop_reason=stop_reason,
                        error=error_message,
                        thread_id=thread_id,
                    )
                except Exception:
                    # Logging errors should not break the main flow
                    traceback.print_exc()

        return StreamingHttpResponse(
            stream_generator(), content_type="text/event-stream"
        )


class ModelConfigView(APIView):
    """Returns the model configuration as a JSON response."""

    def get(self, request):
        """Handles GET requests for model configuration.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            JsonResponse: The model configuration.
        """
        config_data = load_model_config()
        return JsonResponse(config_data)


class PdfView(APIView):
    """PdfView handles the retrieval of PDF files for arXiv papers.

    This view:
    - Accepts GET requests with an 'entry_id' parameter.
    - Calls the ArxivService.download_and_store_pdf to download and save the PDF.
    - Returns the stored PDF file as a FileResponse with content type 'application/pdf'.

    Error Handling:
    - If the PDF cannot be retrieved or an error occurs, returns a JSON error response.
    """

    def get(self, request, entry_id: str, *args, **kwargs):
        """Handles GET requests for PDF retrieval.
        
        Args:
            request: The HTTP request object.
            entry_id: The arXiv paper ID.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            FileResponse: The PDF file if successful.
            JsonResponse: An error message if unsuccessful.
        """
        try:
            # Download and store the PDF using the provided entry_id
            pdf_path = ArxivService.download_and_store_pdf(entry_id)
            # Open the PDF file in binary mode and return as a FileResponse
            return FileResponse(open(pdf_path, "rb"), content_type="application/pdf")
        except Exception as e:
            # Return a JSON response with an error message if something goes wrong
            return JsonResponse({"error": str(e)}, status=400)
