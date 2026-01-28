import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";

import App from "./App";
import Child16App from "./Child16App";

const mode = String((import.meta as any).env?.VITE_APP_MODE ?? "").toLowerCase();

const rootEl = document.getElementById("root");
if (!rootEl) {
  throw new Error('Root element "#root" not found.');
}

createRoot(rootEl).render(
  <StrictMode>{mode === "child16" ? <Child16App /> : <App />}</StrictMode>
);
