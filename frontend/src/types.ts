export type RiskLevel = "Low" | "Moderate" | "High" | "Extreme";

export type DecisionAction =
  | "standard_underwriting"
  | "file_review"
  | "field_verification_recommended"
  | "mandatory_human_decision";

export type PropertyType = "residential" | "commercial" | "hospital" | "school" | "hotel" | "warehouse";

export interface ScoreRequest {
  address?: string;
  lat?: number;
  lon?: number;
  property_type?: PropertyType;
}

export interface ScoreComponents {
  historical_risk: number;
  structural_vulnerability: number;
  extreme_scenario_risk: number;
}

export interface Explanation {
  factor: string;
  impact: "High" | "Medium" | "Low" | string;
}

export interface DecisionSupport {
  action: DecisionAction;
  label: string;
}

export interface ScoreMeta {
  model_version: string;
  data_freshness: string;
  processing_time_ms: number;
  data_completeness: "high" | "medium" | "low" | string;
  llm_enabled?: boolean | null;
  llm_provider?: string | null;
}

export interface ComponentBreakdown {
  historical_risk: string;
  structural_vulnerability: string;
  extreme_scenario_risk: string;
}

export interface LLMExplanation {
  narrative: string;
  breakdown?: ComponentBreakdown | null;
  provider: string;
  status: "success" | "error" | string;
  embedding?: number[] | null;
  context_length: number;
}

export interface ScoreResponse {
  location: {
    lat: number;
    lon: number;
    address_normalized: string;
  };
  score: number;
  risk_level: RiskLevel;
  components: ScoreComponents;
  explanations: Explanation[];
  decision_support: DecisionSupport;
  confidence: number;
  warning?: string | null;
  llm_explanation?: LLMExplanation | null;
  meta: ScoreMeta;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  model: string;
}

export interface ApiErrorState {
  title: string;
  message: string;
  suggestions?: string[];
}

export interface LLMStatusResponse {
  llm_provider: string;
  gemini_configured: boolean;
  openai_configured: boolean;
  ollama_configured: boolean;
  gemini_models: {
    llm: string;
    embeddings: string;
  };
}

export interface BatchExplainResponse {
  status: "success" | "error" | string;
  count?: number;
  lang_used?: string;
  results?: ScoreResponse[];
  message?: string;
}

export interface SemanticSearchResult {
  similarity_score: number;
  location: Record<string, unknown>;
  score?: number;
  risk_level?: RiskLevel | string;
  narrative?: string;
}

export interface SemanticSearchResponse {
  status: "success" | "error" | string;
  query?: string;
  results_count?: number;
  results?: SemanticSearchResult[];
  message?: string;
}

export interface VectorizeScenariosResponse {
  status: "success" | "error" | string;
  scenarios_vectorized?: number;
  output_file?: string;
  sample?: unknown;
  message?: string;
}
