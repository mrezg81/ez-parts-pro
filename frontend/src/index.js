import React from "react";
import ReactDOM from "react-dom/client";
import "@fontsource/chivo/900.css";
import "@fontsource/jetbrains-mono/400.css";
import "@/index.css";
import App from "@/App";

// Register service worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('EzParts SW registered:', registration.scope);
      })
      .catch((error) => {
        console.log('EzParts SW registration failed:', error);
      });
  });
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
