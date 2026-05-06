import type {
  ApiErrorState,
  BatchExplainResponse,
  HealthResponse,
  LLMStatusResponse,
  ScoreRequest,
  ScoreResponse,
  SemanticSearchResponse,
  VectorizeScenariosResponse
} from "./types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(
  /\/$/,
  ""
);

const API_HEADERS = {
  "ngrok-skip-browser-warning": "true",
};

function normalizeDetail(detail: unknown): ApiErrorState {
  if (typeof detail === "string") {
    return { title: "Request failed", message: detail };
  }

  if (detail && typeof detail === "object") {
    const payload = detail as Record<string, unknown>;
    const error = typeof payload.error === "string" ? payload.error : "request_failed";
    const message =
      typeof payload.message === "string"
        ? payload.message
        : typeof payload.detail === "string"
          ? payload.detail
          : "The scoring service could not complete this request.";

    const titles: Record<string, string> = {
      zone_not_covered: "Outside Dakar coverage",
      geocoding_failed: "Address not found",
      feature_extraction_failed: "Feature service unavailable"
    };

    return {
      title: titles[error] ?? "Request failed",
      message,
      suggestions: Array.isArray(payload.suggestions)
        ? payload.suggestions.filter((value): value is string => typeof value === "string")
        : undefined
    };
  }

  return {
    title: "Request failed",
    message: "The scoring service returned an unexpected error."
  };
}

async function parseError(response: Response): Promise<ApiErrorState> {
  try {
    const body = await response.json();
    return normalizeDetail(body.detail ?? body);
  } catch {
    return {
      title: "Request failed",
      message: `The scoring service returned HTTP ${response.status}.`
    };
  }
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
    headers: API_HEADERS,
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json();
}

export async function getLlmStatus(): Promise<LLMStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/llm-status`, {
    headers: API_HEADERS,
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json();
}

export async function scoreLocation(
  request: ScoreRequest,
  options: { includeLlmExplanation?: boolean; lang?: "auto" | "fr" | "en" } = {}
): Promise<ScoreResponse> {
  const params = new URLSearchParams({
    include_llm_explanation: String(options.includeLlmExplanation ?? true),
    lang: options.lang ?? "en",
  });

  const response = await fetch(`${API_BASE_URL}/api/v1/score?${params.toString()}`, {
    method: "POST",
    headers: { ...API_HEADERS, "Content-Type": "application/json" },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  return response.json();
}

export async function batchExplainScores(
  scores: ScoreResponse[],
  options: { useEmbeddings?: boolean; lang?: "auto" | "fr" | "en" } = {}
): Promise<BatchExplainResponse> {
  const params = new URLSearchParams({
    use_embeddings: String(options.useEmbeddings ?? false),
    lang: options.lang ?? "en",
  });
  const file = new File([JSON.stringify(scores)], "scores.json", {
    type: "application/json",
  });
  const body = new FormData();
  body.append("scores_file", file);

  const response = await fetch(`${API_BASE_URL}/api/v1/batch-explain?${params.toString()}`, {
    method: "POST",
    headers: API_HEADERS,
    body,
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json();
}

export async function semanticSearch(
  query: string,
  options: { embeddingDbFile?: string; topK?: number } = {}
): Promise<SemanticSearchResponse> {
  const params = new URLSearchParams({
    query,
    top_k: String(options.topK ?? 3),
  });
  if (options.embeddingDbFile) {
    params.set("embedding_db_file", options.embeddingDbFile);
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/semantic-search?${params.toString()}`, {
    method: "POST",
    headers: API_HEADERS,
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json();
}

export async function vectorizeScenarios(file: File): Promise<VectorizeScenariosResponse> {
  const body = new FormData();
  body.append("scenarios_file", file);

  const response = await fetch(`${API_BASE_URL}/api/v1/vectorize-scenarios`, {
    method: "POST",
    headers: API_HEADERS,
    body,
  });
  if (!response.ok) {
    throw await parseError(response);
  }
  return response.json();
}

export async function downloadWordReport(
  result: ScoreResponse,
  options: { lang?: "fr" | "en" } = {}
): Promise<void> {
  const params = new URLSearchParams({ lang: options.lang ?? "fr" });
  const response = await fetch(`${API_BASE_URL}/api/v1/report-from-result?${params.toString()}`, {
    method: "POST",
    headers: { ...API_HEADERS, "Content-Type": "application/json" },
    body: JSON.stringify(result),
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  const address = result.location.address_normalized.replace(/\s+/g, "_").slice(0, 25);
  anchor.href = url;
  anchor.download = `dekkal_report_${address}.docx`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function normalizeUnknownError(error: unknown): ApiErrorState {
  if (
    error &&
    typeof error === "object" &&
    "title" in error &&
    "message" in error
  ) {
    return error as ApiErrorState;
  }

  if (error instanceof TypeError) {
    return {
      title: "Backend unavailable",
      message:
        "The dashboard could not reach the Dëkkal API. Use sample mode or start the backend."
    };
  }

  return {
    title: "Unexpected error",
    message: error instanceof Error ? error.message : "Something went wrong."
  };
}
