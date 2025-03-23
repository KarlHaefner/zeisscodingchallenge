/**
 * @file ChatStateContext.tsx
 * @description
 *   A React context provider that manages the chat state and makes it available
 *   to all components in the application. This allows sharing state between
 *   ChatWindow and the PDF viewer without prop drilling.
 *
 * @features
 *   - Centralized state management for chat functionality
 *   - Type-safe context implementation with error handling
 *   - Seamless sharing of message history, model selection, and PDF viewing state
 *   - Prevents prop drilling through the component tree
 *
 * @dependencies
 *   - React for context and state management
 *   - useChatState hook for the actual state implementation
 * 
 * @implementation
 *   The module creates a context object with the same shape as the useChatState hook.
 *   It provides a wrapper component (ChatStateProvider) that initializes the chat
 *   state and makes it available to child components. It also exports a custom hook
 *   (useChatState) with proper error handling for consuming the context.
 */

import React, { createContext, useContext, ReactNode } from "react";
import { useChatState as useOriginalChatState } from "../hooks/useChatState";

// Create a context with the shape of the useChatState hook return value
const ChatStateContext = createContext<ReturnType<typeof useOriginalChatState> | undefined>(undefined);

// Props for the provider component
interface ChatStateProviderProps {
  children: ReactNode;
}

/**
 * Provider component that wraps the application and makes chat state available.
 * This component initializes the chat state using the original hook and provides 
 * it to all descendant components through React Context.
 * 
 * @param props - Component properties including children to be wrapped
 * @returns A context provider that makes chat state available to child components
 */
export function ChatStateProvider({ children }: ChatStateProviderProps) {
  const chatState = useOriginalChatState();
  
  return (
    <ChatStateContext.Provider value={chatState}>
      {children}
    </ChatStateContext.Provider>
  );
}

/**
 * Custom hook to use the chat state context with proper error handling.
 * This hook provides type-safe access to all chat state and functions.
 * 
 * @throws Error when used outside of a ChatStateProvider
 * @returns The complete chat state including messages, models, and all handlers
 */
export function useChatState() {
  const context = useContext(ChatStateContext);
  if (context === undefined) {
    throw new Error("useChatState must be used within a ChatStateProvider");
  }
  return context;
}