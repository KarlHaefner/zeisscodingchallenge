/**
 * @file pdf-viewer.tsx
 * @description
 *   Component that renders a PDF document using the browser's built-in PDF viewer
 *   with loading states, error handling, and debugging information.
 *
 * @features
 *   - PDF rendering via iframe with native browser support
 *   - Loading state with visual indicator
 *   - Error handling with user-friendly messages
 *   - CORS issue detection via preflight fetching
 *   - Responsive layout that fills available space
 *   - Debug overlay with URL information
 * 
 * @dependencies
 *   - React for component architecture and state management
 *   - useState for loading and error state tracking
 *   - useEffect for URL validation and preflight checks
 * 
 * @implementation
 *   The component conducts a preflight fetch request to validate the PDF URL
 *   before attempting to load it in an iframe. It manages loading and error
 *   states to provide appropriate UI feedback. When no URL is provided or
 *   errors occur, informative messages are displayed instead of the PDF.
 *
 * @notes
 *   - Requires proper CORS headers on the PDF server for successful loading
 *   - Provides a direct link to open the PDF in a new tab when errors occur
 *   - Debugging overlay helps identify URL-related issues
 */

import React, { useState, useEffect } from "react";

interface PdfViewerProps {
  /**
   * The URL of the PDF to display in the iframe.
   */
  pdfUrl: string;
}

/**
 * Renders a PDF document within an iframe with loading and error handling
 * 
 * @param props - Component properties containing the PDF URL to display
 * @returns A responsive container with iframe PDF viewer and status indicators
 */
const PdfViewer: React.FC<PdfViewerProps> = ({ pdfUrl }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Add debugging to verify URL
  useEffect(() => {
    // Reset states when URL changes
    setLoading(true);
    setError(null);
    
    // Optional: Test the URL with a fetch to check for CORS issues
    if (pdfUrl) {
      fetch(pdfUrl)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error ${response.status}: ${response.statusText}`);
          }
          // Check content type
          const contentType = response.headers.get('content-type');
          return response.blob();
        })
        .then(blob => {
          // PDF fetch successful
        })
        .catch(err => {
          console.error("Error fetching PDF:", err);
          setError(`Error loading PDF: ${err.message}`);
        });
    }
  }, [pdfUrl]);

  // Handle iframe events
  const handleLoad = () => {
    setLoading(false);
  };

  const handleError = () => {
    console.error("PDF iframe failed to load");
    setError("Failed to load PDF in viewer");
    setLoading(false);
  };

  // If URL is empty, show a message
  if (!pdfUrl) {
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500">
        No PDF selected
      </div>
    );
  }

  return (
    <div className="w-full h-full relative">
      {/* Loading indicator */}
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 bg-opacity-75 z-10">
          Loading PDF...
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-100 bg-opacity-75 z-10">
          <div className="bg-white p-4 rounded shadow">
            <h3 className="text-red-600 font-bold">Error</h3>
            <p>{error}</p>
            <p className="text-sm mt-2">
              Try opening the PDF directly: <a href={pdfUrl} target="_blank" rel="noreferrer" className="text-blue-600 underline">Open PDF</a>
            </p>
          </div>
        </div>
      )}
      
      {/* PDF iframe */}
      <iframe
        src={pdfUrl}
        title="PDF Viewer"
        onLoad={handleLoad}
        onError={handleError}
        style={{
          width: "100%",
          height: "100%",
          border: "none",
        }}
      />
    </div>
  );
};

export default PdfViewer;
