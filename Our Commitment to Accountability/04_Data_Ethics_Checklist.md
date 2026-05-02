# Dëkkal — Data Ethics Checklist
**Internal Verification for Ethical Data Sourcing & Handling | v1.0 | April 2026**

---

## Section 1 — Data Collection & Sourcing

| # | Check | Status | Notes |
|---|---|---|---|
| 1.1 | All data sources have verified open licenses (CC BY, Open Government) | ✅ | Sentinel-1, CHIRPS, SRTM, SoilGrids, ERA5, GPM, OSM — all open |
| 1.2 | No personal data collected (names, addresses stored, income, ethnicity) | ✅ | Addresses pseudonymized (SHA-256) before storage |
| 1.3 | No demographic proxies used as features | ✅ | Only geophysical variables in model |
| 1.4 | Data sources are documented in a register | ✅ | See AI Inventory List |
| 1.5 | Institutional data (ANACIM, ONAS) used only under formal agreement | ⏳ | Partnerships in negotiation |
| 1.6 | Training labels are documented and auditable | ✅ | SAR-derived + terrain sources cited |

---

## Section 2 — Data Storage & Security

| # | Check | Status | Notes |
|---|---|---|---|
| 2.1 | Data hosted in sovereign datacenter | ✅ | Sénégal Numérique SA, Diamniadio (ISO 27001) |
| 2.2 | Data encrypted at rest | ✅ | SHA-256 for addresses |
| 2.3 | Data encrypted in transit | ✅ | TLS on all API endpoints |
| 2.4 | Access controls documented | ✅ | CTO-only access to partner data |
| 2.5 | Retention policy defined and implemented | ✅ | API logs: 90 days, scores: 24 months |
| 2.6 | No cross-border data transfer without consent | ✅ | West Africa only |

---

## Section 3 — Fairness & Bias

| # | Check | Status | Notes |
|---|---|---|---|
| 3.1 | Model trained on geophysical data only | ✅ | No socioeconomic variables |
| 3.2 | Fairness audit scheduled quarterly | ⏳ | First audit due Q3 2026 |
| 3.3 | Score distribution reviewed across administrative zones | ⏳ | Pending first commercial deployment |
| 3.4 | No systematic over-scoring of low-income zones | ⏳ | To be verified at first audit |
| 3.5 | Bias audit results published for clients | ⏳ | Protocol defined, implementation pending |

---

## Section 4 — Model Transparency

| # | Check | Status | Notes |
|---|---|---|---|
| 4.1 | Model Card published | ✅ | Available on request |
| 4.2 | Feature importance documented | ✅ | XGBoost SHAP — sar_delta (50%), precip (15%) |
| 4.3 | Known limitations documented | ✅ | SRTM resolution, 40-sample dataset |
| 4.4 | Performance metrics (Recall, Precision, F1) published | ✅ | Recall 83.3%, Precision 89.3%, F1 86.2% |
| 4.5 | Model version tracked per API response | ✅ | model_version field in every response |

---

## Section 5 — Human Oversight

| # | Check | Status | Notes |
|---|---|---|---|
| 5.1 | Mandatory human review for scores > 75 | ✅ | Enforced at API level |
| 5.2 | No automated insurance approvals/denials | ✅ | API returns decision support only |
| 5.3 | Human override mechanism exists | ✅ | POST /api/v1/feedback |
| 5.4 | Override decisions logged | ⏳ | Implementation pending |
| 5.5 | Responsible officer designated | ✅ | Babacar Ndao, CTO |

---

**Checklist Score: 23/30 items complete (77%)**
**Remaining 7 items: pending first commercial deployment or Q3 2026**

---

*Completed by: Babacar Ndao, CTO · April 2026*
