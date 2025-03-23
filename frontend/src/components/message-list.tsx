/**
 * @file message-list.tsx
 * @description
 *   Component that renders the scrollable list of chat messages and manages
 *   the container that holds all message bubbles.
 *
 * @features
 *   - Scrollable container for message history
 *   - Empty state handling with "No messages yet" indicator
 *   - Accessible markup with appropriate ARIA attributes
 *   - Automatic list management with keys for React reconciliation
 *   - Supports both user and assistant message types
 * 
 * @dependencies
 *   - React for component architecture
 *   - MessageBubble component for rendering individual messages
 *   - ChatMessage type from useChatState hook
 * 
 * @implementation
 *   The component receives a list of messages and a ref for the scrollable container.
 *   It renders either an empty state indicator or a list of MessageBubble components.
 *   The container uses ARIA attributes for accessibility and supports automatic scrolling
 *   via the parent component through the passed ref.
 */

import React, { useMemo } from 'react';
import MessageBubble from './message-bubble';
import { ChatMessage } from '../hooks/useChatState';

interface MessageListProps {
  messages: ChatMessage[];
  messagesContainerRef: React.RefObject<HTMLDivElement>;
}

/**
 * Renders a scrollable list of chat messages with accessibility support
 * 
 * @param props - Component properties including messages array and container ref
 * @returns A scrollable container with message bubbles or empty state
 */
export default function MessageList({ messages, messagesContainerRef }: MessageListProps) {
  // No messages indicator as a memoized value
  const noMessagesIndicator = useMemo(() => (
    <p className="text-gray-400 italic self-center mt-4">
      No messages yet.
    </p>
  ), []);

  return (
    <div 
      ref={messagesContainerRef}
      className="flex-grow overflow-y-auto flex flex-col gap-3 p-2"
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
    >
      {messages.length === 0 ? noMessagesIndicator : (
        <ul className="list-none p-0 m-0 w-full space-y-3">
          {messages.map((msg, index) => (
            <li key={index} className="w-full">
              <MessageBubble
                role={msg.role}
                content={msg.content}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}