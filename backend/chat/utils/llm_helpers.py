"""Helper functions for interacting with language models.

This module provides utilities for token counting, model configuration,
and message management to ensure efficient use of LLM context windows.
It includes functions to calculate token counts and truncate messages
as needed to fit within model limits.

Dependencies:
    - tiktoken: For token counting with OpenAI models
    - yaml: For loading model configuration
"""

import os

import tiktoken
import yaml
from django.conf import settings

FALLBACK_MODEL = "gpt-4o-mini-2024-07-18"
FALLBACK_MODEL_TOKEN_LIMIT = 128000
FALLBACK_OUTPUT_TOKEN_LIMIT = 16384


def load_model_config():
    """Loads model configuration from the YAML file.
    
    Returns:
        dict: Dictionary containing model configuration or error message.
    """
    config_path = os.path.join(settings.BASE_DIR, "model_config.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {"error": "Config file not found"}


model_config = load_model_config()
# check if model_config is not empty and does not have the key "error"
if model_config and "error" not in model_config:
    MODEL_CONFIG_LIST = model_config.get("models", [])
else:
    MODEL_CONFIG_LIST = []

# Create a dictionary mapping deployment names to model names and token limits
model_mappings = {
    entry["deployment_name"]: (
        entry["model_name"].lower(),
        entry["model_token_limit"],
        entry["output_token_limit"],
    )
    for entry in MODEL_CONFIG_LIST
}


def num_tokens_from_messages(
    messages: list, model_name: str = FALLBACK_MODEL
) -> int:
    """Calculates the number of tokens in a list of LangChain messages.
    
    This function uses tiktoken to count tokens in the content of each message.
    
    Args:
        messages: List of LangChain message objects.
        model_name: Name of the model to use for token counting.
    
    Returns:
        int: Total number of tokens in the messages.
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        # If model is not found use o200k_base encoding.
        encoding = tiktoken.get_encoding("o200k_base")

    num_tokens = 0
    for message in messages:
        # Count tokens only in message content
        if hasattr(message, 'content'):
            num_tokens += len(encoding.encode(str(message.content)))
    return num_tokens


def truncate_messages_to_token_limit(
    messages: list, deployment_name: str = "gpt-4o-mini-2024-07-18"
) -> list:
    """Truncates messages to fit within the model's token limit.
    
    This function removes older messages (except the system prompt) until
    the total token count plus the expected output tokens fits within
    the model's context window.
    
    Args:
        messages: List of LangChain message objects to potentially truncate.
        deployment_name: The deployment name to determine token limits.
    
    Returns:
        list: A truncated list of messages that fits within the token limit.
    """
    if not messages:
        return messages

    # Get model_name, model_token_limit, and output_token_limit from the deployment_name
    model_name, model_token_limit, output_token_limit = model_mappings.get(
        deployment_name,
        (FALLBACK_MODEL, FALLBACK_MODEL_TOKEN_LIMIT, FALLBACK_OUTPUT_TOKEN_LIMIT),
    )
    
    # Make a copy of messages to avoid modifying the original list
    messages_copy = messages.copy()
    
    messages_tokens = num_tokens_from_messages(messages_copy, model_name)
    
    # Check if the first message is a system message
    is_system_first = False
    if messages_copy and hasattr(messages_copy[0], '__class__'):
        is_system_first = messages_copy[0].__class__.__name__ == 'SystemMessage'
    
    while (messages_tokens + output_token_limit > model_token_limit and len(messages_copy) > 1):
        # Remove the oldest message after the system prompt
        if is_system_first:
            if len(messages_copy) > 1:  # Make sure we have more than just the system message
                messages_copy.pop(1)  # Remove the second message (preserving system message)
        else:
            messages_copy.pop(0)  # If no system message, remove the oldest message
            
        messages_tokens = num_tokens_from_messages(messages_copy, model_name)
        
    return messages_copy
