"""
Unit tests for the LLMService service methods.

Tests include:
  - create_llm: Ensures that an LLM instance is created with the expected parameters.
  - create_chat_workflow: Validates that a chat workflow is created.
  - generate_stream: Simulates a streaming response and verifies that the generator yields correct output.
      
Notes:
    - Uses unittest.mock to patch external calls and dependencies.
    - Avoids making real calls to Azure OpenAI.
"""

import unittest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessageChunk

from chat.services import llm_service
from chat.services.llm_service import LLMService


# Dummy classes and functions to simulate behavior
class DummyAzureChatOpenAI:
    def __init__(
        self,
        azure_endpoint,
        azure_deployment,
        openai_api_version,
        temperature,
        streaming,
    ):
        self.azure_endpoint = azure_endpoint
        self.azure_deployment = azure_deployment
        self.openai_api_version = openai_api_version
        self.temperature = temperature
        self.streaming = streaming

    def bind_tools(self, tools):
        self.tools = tools
        return self

    def invoke(self, prompt):
        return "dummy response"

    def stream(self, input_data, config, stream_mode):
        # Simulate a stream yielding a tuple (content, metadata)
        yield ("Chunk 1", {"dummy": "metadata"})
        yield ("Chunk 2", {"dummy": "metadata"})


class DummyWorkflow:
    def stream(self, input_data, config, stream_mode):
        # Simulate a stream generator for testing generate_stream.
        yield ("Test streaming chunk", {"info": "dummy"})


class TestLLMService(unittest.TestCase):
    @patch("chat.services.llm_service.AzureChatOpenAI", new=DummyAzureChatOpenAI)
    def test_create_llm(self):
        """
        Test that create_llm returns an instance of AzureChatOpenAI with the correct parameters.
        """
        deployment_name = "gpt-4o"
        temperature = 0.6
        llm_instance = LLMService.create_llm(deployment_name, temperature)
        self.assertIsInstance(llm_instance, DummyAzureChatOpenAI)
        self.assertEqual(llm_instance.azure_deployment, deployment_name)
        self.assertEqual(llm_instance.temperature, temperature)
        self.assertTrue(llm_instance.streaming)

    def test_create_chat_workflow(self):
        """
        Test that create_chat_workflow returns a non-null workflow object.
        """
        # Create a dummy LLM instance with bind_tools capability.
        dummy_llm = DummyAzureChatOpenAI(
            "dummy_endpoint", "gpt-4o", "dummy_version", 0.5, True
        )

        # Replace lambda with a proper function that has a docstring
        def dummy_tool(x):
            """A dummy tool function for testing."""
            return x

        tools = [dummy_tool]
        use_summarization = False  # Add the missing argument
        workflow = LLMService.create_chat_workflow(dummy_llm, tools, use_summarization)
        self.assertIsNotNone(workflow)

    def test_generate_stream(self):
        """
        Test that generate_stream yields the expected streaming output.
        """
        # Create a dummy workflow that simulates streaming.
        dummy_workflow = DummyWorkflow()
        # Prepare a dummy input message list and thread_id.
        input_messages = ["Dummy message"]
        thread_id = "dummy-thread"

        # Create a generator function for our mock using the actual AIMessageChunk class
        def mock_stream(*args, **kwargs):
            yield (AIMessageChunk(content="Test streaming chunk"), {"info": "dummy"})

        # Patch with the generator function
        with patch.object(dummy_workflow, "stream", side_effect=mock_stream):
            stream_gen = LLMService.generate_stream(
                dummy_workflow, input_messages, thread_id
            )
            chunks = list(stream_gen)
            self.assertGreater(len(chunks), 0)
            self.assertEqual(
                chunks[0][0], "Test streaming chunk"
            )  # Changed to expect string instead of object
            self.assertEqual(chunks[0][1], {"info": "dummy"})


if __name__ == "__main__":
    unittest.main()
