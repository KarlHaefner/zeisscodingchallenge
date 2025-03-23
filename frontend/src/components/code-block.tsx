/**
 * @file code-block.tsx
 * @description
 *   Reusable code block component that displays syntax-highlighted code with copy functionality.
 *   Supports both inline code snippets and multi-line code blocks with language detection.
 *
 * @features
 *   - Automatic language detection from className
 *   - Syntax highlighting using Prism
 *   - One-click copy to clipboard functionality
 *   - Support for both inline and block code display
 *   - Dark theme styling optimized for readability
 * 
 * @dependencies
 *   - React for component architecture
 *   - react-syntax-highlighter for code formatting and highlighting
 *   - lucide-react for the copy icon
 * 
 * @implementation
 *   The component renders either an inline <code> tag or a full syntax-highlighted
 *   code block based on the 'inline' prop. For code blocks, it extracts the language
 *   from the className and provides a copy button that uses the Clipboard API.
 *   Performance is optimized through component memoization.
 */

import React, { useCallback, memo } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { Copy } from "lucide-react";

interface CodeBlockProps {
  /**
   * Indicates if the code is an inline code snippet
   */
  inline?: boolean;
  
  /**
   * CSS classes for the code block, should include 'language-{name}' for syntax highlighting
   */
  className?: string;
  
  /**
   * The code content to be displayed and highlighted
   */
  children: React.ReactNode;
}

/**
 * Renders a syntax-highlighted code block with a copy button
 * 
 * @param props - Component properties including inline status, className, and children
 * @returns Rendered code block with syntax highlighting and copy functionality or inline code
 */
const CodeBlock: React.FC<CodeBlockProps> = ({ 
  inline, 
  className, 
  children,
  ...props 
}) => {
  // Extract the programming language from the class name (e.g., "language-javascript")
  const match = /language-(\w+)/.exec(className || "");
  const language = match ? match[1] : "text"; // Default to "text" for unspecified language
  const codeText = String(children).replace(/\n$/, "");

  /**
   * Copies this specific code block's text to the clipboard.
   * Uses the Navigator Clipboard API with error handling.
   */
  const handleCopyCodeBlock = useCallback(() => {
    try {
      navigator.clipboard.writeText(codeText);
    } catch (err) {
      console.error("Failed to copy code block:", err);
      // Optional: Show a toast notification for error feedback
    }
  }, [codeText]);

  // Only treat as inline if it's explicitly marked as inline
  if (inline) {
    return (
      <code className={className} {...props}>
        {children}
      </code>
    );
  }

  // Otherwise, render a code block with syntax highlighting and copy button
  return (
    <div className="relative my-2 p-0">
      <button
        type="button"
        onClick={handleCopyCodeBlock}
        className="
          absolute top-0 right-2
          bg-gray-700 hover:bg-gray-800
          text-white p-0.5 rounded
          text-xs flex items-center z-10
        "
        aria-label="Copy code to clipboard"
      >
        <Copy className="w-3 h-3 mr-0.5" />
        <span>Copy</span>
      </button>

      <SyntaxHighlighter
        style={oneDark}
        language={language}
        PreTag="div"
        className="w-full"
        customStyle={{ margin: 0, padding: '1.5rem 1rem 0.5rem 1rem' }}
        {...props}
      >
        {codeText}
      </SyntaxHighlighter>
    </div>
  );
};

// Memoize the component to prevent unnecessary re-renders
export default memo(CodeBlock);