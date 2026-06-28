import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { Toaster } from "sonner";
import App from "./App";
import { queryClient } from "@/lib/query-client";
import "./index.css";

const root = document.getElementById("root");
if (!root) throw new Error("Missing #root element");

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster
          theme="dark"
          position="top-right"
          toastOptions={{
            className: "!bg-card !text-card-foreground !border-border",
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);