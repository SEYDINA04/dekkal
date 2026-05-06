import { ChangeEvent, useEffect, useState } from "react";
import { batchExplainScores, getLlmStatus, semanticSearch, vectorizeScenarios } from "@/api";
import { Button } from "@/components/ui/button";
import type {
  BatchExplainResponse,
  LLMStatusResponse,
  ScoreResponse,
  SemanticSearchResponse,
  VectorizeScenariosResponse,
} from "@/types";

export function AiToolsPage() {
  const [llmStatus, setLlmStatus] = useState<LLMStatusResponse | null>(null);
  const [semanticQuery, setSemanticQuery] = useState("low elevation high rainfall");
  const [embeddingDbFile, setEmbeddingDbFile] = useState("");
  const [semanticResult, setSemanticResult] = useState<SemanticSearchResponse | null>(null);
  const [vectorizeResult, setVectorizeResult] = useState<VectorizeScenariosResponse | null>(null);
  const [batchResult, setBatchResult] = useState<BatchExplainResponse | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    getLlmStatus().then(setLlmStatus).catch(() => setLlmStatus(null));
  }, []);

  async function handleVectorize(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy("vectorize");
    try {
      setVectorizeResult(await vectorizeScenarios(file));
    } finally {
      setBusy(null);
      event.target.value = "";
    }
  }

  async function handleBatchExplain(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy("batch");
    try {
      const scores = JSON.parse(await file.text()) as ScoreResponse[] | ScoreResponse;
      setBatchResult(await batchExplainScores(Array.isArray(scores) ? scores : [scores], { lang: "en" }));
    } finally {
      setBusy(null);
      event.target.value = "";
    }
  }

  async function runSemanticSearch() {
    setBusy("semantic");
    try {
      setSemanticResult(await semanticSearch(semanticQuery, {
        embeddingDbFile: embeddingDbFile || undefined,
        topK: 3,
      }));
    } finally {
      setBusy(null);
    }
  }

  return (
    <section className="mx-auto w-full max-w-7xl px-3 py-6 sm:px-4 sm:py-8 lg:px-8">
      <p className="text-sm uppercase tracking-[0.25em] text-lead">AI Tools</p>
      <h2 className="mt-2 text-3xl font-light text-ink sm:text-4xl md:text-5xl">
        LLM explanations and scenario search
      </h2>

      <div className="mt-8 grid gap-4 lg:grid-cols-2">
        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">LLM status</h3>
          <div className="mt-4 grid gap-2 text-sm text-slate-600">
            <p>Provider: <strong className="text-ink">{llmStatus?.llm_provider ?? "Checking..."}</strong></p>
            <p>Gemini configured: <strong className="text-ink">{llmStatus ? String(llmStatus.gemini_configured) : "Checking..."}</strong></p>
            <p>LLM model: <strong className="text-ink">{llmStatus?.gemini_models.llm ?? "N/A"}</strong></p>
            <p>Embedding model: <strong className="text-ink">{llmStatus?.gemini_models.embeddings ?? "N/A"}</strong></p>
          </div>
        </article>

        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">Batch explain</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Upload a JSON score response or an array of score responses. The backend returns LLM-enriched results.
          </p>
          <input
            accept="application/json,.json"
            className="mt-4 w-full rounded-full border border-slate-200 px-5 py-3 text-sm"
            type="file"
            onChange={handleBatchExplain}
          />
          {batchResult ? (
            <p className="mt-4 text-sm text-slate-600">
              Status: <strong className="text-ink">{batchResult.status}</strong>
              {batchResult.count ? ` · ${batchResult.count} explained` : ""}
              {batchResult.message ? ` · ${batchResult.message}` : ""}
            </p>
          ) : null}
        </article>

        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">Vectorize scenarios</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Upload scenario JSON to generate a server-side vectorized library path for semantic search.
          </p>
          <input
            accept="application/json,.json"
            className="mt-4 w-full rounded-full border border-slate-200 px-5 py-3 text-sm"
            type="file"
            onChange={handleVectorize}
          />
          {vectorizeResult ? (
            <div className="mt-4 rounded-2xl bg-slate-50 p-3 text-sm text-slate-600">
              <p>Status: <strong className="text-ink">{vectorizeResult.status}</strong></p>
              <p>Scenarios: <strong className="text-ink">{vectorizeResult.scenarios_vectorized ?? 0}</strong></p>
              <p className="break-all">Output: <strong className="text-ink">{vectorizeResult.output_file ?? "N/A"}</strong></p>
            </div>
          ) : null}
        </article>

        <article className="rounded-3xl border border-slate-200 bg-white p-5 sm:p-6">
          <h3 className="text-xl font-medium text-ink">Semantic search</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Search a vectorized scenario library. The backend currently expects a server-side JSON path.
          </p>
          <div className="mt-4 grid gap-3">
            <input
              className="rounded-full border border-slate-200 px-5 py-3 text-sm outline-none focus:border-mercury-blue"
              value={semanticQuery}
              onChange={(event) => setSemanticQuery(event.target.value)}
              placeholder="low elevation high rainfall"
            />
            <input
              className="rounded-full border border-slate-200 px-5 py-3 text-sm outline-none focus:border-mercury-blue"
              value={embeddingDbFile}
              onChange={(event) => setEmbeddingDbFile(event.target.value)}
              placeholder="/tmp/scenarios_vectorized.json"
            />
            <Button
              className="rounded-full bg-mercury-blue text-white hover:bg-mercury-blue/90"
              disabled={busy === "semantic"}
              onClick={runSemanticSearch}
              type="button"
            >
              {busy === "semantic" ? "Searching..." : "Search similar scenarios"}
            </Button>
          </div>
          {semanticResult ? (
            <div className="mt-4 grid gap-2">
              <p className="text-sm text-slate-600">
                Status: <strong className="text-ink">{semanticResult.status}</strong>
                {semanticResult.message ? ` · ${semanticResult.message}` : ""}
              </p>
              {semanticResult.results?.map((item, index) => (
                <article className="rounded-2xl border border-slate-100 p-3 text-sm" key={index}>
                  <strong className="text-ink">Similarity {item.similarity_score}</strong>
                  <p className="mt-1 text-slate-600">{item.risk_level} · {item.score}</p>
                  <p className="mt-1 text-slate-500">{item.narrative}</p>
                </article>
              ))}
            </div>
          ) : null}
        </article>
      </div>
    </section>
  );
}
