/**
 * @file App.tsx
 * @description
 *   The root component of the ChallengeChat application that orchestrates the complete UI layout
 *   and provides context for state sharing between components.
 *
 * @features
 *   - Two-column responsive layout with chat and PDF viewer
 *   - Centralized state management through ChatStateProvider
 *   - Dynamic PDF viewer that appears when a document is selected
 *   - Responsive design that adapts to different screen sizes
 *   - Informative placeholder when no PDF is selected
 * 
 * @dependencies
 *   - React for component architecture and rendering
 *   - ChatWindow for the messaging interface
 *   - PdfViewer for rendering PDF documents
 *   - ChatStateContext for state sharing across components
 * 
 * @implementation
 *   The component is organized into two main parts: a wrapper App component that provides
 *   the ChatStateContext, and an inner AppContent component that consumes the context
 *   and renders the actual UI. The layout uses a responsive two-column design that
 *   shows both chat and PDF viewer on desktop, but collapses to a single column on mobile.
 *
 * @notes
 *   - 'use client' directive is required for Next.js client-side rendering
 *   - PDF viewer is conditionally rendered based on currentPdfEntry state
 *   - Layout container uses fixed height (90vh) for consistent display
 */

"use client";

import React from "react";
import ChatWindow from "./components/chat-window";
import PdfViewer from "./components/pdf-viewer";
import { ChatStateProvider, useChatState } from "./contexts/ChatStateContext";

/**
 * Inner component that consumes ChatStateContext to render the complete UI layout
 * 
 * @returns A responsive two-column layout with chat interface and conditional PDF viewer
 */
function AppContent(): JSX.Element {
  const { currentPdfEntry } = useChatState();
  
  // Construct PDF URL if a PDF is selected
  const pdfUrl = currentPdfEntry ? `http://localhost:8000/api/pdf/${currentPdfEntry}/` : "";

  return (
    <div className="min-h-screen flex flex-col justify-center bg-white p-2">
      <h1 className="text-2xl font-semibold mb-4 pl-4">
        ChallengeChat
      </h1>

      <div className="w-full" style={{ maxWidth: "2000px" }}>
        {/* Two-column layout with gap */}
        <div className="w-full h-[90vh] flex gap-4 overflow-hidden">
          {/* Left column: Chat interface */}
          <div className="flex flex-col w-full md:w-1/2 bg-white rounded shadow-lg overflow-hidden">
            <ChatWindow />
          </div>
          
          {/* Right column: PDF Viewer (only displayed if a PDF is selected) */}
          {currentPdfEntry ? (
            <div className="hidden md:flex w-1/2 bg-white rounded shadow-lg overflow-hidden">
              <PdfViewer pdfUrl={pdfUrl} />
            </div>
          ) : (
            <div className="hidden md:flex w-1/2 bg-white rounded shadow-lg overflow-hidden items-center justify-center text-gray-500 p-4 text-center">
              Please ask for arXiv papers to show them here.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Root component that wraps AppContent with ChatStateProvider for state management
 * 
 * @returns The complete application with context provider and UI components
 */
function App(): JSX.Element {
  return (
    <ChatStateProvider>
      <AppContent />
    </ChatStateProvider>
  );
}

export default App;