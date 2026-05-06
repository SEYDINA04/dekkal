import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router";
import "leaflet/dist/leaflet.css";
import "./styles.css";
import App from "./app";

const root = document.getElementById("root");

ReactDOM.createRoot(root!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
