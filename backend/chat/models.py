"""
Database models for the `chat` application.

This file defines the data schema for storing usage logs of AI interactions
and includes a helper method to simplify creating new log entries without
disrupting the main application flow.
"""

from django.db import models


class UsageLog(models.Model):
    """
    Represents a record of a usage event in the system, storing details about
    the prompt, tokens used, potential content filtering, and more.

    Attributes:
        timestamp (DateTimeField): The time this record was created (auto-populated).
        user_identifier (CharField): Optionally store user ID or some user reference (if applicable).
        thread_id (CharField): A unique ID for the conversation thread (UUID or string).
        model (CharField): The AI model used, e.g., "gpt-4o" or "gpt-4o-mini".
        temperature (FloatField): The temperature setting used for the AI request.
        prompt_text (TextField): The user's text prompt.
        ai_response (TextField): The full response from the OpenAI model.
        token_usage (IntegerField): Total tokens used in the AI response.
        stop_reason (CharField): Why the AI response ended, e.g., "length", "user", "content_filter".
        error (TextField): Any error messages encountered during the request.
        content_filter_result (TextField): Info about content filtering from Azure (if provided).
    """

    timestamp = models.DateTimeField(
        auto_now_add=True, help_text="The time when this log record was created."
    )

    user_identifier = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="An optional identifier for the user who made the request.",
    )

    thread_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        help_text="A unique thread ID that identifies a conversation.",
    )

    model = models.CharField(
        max_length=50, help_text="The AI model name, e.g., 'gpt-4o' or 'gpt-4o-mini'."
    )

    temperature = models.FloatField(
        help_text="The temperature setting used for this request."
    )

    prompt_text = models.TextField(help_text="The prompt text sent by the user.")

    ai_response = models.TextField(
        null=True, blank=True, help_text="The full response from the OpenAI model."
    )

    stop_reason = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="The stop reason returned by the AI, if any.",
    )

    error = models.TextField(
        null=True,
        blank=True,
        help_text="Details of any error encountered during the request.",
    )

    def __str__(self) -> str:
        """
        Returns a user-friendly string representation of this log entry.

        Returns:
            str: A string showing model name, timestamp, thread_id, and user_identifier if present.
        """
        user_part = f" | user: {self.user_identifier}" if self.user_identifier else ""
        thread_part = f" | thread: {self.thread_id}" if self.thread_id else ""
        return f"UsageLog({self.model} @ {self.timestamp}{thread_part}{user_part})"

    @classmethod
    def log_interaction(
        cls,
        user_identifier: str | None,
        model: str,
        temperature: float,
        prompt_text: str,
        ai_response: str | None = None,
        stop_reason: str | None = None,
        error: str | None = None,
        thread_id: str | None = None,
    ) -> None:
        """
        A convenience method to log a new usage event without interrupting
        the main request flow if an error occurs.

        Args:
            user_identifier (str | None): Optional identifier for the user requesting the model.
            model (str): The AI model used (e.g., 'gpt-4o' or 'gpt-4o-mini').
            temperature (float): The temperature setting for this request.
            prompt_text (str): The text prompt that was sent to the AI model.
            ai_response (str | None): The text response from the AI model, if any.
            stop_reason (str | None): Reason the AI response ended (e.g., 'length', 'user').
            error (str | None): Any error message encountered during the request (if any).
            thread_id (str | None): Identifier for the conversation thread.
        """
        try:
            cls.objects.create(
                user_identifier=user_identifier,
                model=model,
                temperature=temperature,
                prompt_text=prompt_text,
                ai_response=ai_response,
                stop_reason=stop_reason,
                error=error,
                thread_id=thread_id,
            )
        except Exception as e:
            # We do not raise the error further because we don't want to crash
            # the main application flow just due to a logging failure.
            # Instead, we could add a logger.warning or logger.error message here.
            pass
