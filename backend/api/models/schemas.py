"""
Dëkkal — API Schemas (Pydantic)
Input / Output contract
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class RiskLevel(str, Enum):
    LOW      = "Low"
    MODERATE = "Moderate"
    HIGH     = "High"
    EXTREME  = "Extreme"


class DecisionAction(str, Enum):
    STANDARD_UNDERWRITING         = "standard_underwriting"
    FILE_REVIEW                   = "file_review"
    FIELD_VERIFICATION            = "field_verification_recommended"
    MANDATORY_HUMAN_DECISION      = "mandatory_human_decision"


# ── INPUT ────────────────────────────────────────────────
class ScoreRequest(BaseModel):
    address : Optional[str]   = Field(None, example="Pikine Technopole, Dakar")
    lat     : Optional[float] = Field(None, example=14.75)
    lon     : Optional[float] = Field(None, example=-17.39)

    class Config:
        json_schema_extra = {
            "examples": [
                {"address": "Almadies, Dakar"},
                {"lat": 14.734, "lon": -17.510}
            ]
        }


# ── OUTPUT ───────────────────────────────────────────────
class ScoreComponents(BaseModel):
    historical_risk         : float = Field(..., ge=0, le=100)
    structural_vulnerability: float = Field(..., ge=0, le=100)
    extreme_scenario_risk   : float = Field(..., ge=0, le=100)


class Explanation(BaseModel):
    factor: str
    impact: str  # "High" | "Medium" | "Low"


class DecisionSupport(BaseModel):
    action: DecisionAction
    label : str


class ScoreMeta(BaseModel):
    model_version    : str
    data_freshness   : str
    processing_time_ms: int
    data_completeness: str  # "high" | "medium" | "low"


class ScoreResponse(BaseModel):
    location   : dict
    score      : int         = Field(..., ge=0, le=100)
    risk_level : RiskLevel
    components : ScoreComponents
    explanations     : List[Explanation]
    decision_support : DecisionSupport
    confidence       : float = Field(..., ge=0, le=1)
    warning          : Optional[str] = None
    meta             : ScoreMeta
