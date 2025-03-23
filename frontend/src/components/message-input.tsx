/**
 * @file message-input.tsx
 * @description
 *   Component for user message input in the chat interface with auto-resizing,
 *   keyboard shortcuts, and submission handling.
 *
 * @features
 *   - Auto-resizing text area for variable message lengths
 *   - Keyboard shortcuts for submission (Ctrl+Enter/Cmd+Enter)
 *   - Disabled state during streaming responses
 *   - Form submission handling
 *   - Visual feedback during streaming with button loading state
 *   - Accessible markup with appropriate ARIA attributes
 *
 * @dependencies
 *   - React for component architecture
 *   - Ant Design for Input.TextArea and Button components
 *   - External keyboard event handling through props
 * 
 * @implementation
 *   The component renders a form with a textarea and submit button. It uses a custom
 *   ref handling function to properly reference the inner textarea element of Ant Design's
 *   Input.TextArea component. The component is fully controlled with state management
 *   handled by the parent component via props.
 */

import React, { useEffect } from 'react';
import { Button, Input } from 'antd';

interface MessageInputProps {
  messageInput: string;
  setMessageInput: (value: string) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => Promise<void>;
  isStreaming: boolean;
  handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>, setMessageInput: (value: string) => void) => void;
  textareaRef: React.MutableRefObject<HTMLTextAreaElement | null>;
}

/**
 * User message input component with auto-resizing textarea and submit button
 * 
 * @param props - Component properties including message state, handlers and refs
 * @returns A form with textarea input and submit button for chat messages
 */
export default function MessageInput({
  messageInput,
  setMessageInput,
  handleSubmit,
  isStreaming,
  handleKeyDown,
  textareaRef,
}: MessageInputProps) {

  // Special ref handling for Ant Design's Input.TextArea
  const handleTextAreaRef = (node: any) => {
    if (node && textareaRef) {
      // Access the actual textarea element inside the Ant Design component
      textareaRef.current = node.resizableTextArea?.textArea;
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 items-end">
      <Input.TextArea
        ref={handleTextAreaRef}
        placeholder="Type your message..."
        value={messageInput}
        onChange={(e) => setMessageInput(e.target.value)}
        disabled={isStreaming}
        onKeyDown={(e) => handleKeyDown(e, setMessageInput)}
        rows={1}
        autoSize={{ minRows: 1, maxRows: 5 }}
        aria-label="Chat message input"
        className="flex-grow"
        style={{ 
          resize: 'none',
          padding: '8px 12px'
        }}
      />

      <Button
        type="primary"
        htmlType="submit"
        loading={isStreaming}
        disabled={!messageInput.trim()}
        aria-label="Send message"
        style={{ height: '40px' }}
      >
        Send
      </Button>
    </form>
  );
}