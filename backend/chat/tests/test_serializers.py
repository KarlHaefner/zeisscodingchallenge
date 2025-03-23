"""Unit tests for serializers in the chat app.

This file tests:
  - ChatRequestSerializer: Ensuring it validates correct payloads and rejects incorrect ones.
  - UsageLogSerializer: Confirming that a UsageLog instance is correctly serialized into JSON.
    
Notes:
    - Uses Django's TestCase for an isolated testing environment.
    - Ensures that error messages are generated for missing required fields in ChatRequestSerializer.
"""

from django.test import TestCase

from chat.models import UsageLog
from chat.serializers import ChatRequestSerializer, UsageLogSerializer


class ChatRequestSerializerTest(TestCase):
    def test_valid_data(self):
        """Test that the ChatRequestSerializer validates correct data."""
        valid_data = {
            "thread_id": "thread-123",
            "model": "gpt-4o",
            "temperature": 0.3,
            "message": "Hello, world!",
        }
        serializer = ChatRequestSerializer(data=valid_data)
        self.assertTrue(
            serializer.is_valid(), "Serializer should be valid with proper data"
        )
        self.assertEqual(serializer.validated_data["thread_id"], "thread-123")
        self.assertEqual(serializer.validated_data["model"], "gpt-4o")
        self.assertEqual(serializer.validated_data["temperature"], 0.3)
        self.assertEqual(serializer.validated_data["message"], "Hello, world!")

    def test_invalid_data(self):
        """Test that the ChatRequestSerializer returns errors for invalid/missing data."""
        invalid_data = {
            "model": "gpt-4o",
            "temperature": 0.3,
            # Missing 'thread_id' and 'message'
        }
        serializer = ChatRequestSerializer(data=invalid_data)
        self.assertFalse(
            serializer.is_valid(),
            "Serializer should be invalid if required fields are missing",
        )
        self.assertIn("thread_id", serializer.errors)
        self.assertIn("message", serializer.errors)


class UsageLogSerializerTest(TestCase):
    def test_serialization(self):
        """Test that UsageLogSerializer correctly serializes a UsageLog instance."""
        # Create a UsageLog instance
        usage_log = UsageLog.objects.create(
            user_identifier="test_user",
            model="gpt-4o",
            temperature=0.5,
            prompt_text="Test prompt for serialization",
            ai_response="Test AI response",
            stop_reason="completed",
            error=None,
            thread_id="thread-456",
        )
        serializer = UsageLogSerializer(instance=usage_log)
        data = serializer.data

        # Verify that all fields are correctly serialized
        self.assertEqual(data["user_identifier"], "test_user")
        self.assertEqual(data["model"], "gpt-4o")
        self.assertEqual(float(data["temperature"]), 0.5)
        self.assertEqual(data["prompt_text"], "Test prompt for serialization")
        self.assertEqual(data["ai_response"], "Test AI response")
        self.assertEqual(data["stop_reason"], "completed")
        self.assertEqual(data["error"], None)
        self.assertEqual(data["thread_id"], "thread-456")
        # Check that a timestamp is present in the serialized data
        self.assertIn("timestamp", data)
