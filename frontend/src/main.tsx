import { StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { Toaster } from "react-hot-toast";
import "./index.css";
import "./i18n";
import App from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Suspense fallback={<div className="h-screen bg-gray-950" />}>
      <App />
      <Toaster
        position="bottom-center"
        toastOptions={{
          style: {
            background: "#1e293b",
            color: "#e2e8f0",
            border: "1px solid #334155",
          },
        }}
      />
    </Suspense>
  </StrictMode>
);
