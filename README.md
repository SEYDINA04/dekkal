# Dëkkal — Technical Deliverables

**Version:** 1.0  
**Date:** April 2026  
**Team:** Aminata Sall · Babacar Ndao · Desmone Coffee  
**Status:** Pre-pilot · Architecture complete · Pipeline validated

---

## 1. Technology stack

| Layer | Description |
|---|---|
| **Frontend** | Interactive web dashboard with map-based risk visualization and REST API access for programmatic integration |
| **Backend** | Python-based microservices architecture with asynchronous task processing and real-time data handling |
| **AI & ML** | Gradient boosting model for static flood vulnerability scoring combined with a deep learning time-series model for dynamic nowcasting |
| **Database** | Geospatial relational database for score storage and address lookup, complemented by object storage for raw climate and satellite data |
| **Orchestration** | Automated multi-source data pipeline with scheduling, retry logic, and failure alerting |
| **Hosting** | African sovereign cloud infrastructure based in Senegal, compliant with local data governance requirements |
| **Monitoring** | Automated model performance tracking with data drift detection and retraining triggers |
| **Security** | Secret management, encrypted communications, audit logging, and role-based access control |

---

## 2. System architecture

```
┌──────────────────────────────────────────────────────┐
│               AUTOMATED DATA PIPELINE                │
│   Satellite imagery · Climate reanalysis · Terrain   │
│   Rainfall · Soil · Urban network · Ground truth     │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                    AI ENGINE                         │
│   Static vulnerability model  (periodic update)     │
│   Dynamic nowcasting model    (real-time updates)    │
│   Validation · Monitoring · Auto-retrain             │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              API & CLIENT INTERFACES                 │
│   REST API — score · forecast · batch endpoints      │
│   Web dashboard — underwriting & operations views    │
│   PDF reports · CSV batch export · Webhook alerts    │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                    END USERS                         │
│   IARD insurers · Governments · NGOs                 │
└──────────────────────────────────────────────────────┘
```

### AI flow

```
Address input
      │
      ▼
Geospatial lookup
      │
      ├── Terrain features     (elevation · slope · drainage)
      ├── Urban features       (built density · land cover)
      ├── Soil features        (infiltration · soil type)
      └── Rainfall features    (historical · real-time)
      │
      ▼
Static model ──────────────────┐
                               ├──► Fused risk score (0–100)
Dynamic nowcasting model ──────┘
      │
      ▼
Risk score delivered via API · Dashboard · Alerts
```

---

## 3. GitHub repository structure

```
dekkal/
├── .github/
│   └── workflows/          # CI/CD — tests, linting, deploy
├── pipeline/
│   ├── ingestion/          # Automated data collection
│   ├── processing/         # Geospatial feature extraction
│   └── features/           # ML feature engineering
├── models/
│   ├── static/             # Vulnerability scoring model
│   └── dynamic/            # Nowcasting model
├── api/
│   ├── main.py             # API entrypoint
│   ├── routers/            # Endpoints
│   └── schemas/            # Data validation
├── dashboard/              # Frontend web interface
├── docker/
│   └── docker-compose.yml  # Local development environment
├── tests/                  # Unit + integration tests
├── docs/                   # Technical documentation
└── README.md
```

---

## 4. Technical risks and constraints

| Risk | Severity | Mitigation |
|---|---|---|
| Institutional data access delays | High | Free open-source satellite datasets available as fallback for MVP |
| Urban terrain model bias | High | Secondary elevation dataset as correction layer |
| Historical flood label scarcity | Medium | Multi-source ground truth approach (satellite + official records) |
| API scalability under peak load | Medium | Score caching layer with time-to-live expiration |
| African cloud infrastructure reliability | Medium | Redundancy plan with multi-zone deployment |
| Model performance degradation over time | Low | Automated drift monitoring with retraining pipeline |

---

## 5. Development workflow

### Branching strategy

```
main          ←  Production only · Protected · Requires PR review
develop       ←  Integration branch · All features merge here first
feature/xxx   ←  New features (backend, models, API)
data/xxx      ←  Data pipeline and ML experiments
hotfix/xxx    ←  Critical production fixes only
```

### Merge rules

- Minimum 1 peer review before merge to `develop`
- All automated tests must pass before merge
- No direct push to `main` — release via PR only
- Feature branches deleted after merge

### CI/CD pipeline

```
Push to feature branch
      │
      ▼
Automated tests + linting
      │
      ▼
PR review (1 approver minimum)
      │
      ▼
Merge to develop
      │
      ▼
Integration tests
      │
      ▼
Merge to main → Deploy to production
```

---

## 6. MVP milestones

| Week | Deliverable | Owner |
|---|---|---|
| 1–2 | Data download + geospatial feature extraction | Aminata |
| 2–3 | Static model training + validation | Aminata + Babacar |
| 3 | REST API live on production server | Babacar |
| 4 | Dashboard MVP + pilot demo ready | Babacar |
| Phase 2 | Dynamic nowcasting model | Babacar |
| Phase 2 | IoT sensor integration | Babacar |
| Phase 2 | Multi-city expansion | Full team |

---

*Dëkkal — Know your ground.*
