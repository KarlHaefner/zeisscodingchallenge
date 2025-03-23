/**
 * @file chat-window.tsx
 * @description
 *   Main chat interface component that orchestrates the complete chat experience.
 *   Provides a unified UI combining model selection, message history, and user input.
 *
 * @features
 *   - Model selection with temperature adjustment
 *   - Message history display with automatic scrolling
 *   - Text input with keyboard shortcuts
 *   - Streaming message support
 *   - New chat creation
 * 
 * @dependencies
 *   - React for component architecture and effects
 *   - useChatState: Manages message data, model selection, and API interactions
 *   - useTextareaControl: Handles input focus, keyboard events, and scroll behavior
 *   - ModelControls: UI for model selection and temperature adjustment
 *   - MessageList: Renders conversation history
 *   - MessageInput: Handles user text input and submission
 * 
 * @implementation
 *   The component initializes by fetching available models and setting up
 *   automatic scrolling behavior. It composes the UI from three main sections:
 *   controls at the top, message history in the middle, and input at the bottom.
 */

import React, { useEffect } from "react";
import { useChatState } from "../contexts/ChatStateContext";
import { useTextareaControl } from "../hooks/useTextareaControl";
import ModelControls from "./model-controls";
import MessageList from "./message-list";
import MessageInput from "./message-input";

export default function ChatWindow(): JSX.Element {
  // Extract chat state and handlers from custom hook
  const {
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
  } = useChatState();

  // Extract textarea control logic from custom hook
  const {
    textareaRef,
    messagesContainerRef,
    handleKeyDown,
    scrollToBottom,
  } = useTextareaControl(messageInput, handleSubmit, isStreaming);

  // Fetch models on component mount
  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <div className="flex flex-col w-full h-full p-4">
      <ModelControls
        selectedModel={selectedModel}
        setSelectedModel={setSelectedModel}
        models={models}
        temperature={temperature}
        setTemperature={setTemperature}
        isStreaming={isStreaming}
        handleNewChat={handleNewChat}
      />

      <MessageList 
        messages={messages} 
        messagesContainerRef={messagesContainerRef} 
      />

      <MessageInput
        messageInput={messageInput}
        setMessageInput={setMessageInput}
        handleSubmit={handleSubmit}
        isStreaming={isStreaming}
        handleKeyDown={handleKeyDown}
        textareaRef={textareaRef}
      />
    </div>
  );
}