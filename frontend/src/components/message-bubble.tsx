/**
 * @file message-bubble.tsx
 * @description
 *   A React component responsible for displaying a single message in the chat with
 *   Markdown support, syntax highlighting, and copy functionality.
 *
 * @features
 *   - Markdown rendering with support for GFM and line breaks
 *   - Syntax highlighting for code blocks
 *   - One-click copy functionality for entire messages
 *   - Interactive PDF link detection and handling
 *   - Visual distinction between user and assistant messages
 *   - Accessible markup with appropriate ARIA attributes
 *
 * @dependencies
 *   - React for component architecture
 *   - ReactMarkdown for Markdown rendering
 *   - remark-gfm and remark-breaks for enhanced Markdown support
 *   - useChatState from ChatStateContext for PDF viewer integration
 *   - CodeBlock for code syntax highlighting
 * 
 * @implementation
 *   The component renders messages differently based on the sender role (user/assistant).
 *   It processes Markdown content and detects special PDF links with the "#pdf/" prefix.
 *   When these links are clicked, it updates the PDF viewer state via context.
 *   The component is optimized with memoization to prevent unnecessary rerenders.
 *
 * @notes
 *   - PDF links use "#pdf/" prefix to avoid sanitization
 *   - Custom link renderer intercepts PDF links and updates app state accordingly
 *   - User and assistant messages have different styling and alignment
 */

"use client";

import React, { useCallback, useMemo, memo } from "react";
import ReactMarkdown, { Components } from 'react-markdown';
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { Copy } from "lucide-react";
import CodeBlock from "./code-block";
import { useChatState } from "../contexts/ChatStateContext";
import type { ComponentPropsWithoutRef } from 'react';

// Use a standard URL pattern that won't get sanitized
const PDF_LINK_PREFIX = "#pdf/";

/**
 * Custom Link Renderer for ReactMarkdown.
 *
 * @param props - Anchor tag properties from ReactMarkdown.
 * @returns JSX.Element - A custom anchor element.
 */
const LinkRenderer = ({ href, children, ...rest }: React.ComponentPropsWithoutRef<'a'> & { node?: any }) => {
  const { setCurrentPdfEntry } = useChatState();

  // Check if the href is defined and starts with the PDF prefix.
  if (href && href.startsWith(PDF_LINK_PREFIX)) {
    const entryId = href.substring(PDF_LINK_PREFIX.length);

    const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
      e.preventDefault();
      
      // Update the chat state to display the selected PDF.
      setCurrentPdfEntry(entryId);
    };

    return (
      <a 
        href={href} 
        onClick={handleClick} 
        {...rest} 
        className="text-blue-600 hover:underline font-bold"
        style={{backgroundColor: "#f0f9ff", padding: "2px 4px", borderRadius: "4px"}}
      >
        {children}
      </a>
    );
  }

  // If not a PDF link, render the normal anchor element.
  return (
    <a href={href} {...rest} className="text-blue-600 hover:underline">
      {children}
    </a>
  );
};

/**
 * Props for the MessageBubble component.
 */
interface MessageBubbleProps {
  /**
   * Indicates who authored the message.
   */
  role: "user" | "assistant";
  /**
   * The raw text content (in Markdown format).
   */
  content: string;
}

/**
 * A component that renders a single chat message as a bubble with Markdown support,
 * syntax highlighting, copy functionality, and clickable PDF links.
 *
 * @param props - Component properties.
 * @returns Rendered message bubble.
 */
const MessageBubble: React.FC<MessageBubbleProps> = ({ role, content }) => {
  const isAssistant = role === "assistant";

  /**
   * Copies the entire message text to the clipboard.
   */
  const handleCopyMessage = useCallback(() => {
    try {
      navigator.clipboard.writeText(content.trim());
    } catch (err) {
      console.error("Failed to copy message:", err);
    }
  }, [content]);

  /**
   * Determine message alignment and background color based on sender.
   */
  const messageStyles = useMemo(() => ({
    containerAlign: isAssistant ? "justify-start" : "justify-end",
    bubbleBackground: isAssistant ? "bg-blue-100" : "bg-blue-200",
    senderLabel: isAssistant ? "Assistant" : "You"
  }), [isAssistant]);

  /**
   * Custom Markdown component configuration.
   * Includes custom renderers for code blocks and links.
   */
  const markdownComponents: Components = useMemo(() => ({
    code: ({ node, inline, className, children, ...props }) => (
      <CodeBlock 
        inline={inline}
        className={className}
        {...props}
      >
        {children}
      </CodeBlock>
    ),
    a: LinkRenderer
  }), []);

  return (
    <div className={`w-full flex ${messageStyles.containerAlign}`} role="listitem">
      <div
        className={`relative p-3 rounded-lg min-w-[30%] max-w-[80%] text-left ${messageStyles.bubbleBackground}`}
        aria-label={`${messageStyles.senderLabel} message`}
      >
        {/* Copy button */}
        <button
          type="button"
          onClick={handleCopyMessage}
          className="absolute top-2 right-2 bg-gray-400 hover:bg-gray-500 text-white p-0.5 rounded text-xs flex items-center"
          aria-label="Copy message to clipboard"
        >
          <Copy className="w-3 h-3 mr-0.5" />
          <span>Copy</span>
        </button>

        {/* Sender label */}
        <p className="text-sm font-semibold mb-1">{messageStyles.senderLabel}</p>

        {/* Message content rendered as Markdown */}
        <div className="prose break-words custom-markdown">
          <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} components={markdownComponents}>
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

// Memoize the component to prevent unnecessary re-renders.
export default memo(MessageBubble);
