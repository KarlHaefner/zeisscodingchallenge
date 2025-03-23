/**
 * @file useChatState.ts
 * @description
 *   Custom React hook that manages the complete chat application state.
 *   Handles message history, API interactions, model selection, and PDF viewer integration.
 *
 * @features
 *   - Message submission and streaming response handling
 *   - Thread-based conversation management with unique IDs
 *   - Model selection and temperature adjustment
 *   - PDF viewer state integration
 *   - Error handling and recovery
 *   - Optimistic UI updates for improved responsiveness
 * 
 * @dependencies
 *   - React for state management through useState and useCallback
 *   - Browser's crypto API for UUID generation
 *   - Fetch API for backend communication
 * 
 * @implementation
 *   The hook maintains local state for UI display while sending only the latest message
 *   to the backend along with thread_id, model, and temperature parameters. The backend
 *   manages the full conversation history, and responses are streamed back to provide
 *   incremental updates to the UI.
 *
 * @notes
 *   - Uses thread_id (sent as conversationId internally) for backend conversation tracking
 *   - Implements streaming text responses with TextDecoder for incremental updates
 *   - Handles PDF viewer integration through currentPdfEntry state
 */

import { useState, useCallback } from 'react';

// API base URL constant to avoid hardcoding throughout the component
const API_BASE_URL = "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ModelConfig {
  deployment_name: string;
  display_name: string;
  model_name: string;
  model_token_limit: number;
  output_token_limit: number;
}

export function useChatState() {
  // Using conversationId for thread identification; will be sent as "thread_id" to the backend.
  const [conversationId, setConversationId] = useState<string>(() => crypto.randomUUID());
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [messageInput, setMessageInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [temperature, setTemperature] = useState<number>(0.3);
  const [models, setModels] = useState<ModelConfig[]>([]);
  
  // New state for managing the currently selected PDF entry (from arXiv)
  const [currentPdfEntry, setCurrentPdfEntry] = useState<string | null>(null);

  /**
   * Clears the entire conversation and generates a new thread ID.
   */
  const handleNewChat = useCallback((): void => {
    setMessages([]);
    setConversationId(crypto.randomUUID());
    // Reset the current PDF entry when starting a new chat
    setCurrentPdfEntry(null);
  }, []);

  /**
   * Handles submission of a new user message and streams the response.
   * In this updated version, only the latest user message is sent to the backend
   * along with thread_id, model, and temperature. The full conversation is managed
   * on the backend, while local state is used only for display.
   *
   * @param event - Form event from the message input form.
   */
  const handleSubmit = useCallback(async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    const userText = messageInput.trim();
    if (!userText) {
      console.log("No message to send.");
      return;
    }

    // Create a user message object for local display
    const userMsg: ChatMessage = {
      role: "user",
      content: userText
    };

    // Placeholder for the assistant's response
    const assistantMsg: ChatMessage = {
      role: "assistant",
      content: ""
    };

    // Reset the input and indicate that streaming is in progress
    setMessageInput("");
    setIsStreaming(true);

    // Optimistically update local state with the new user message and an empty assistant message
    setMessages((prev) => [...prev, userMsg, assistantMsg]);

    try {
      // Send only the latest user message along with the necessary metadata.
      // The backend will use "thread_id" to manage the conversation history.
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: conversationId,
          model: selectedModel,
          temperature: temperature,
          message: userText
        })
      });

      if (!response.ok || !response.body) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      // Read the streamed data from the response
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      // Append partial tokens to the assistant message as they arrive
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        // Decode the current chunk of bytes
        const partialText = decoder.decode(value, { stream: true });

        // Check for a stream completion signal "[DONE]"
        if (partialText === "[DONE]") {
          break;
        }

        // Update the assistant's message with the new partial text
        setMessages((prevMessages) => {
          const assistantIndex = prevMessages.length - 1;
          if (assistantIndex >= 0 && prevMessages[assistantIndex].role === 'assistant') {
            const updated = [...prevMessages];
            updated[assistantIndex] = {
              ...updated[assistantIndex],
              content: updated[assistantIndex].content + partialText
            };
            return updated;
          }
          return prevMessages;
        });
      }
    } catch (err) {
      console.error("Streaming error:", err);
      const errorText = "An error occurred. Please try again later.";
      
      // Display a fallback error message in the assistant bubble
      setMessages((prevMessages) => {
        const assistantIndex = prevMessages.length - 1;
        if (assistantIndex >= 0 && prevMessages[assistantIndex].role === 'assistant') {
          const updated = [...prevMessages];
          updated[assistantIndex] = {
            ...updated[assistantIndex],
            content: errorText
          };
          return updated;
        }
        return prevMessages;
      });
    } finally {
      setIsStreaming(false);
    }
  }, [conversationId, messageInput, selectedModel, temperature]);

  /**
   * Fetches available model configurations from the backend.
   */
  const fetchModels = useCallback(async () => {
    try {
      const resp = await fetch(`${API_BASE_URL}/api/model-config/`);
      if (!resp.ok) {
        throw new Error(`Failed to fetch models: ${resp.status} ${resp.statusText}`);
      }
      const data = await resp.json();
      setModels(data.models);
      
      // If models exist and none is selected, set the first one as default.
      if (data.models?.length > 0 && !selectedModel) {
        setSelectedModel(data.models[0].deployment_name);
      }
    } catch (error) {
      console.error("Error fetching model config:", error);
    }
  }, [selectedModel]);

  return {
    conversationId,
    messages,
    messageInput,
    setMessageInput,
    isStreaming,
    selectedModel,
    setSelectedModel,
    temperature,
    setTemperature,
    models,
    handleNewChat,
    handleSubmit,
    fetchModels,
    // New PDF viewer state variables
    currentPdfEntry,
    setCurrentPdfEntry,
  };
}

export default useChatState;
