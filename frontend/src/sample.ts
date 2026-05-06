import type { ScoreResponse } from "./types";

export const sampleScore: ScoreResponse = {
  location: {
    lat: 14.734,
    lon: -17.39,
    address_normalized: "Pikine, Dakar, Senegal"
  },
  score: 68,
  risk_level: "High",
  components: {
    historical_risk: 45,
    structural_vulnerability: 76.4,
    extreme_scenario_risk: 69.8
  },
  explanations: [
    {
      factor: "Pikine - 70% historical flood frequency",
      impact: "High"
    },
    {
      factor: "Moderate satellite flood signal detected",
      impact: "Medium"
    },
    {
      factor: "Low elevation (4.8m)",
      impact: "High"
    }
  ],
  decision_support: {
    action: "field_verification_recommended",
    label: "Field verification advised"
  },
  confidence: 0.82,
  warning: null,
  meta: {
    model_version: "xgboost_v1.0",
    data_freshness: "2026-04",
    processing_time_ms: 1840,
    data_completeness: "high"
  }
};
