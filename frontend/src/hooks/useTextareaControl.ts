/**
 * @file useTextareaControl.ts
 * @description
 *   Custom React hook that provides textarea control functionality for the chat interface,
 *   including keyboard shortcuts, cursor positioning, and scroll management.
 *
 * @features
 *   - Automatic scrolling to the bottom of the message container
 *   - Keyboard shortcuts for form submission (Enter) and line breaks (Shift+Enter)
 *   - Cursor position management for improved editing experience
 *   - Reference management for both textarea and messages container
 *   - Streaming state awareness to prevent submissions during responses
 * 
 * @dependencies
 *   - React hooks (useCallback, useRef) for memoization and DOM references
 *   - External state and handlers passed from parent component
 * 
 * @implementation
 *   The hook maintains references to the textarea element and the messages container.
 *   It provides handlers for special keyboard interactions, including differentiation
 *   between Enter (submit) and Shift+Enter (line break). The hook also manages cursor
 *   positioning after inserting line breaks and offers a utility to scroll the message
 *   container to the bottom.
 */

import { useCallback, useRef } from 'react';

export function useTextareaControl(messageInput: string, handleSubmit: (e: React.FormEvent<HTMLFormElement>) => Promise<void>, isStreaming: boolean) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  /**
   * Scrolls the messages container to the bottom to show the latest messages
   * Used after new messages are added or when the component mounts
   */
  const scrollToBottom = useCallback(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, []);

  /**
   * Handles keyboard events in the textarea to support special actions
   * - Enter key submits the form when not streaming and input is not empty
   * - Shift+Enter inserts a line break and maintains cursor position
   * 
   * @param e - Keyboard event from the textarea
   * @param setMessageInput - State setter function to update the input value
   */
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>, setMessageInput: (value: string) => void) => {
    if (e.key === 'Enter') {
      // If Shift is pressed with Enter, insert a line break
      if (e.shiftKey) {
        e.preventDefault();
        const cursorPosition = e.currentTarget.selectionStart;
        const textBeforeCursor = messageInput.slice(0, cursorPosition);
        const textAfterCursor = messageInput.slice(cursorPosition);
        
        // Update the message input with the newline inserted
        setMessageInput(textBeforeCursor + '\n' + textAfterCursor);
        
        // Store the desired cursor position
        const newCursorPosition = cursorPosition + 1;
        
        // Set cursor position after the inserted newline
        setTimeout(() => {
          const textarea = textareaRef.current;
          if (textarea) {
            textarea.focus();
            textarea.selectionStart = newCursorPosition;
            textarea.selectionEnd = newCursorPosition;
          }
        }, 0);
        return;
      } 
      // If just Enter without Shift, submit the form
      else if (!isStreaming && messageInput.trim()) {
        e.preventDefault();
        const syntheticEvent = new Event('submit') as unknown as React.FormEvent<HTMLFormElement>;
        handleSubmit(syntheticEvent);
      }
    }
  }, [handleSubmit, isStreaming, messageInput]);

  return {
    textareaRef,
    messagesContainerRef,
    scrollToBottom,
    handleKeyDown,
  };
}