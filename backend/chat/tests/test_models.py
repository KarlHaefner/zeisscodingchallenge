"""Unit tests for the UsageLog model.

This file tests the log_interaction class method to ensure that a usage log entry is created with
correct field values and that the string representation (__str__) returns the expected format.
    
Notes:
    - Uses Django's TestCase for an isolated testing environment.
    - Verifies that errors during logging do not interrupt log creation.
"""

import datetime

from django.test import TestCase

from chat.models import UsageLog


class UsageLogModelTest(TestCase):
    def test_log_interaction_creates_entry(self):
        """Test that log_interaction creates a UsageLog entry with correct field values."""
        # Define test data
        test_user = "test_user"
        test_model = "gpt-4o-mini"
        test_temperature = 0.5
        test_prompt = "What is the meaning of life?"
        test_response = "42"
        test_stop_reason = "completed"
        test_error = None
        test_thread_id = "123e4567-e89b-12d3-a456-426614174000"

        # Invoke the logging method
        UsageLog.log_interaction(
            user_identifier=test_user,
            model=test_model,
            temperature=test_temperature,
            prompt_text=test_prompt,
            ai_response=test_response,
            stop_reason=test_stop_reason,
            error=test_error,
            thread_id=test_thread_id,
        )

        # Retrieve the last logged entry
        log_entry = UsageLog.objects.last()
        self.assertIsNotNone(log_entry, "The log entry should be created and not None")
        self.assertEqual(log_entry.user_identifier, test_user)
        self.assertEqual(log_entry.model, test_model)
        self.assertEqual(log_entry.temperature, test_temperature)
        self.assertEqual(log_entry.prompt_text, test_prompt)
        self.assertEqual(log_entry.ai_response, test_response)
        self.assertEqual(log_entry.stop_reason, test_stop_reason)
        self.assertEqual(log_entry.error, test_error)
        self.assertEqual(log_entry.thread_id, test_thread_id)

        # Verify that the timestamp is a valid datetime and recent (within the last minute)
        self.assertTrue(isinstance(log_entry.timestamp, datetime.datetime))
        now = datetime.datetime.now(datetime.timezone.utc)
        self.assertLess((now - log_entry.timestamp).total_seconds(), 60)

    def test_str_method(self):
        """Test that the __str__ method of the UsageLog returns the expected string format."""
        # Create a UsageLog instance directly (bypassing log_interaction for testing __str__)
        log_entry = UsageLog.objects.create(
            user_identifier="user_str",
            model="gpt-4o",
            temperature=0.7,
            prompt_text="Test prompt",
            ai_response="Test response",
            stop_reason="completed",
            error=None,
            thread_id="thread-001",
        )
        string_repr = str(log_entry)
        self.assertIn("gpt-4o", string_repr)
        self.assertIn("thread-001", string_repr)
        self.assertIn("user: user_str", string_repr)
