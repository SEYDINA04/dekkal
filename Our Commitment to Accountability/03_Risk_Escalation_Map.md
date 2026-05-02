# Dëkkal — Risk Escalation Map
**Algorithmic Risk Reporting & Mitigation Process | v1.0 | April 2026**

---

## 1. Scoring Risk Thresholds & Automatic Actions

```
Score 0–30   (Low)      → Standard underwriting — no escalation
Score 31–55  (Moderate) → File review recommended — insurer notified
Score 56–75  (High)     → Field verification advised — flag raised
Score 76–100 (Extreme)  → MANDATORY human decision — automated processing blocked
```

---

## 2. Escalation Triggers

| Trigger | Who Detects | Action |
|---|---|---|
| Score > 75 | API (automatic) | Block automated decision, notify underwriter |
| Confidence < 0.5 | API (automatic) | Add warning flag to response |
| Geocoding failure | API (automatic) | Return error + address suggestions |
| False negative reported by insurer | Insurer via POST /api/v1/feedback | Open investigation (J+2) |
| Model drift detected (>10% score shift) | CTO monthly review | Trigger emergency recalibration |
| Data source outage (GEE, CHIRPS) | Monitoring (Prometheus) | Fallback to cached features + low-confidence flag |

---

## 3. Incident Response Protocol

```
J+0   Insurer reports incident via API or nbcprof04@gmail.com
J+2   CTO opens investigation — root cause analysis begins
J+5   Preliminary report: model error vs insurer decision error
J+15  Final root cause report with supporting satellite data
J+30  Corrective patch deployed + recalibration if systemic
J+30  All clients notified if error is systemic across multiple zones
```

---

## 4. Escalation Hierarchy

```
Level 1 — Automatic (API)
    → Score flags, confidence warnings, geocoding errors
    → No human intervention required

Level 2 — Insurer Risk Analyst
    → Scores 56–100 trigger recommended human review
    → Insurer responsible for final decision

Level 3 — Dëkkal CTO (Babacar Ndao)
    → Systemic scoring errors, model drift, data source failures
    → Response within 48 hours

Level 4 — Dëkkal CEO (Aminata Sall)
    → Regulatory escalation, CIMA audit requests
    → External legal or compliance involvement
```

---

## 5. Feedback Loop

```
Insurer reports sinistre → POST /api/v1/feedback
    ↓
Dëkkal logs incident in registry
    ↓
CTO reviews quarterly batch of feedback
    ↓
Model recalibration if pattern detected
    ↓
Updated model card published
```

---

## 6. Liability Cap

Dëkkal's financial liability is capped at 12 months of contract value per confirmed scoring error. All final underwriting decisions remain the sole responsibility of the insurer.

---

*Dëkkal · Keur Massar, Dakar, Senegal · nbcprof04@gmail.com*
*Version 1.0 · April 2026*
