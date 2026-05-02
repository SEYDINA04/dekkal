# Dëkkal — Algorithmic Accountability Guideline
**Public Declaration of Logic, API Dependencies & Data Sovereignty | v1.0 | April 2026**
**ARISE Framework Compliant — Pillars 4 & 6**

---

## 1. System Description

**System Name:** Dëkkal Flood Risk Scoring Engine v1.0
**Type:** XGBoost Gradient Boosting Classifier (Statistical Layer)
**Purpose:** Deliver address-level flood risk scores (0–100) to IARD insurers in Dakar, Senegal
**Output:** Risk score + risk level + 3 explanatory factors + confidence interval + decision support action
**Coverage:** Dakar urban zone (lat 14.6–14.95, lon -17.6 to -17.1)

---

## 2. Model Logic

The scoring engine uses a three-component weighted aggregation:

```
Final Score = 0.25 × Historical Risk
            + 0.35 × Structural Vulnerability
            + 0.40 × Extreme Scenario Risk
```

**Historical Risk (25%):** Derived from Sentinel-1 SAR water detection delta between dry baseline (Jan–Feb 2020) and rainy season. Captures satellite-confirmed flood signals.

**Structural Vulnerability (35%):** Derived from SRTM elevation, slope, soil clay fraction (SoilGrids), antecedent soil moisture (ERA5-Land), and OSM drainage network proximity. Captures physical terrain susceptibility.

**Extreme Scenario Risk (40%):** Derived from CHIRPS + GPM IMERG ensemble P99 rainfall vs drainage capacity proxy (25mm/day for urban Dakar). Captures forward-looking climate risk even in zones with no flood history.

---

## 3. Third-Party API Dependencies

| Service | Provider | Purpose | Data Sovereignty |
|---|---|---|---|
| Google Earth Engine | Google LLC | Feature extraction (SAR, DEM, CHIRPS, ERA5, SoilGrids, GPM) | Processed on GEE servers — raw data not stored |
| Sentinel-1 SAR | ESA / Copernicus | Flood detection imagery | Open license — CC BY SA |
| CHIRPS Daily | UCSB / USAID | Precipitation time series | Open license |
| ERA5-Land | ECMWF / Copernicus | Soil moisture | Copernicus licence — non-commercial permitted |
| SoilGrids | ISRIC | Soil clay/sand properties | CC BY 4.0 |
| GPM IMERG | NASA EarthData | Extreme rainfall P99 | Open license |
| Nominatim | OpenStreetMap | Address geocoding | Open license — ODbL |
| OpenStreetMap | OSM Contributors | Drainage network | Open license — ODbL |
| Sénégal Numérique SA | Senegalese State | Data hosting | ISO 27001 certified — sovereign |

---

## 4. Data Sovereignty Statement

All Dëkkal data assets are hosted exclusively at **Sénégal Numérique SA**, Diamniadio, Senegal — an ISO 27001 certified sovereign datacenter. No personal data or client query data is transferred outside West Africa. Third-party API calls (GEE, Nominatim) transmit only coordinates and return numerical values — no personal data leaves Dëkkal's systems.

---

## 5. Standardised Data Schema

All inputs are standardised to **WGS84 coordinate reference system** before processing. Property addresses are pseudonymized using SHA-256 hashing before storage. No plaintext addresses are retained beyond the scoring transaction.

**Input schema:**
```json
{ "address": "string" }  OR  { "lat": float, "lon": float }
```

**Output schema:**
```json
{
  "score": int (0-100),
  "risk_level": "Low|Moderate|High|Extreme",
  "components": { "historical_risk": float, "structural_vulnerability": float, "extreme_scenario_risk": float },
  "explanations": [{ "factor": string, "impact": "High|Medium|Low" }],
  "confidence": float (0-1),
  "meta": { "model_version": string, "data_freshness": string, "processing_time_ms": int }
}
```

---

## 6. Bias & Fairness Protocol

- Features: geophysical variables only — no demographic, income, or social proxies
- Quarterly fairness audits comparing score distributions across Dakar administrative zones
- Bias audit reports available to clients on request
- Responsible officer: Babacar Ndao, CTO

---

## 7. Performance Metrics (LOO-CV on 40-sample dataset)

| Metric | Value | Target |
|---|---|---|
| Accuracy | 80.0% | — |
| Precision | 89.3% | >75% ✅ |
| Recall | 83.3% | >80% ✅ |
| F1-Score | 86.2% | >77% ✅ |
| Training samples | 40 | Target: 200+ (v1.1) |

---

## 8. Known Limitations

- Training dataset: 40 samples (4 Dakar zones × 10 years) — XGBoost performance will improve with more samples
- SRTM 30m resolution: limited address-level discrimination in flat urban zones
- Keur Massar bbox: partially validated — known noise in SAR labels
- LSTM temporal layer: in development for v2.0 — not deployed in v1.0
- Coverage: Dakar urban zone only — no other Senegalese cities yet

---

## 9. Audit Trail

Every API response includes a signed metadata payload:
- model_version: identifies which model produced the score
- data_freshness: vintage of input data used
- processing_time_ms: full latency measurement
- confidence: data completeness indicator

External audits are conducted annually. Audit reports are produced within 15 business days of request.

---

*Dëkkal · Keur Massar, Dakar, Senegal · nbcprof04@gmail.com · +221 78 312 88 32*
*ARISE Framework — Pillars 4 (Data Sovereignty) & 6 (Ethical Governance)*
*Version 1.0 · April 2026*
