/**
 * @file main.tsx
 * @description
 *   Entry point for the ChallengeChat React application. Vite reads this file as
 *   specified in index.html to initialize and render the UI.
 *
 * @notes
 *   - We import React and ReactDOM to mount the <App /> component into the #root element.
 *   - We import our global Tailwind + Ant Design styles from "index.css".
 *
 * @dependencies
 *   - React for creating UI components.
 *   - ReactDOM for rendering them to the DOM.
 *   - App component from ./App.
 *   - index.css for Tailwind and other global styles.
 */

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css"; // Global styles (Tailwind, etc.)
import "antd/dist/reset.css"; // Import Ant Design styles

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
