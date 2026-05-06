import { useEffect, useState } from "react";
import { getLlmStatus } from "@/api";
import type { LLMStatusResponse } from "@/types";

export function SettingsPage() {
  const [llmStatus, setLlmStatus] = useState<LLMStatusResponse | null>(null);

  useEffect(() => {
    getLlmStatus().then(setLlmStatus).catch(() => setLlmStatus(null));
  }, []);

  return (
    <section className="mx-auto w-full max-w-7xl px-3 py-6 sm:px-4 sm:py-8 lg:px-8">
      <p className="text-sm uppercase tracking-[0.25em] text-lead">Settings</p>
      <h2 className="mt-2 text-3xl font-light text-ink sm:text-4xl md:text-5xl">Pilot configuration</h2>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">Backend URL</h3>
          <p className="mt-3 text-slate-600">Configured through Vite with `VITE_API_BASE_URL`. Sample mode remains available for demos.</p>
        </article>
        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">Coverage</h3>
          <p className="mt-3 text-slate-600">Current scoring coverage is Dakar. Future settings can expose appetite thresholds by commune or line of business.</p>
        </article>
        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">LLM service</h3>
          <div className="mt-4 grid gap-3 text-sm text-slate-600">
            <p>Provider: <strong className="text-ink">{llmStatus?.llm_provider ?? "Checking..."}</strong></p>
            <p>Gemini configured: <strong className="text-ink">{llmStatus ? String(llmStatus.gemini_configured) : "Checking..."}</strong></p>
            <p>Model: <strong className="text-ink">{llmStatus?.gemini_models.llm ?? "N/A"}</strong></p>
          </div>
        </article>
        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">New backend endpoints</h3>
          <p className="mt-3 text-slate-600">
            The frontend API client now supports batch explanations, semantic search, scenario vectorization, and LLM status.
          </p>
        </article>
      </div>
    </section>
  );
}
