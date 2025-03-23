"""Unit tests for the llm_helpers module.

Tests include:
    - num_tokens_from_messages: Tests token counting for different message types and models.
    - truncate_messages_to_token_limit: Tests message truncation logic to fit within model limits.
            
Notes:
        - Uses unittest.mock to patch external dependencies like tiktoken.
        - Tests both normal operation and edge cases like empty message lists.
"""

import unittest
from unittest.mock import MagicMock, patch

from ..utils.llm_helpers import (
        num_tokens_from_messages,
        truncate_messages_to_token_limit,
        FALLBACK_MODEL,
)


class MockMessage:
        """A mock message class for testing."""
        
        def __init__(self, content=None, role=None):
                self.content = content
                self.role = role
                
        def __class__(self):
                # For testing SystemMessage detection
                class_mock = MagicMock()
                class_mock.__name__ = self.role if self.role else "HumanMessage"
                return class_mock


class TestLLMHelpers(unittest.TestCase):
        """Test cases for the LLM helper functions."""
        
        @patch("chat.utils.llm_helpers.tiktoken")
        def test_num_tokens_from_messages_with_content(self, mock_tiktoken):
                """Test token counting for messages with content."""
                # Set up the mock
                mock_encoding = MagicMock()
                # Fix: Return a list with length equal to the number of tokens we want to simulate
                # "Hello, world!" -> 13 chars
                # "This is a test message." -> 23 chars (not 24, there's no trailing space)
                mock_encoding.encode.side_effect = lambda text: [0] * len(text)
                mock_tiktoken.encoding_for_model.return_value = mock_encoding
                
                # Create test messages
                messages = [
                        MockMessage(content="Hello, world!"),
                        MockMessage(content="This is a test message.")
                ]
                
                # Calculate tokens
                result = num_tokens_from_messages(messages, "gpt-4o-mini-2024-07-18")
                
                # Verify results - correct the expected value to 13 + 23 = 36
                self.assertEqual(result, 36)  # Length of both message contents
                mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o-mini-2024-07-18")
                self.assertEqual(mock_encoding.encode.call_count, 2)

        @patch("chat.utils.llm_helpers.tiktoken")
        def test_num_tokens_from_messages_without_content(self, mock_tiktoken):
                """Test token counting for messages without content attribute."""
                # Set up the mock
                mock_encoding = MagicMock()
                mock_encoding.encode.side_effect = lambda text: [0] * len(text)
                mock_tiktoken.encoding_for_model.return_value = mock_encoding
                
                # Create test messages, one with content and one without
                class MessageWithoutContent:
                        pass
                        
                messages = [
                        MockMessage(content="Hello, world!"),
                        MessageWithoutContent()
                ]
                
                # Calculate tokens
                result = num_tokens_from_messages(messages, "gpt-4o-mini-2024-07-18")
                
                # Verify only the message with content was counted
                self.assertEqual(result, 13)
                self.assertEqual(mock_encoding.encode.call_count, 1)

        @patch("chat.utils.llm_helpers.tiktoken")
        def test_num_tokens_from_messages_fallback_encoding(self, mock_tiktoken):
                """Test token counting with fallback encoding when model is not found."""
                # Set up the mock to raise KeyError for the specific model
                mock_encoding = MagicMock()
                mock_encoding.encode.side_effect = lambda text: [0] * len(text)
                mock_tiktoken.encoding_for_model.side_effect = KeyError("Model not found")
                mock_tiktoken.get_encoding.return_value = mock_encoding
                
                # Create test message
                messages = [MockMessage(content="Hello, world!")]
                
                # Calculate tokens
                result = num_tokens_from_messages(messages, "non-existent-model")
                
                # Verify fallback encoding was used
                self.assertEqual(result, 13)
                mock_tiktoken.get_encoding.assert_called_with("o200k_base")
                
        @patch("chat.utils.llm_helpers.tiktoken")
        def test_num_tokens_from_messages_empty_list(self, mock_tiktoken):
                """Test token counting with an empty message list."""
                # Set up the mock
                mock_encoding = MagicMock()
                mock_tiktoken.encoding_for_model.return_value = mock_encoding
                
                # Calculate tokens with empty list
                result = num_tokens_from_messages([], "gpt-4o-mini-2024-07-18")
                
                # Verify result is zero and encode was not called
                self.assertEqual(result, 0)
                mock_encoding.encode.assert_not_called()

        @patch("chat.utils.llm_helpers.tiktoken")
        def test_num_tokens_from_messages_default_model(self, mock_tiktoken):
                """Test token counting with the default model."""
                # Set up the mock
                mock_encoding = MagicMock()
                mock_encoding.encode.side_effect = lambda text: [0] * len(text)
                mock_tiktoken.encoding_for_model.return_value = mock_encoding
                
                # Create test message
                messages = [MockMessage(content="Hello, world!")]
                
                # Calculate tokens without specifying model (should use default)
                result = num_tokens_from_messages(messages)
                
                # Verify default model was used
                mock_tiktoken.encoding_for_model.assert_called_with(FALLBACK_MODEL)
                self.assertEqual(result, 13)


if __name__ == "__main__":
        unittest.main()