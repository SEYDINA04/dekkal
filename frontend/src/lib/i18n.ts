export type Lang = "en" | "fr";

export const t = {
  en: {
    // Header
    quoteReview: "Quote review",
    dashboardTitle: "Underwriting dashboard",
    scoringTitle: "Dëkkal Score",
    scoringInProcess: "Dëkkal scoring in process",

    // Form
    scoreLocation: "Score a Location",
    sampleMode: "Sample mode",
    address: "Address",
    latitude: "Latitude",
    longitude: "Longitude",
    propertyType: "Property type",
    runScore: "Run Risk Score",
    scoring: "Scoring...",

    // Property types
    residential: "Residential",
    commercial: "Commercial",
    hotel: "Hotel",
    school: "School",
    hospital: "Hospital",
    warehouse: "Warehouse",

    // Results
    riskComponents: "Risk Components",
    historicalRisk: "Historical risk",
    structuralVuln: "Structural vulnerability",
    extremeRisk: "Extreme scenario risk",
    riskAnalysis: "Dëkkal Risk Analysis",
    noScoreYet: "No score yet",
    noScoreDesc: "Submit an address or select coordinates on the Dakar map to start an underwriting review.",

    outOf100: "out of 100",

    // Risk levels
    Low: "Low", Moderate: "Moderate", High: "High", Extreme: "Extreme",

    // Decision labels
    standard_underwriting: "Standard underwriting",
    file_review: "File review recommended",
    field_verification_recommended: "Field verification advised",
    mandatory_human_decision: "Mandatory human decision required",

    // Underwriting decision
    uwDecision: "Underwriting Decision",
    humanLed: "human led",
    caseNotes: "Case notes",
    caseNotesPlaceholder: "Record broker context, inspection requirement, pricing rationale, or manager approval notes.",
    saveCase: "Save Case",
    exportReport: "Export .docx",
    exportingReport: "Generating...",
    savedReviews: "Saved Reviews",
    cases: "cases",

    // Final decisions
    accepted: "Accept",
    referred: "Refer",
    inspection_requested: "Request inspection",
    declined: "Decline",
    priced_up: "Price up",

    // Batch
    portfolioScreening: "Portfolio Screening",
    uploadCsv: "Upload CSV with address or lat/lon columns",
    csvColumns: "Columns accepted: address, location, site, lat, latitude, lon, lng, longitude.",
    runBatch: "Run Batch",
    runningBatch: "Scoring Batch...",
    exportCsv: "Export CSV",

    // Tooltips
    tooltipHistorical: "Based on satellite SAR imagery comparing dry vs. wet season water extent in this zone. Higher = more historical flood inundation detected.",
    tooltipStructural: "Estimates how susceptible the property is to flood damage given its elevation, terrain slope, and property type. Adjusted per asset class.",
    tooltipExtreme: "Probability of severe flood impact during rare but intense rainfall events (99th percentile precipitation). Reflects climate tail-risk.",

    // Scoring steps
    step1: "Geocoding address",
    step2: "Extracting satellite features",
    step3: "Running XGBoost model",
    step4: "Generating AI analysis",
  },

  fr: {
    // Header
    quoteReview: "Analyse de devis",
    dashboardTitle: "Tableau de souscription",
    scoringTitle: "Score Dëkkal",
    scoringInProcess: "Dëkkal analyse en cours",

    // Form
    scoreLocation: "Scorer une localisation",
    sampleMode: "Mode démo",
    address: "Adresse",
    latitude: "Latitude",
    longitude: "Longitude",
    propertyType: "Type de propriété",
    runScore: "Calculer le risque",
    scoring: "Calcul en cours...",

    // Property types
    residential: "Résidentiel",
    commercial: "Commercial",
    hotel: "Hôtel",
    school: "École",
    hospital: "Hôpital",
    warehouse: "Entrepôt",

    // Results
    riskComponents: "Composantes du risque",
    historicalRisk: "Risque historique",
    structuralVuln: "Vulnérabilité structurelle",
    extremeRisk: "Risque scénario extrême",
    riskAnalysis: "Analyse de risque Dëkkal",
    noScoreYet: "Aucun score",
    noScoreDesc: "Soumettez une adresse ou cliquez sur la carte de Dakar pour lancer une analyse de souscription.",

    outOf100: "sur 100",

    // Risk levels
    Low: "Faible", Moderate: "Modéré", High: "Élevé", Extreme: "Extrême",

    // Decision labels
    standard_underwriting: "Souscription standard",
    file_review: "Révision du dossier recommandée",
    field_verification_recommended: "Vérification terrain conseillée",
    mandatory_human_decision: "Décision humaine obligatoire",

    // Underwriting decision
    uwDecision: "Décision de souscription",
    humanLed: "décision humaine",
    caseNotes: "Notes du dossier",
    caseNotesPlaceholder: "Contexte courtier, exigences d'inspection, justification tarifaire ou validation manager.",
    saveCase: "Sauvegarder",
    exportReport: "Exporter .docx",
    exportingReport: "Génération...",
    savedReviews: "Dossiers sauvegardés",
    cases: "dossiers",

    // Final decisions
    accepted: "Accepter",
    referred: "Référer",
    inspection_requested: "Demander inspection",
    declined: "Refuser",
    priced_up: "Majorer la prime",

    // Batch
    portfolioScreening: "Screening de portefeuille",
    uploadCsv: "Charger un CSV avec colonnes adresse ou lat/lon",
    csvColumns: "Colonnes acceptées : address, location, site, lat, latitude, lon, lng, longitude.",
    runBatch: "Lancer le lot",
    runningBatch: "Calcul en cours...",
    exportCsv: "Exporter CSV",

    // Tooltips
    tooltipHistorical: "Basé sur les images SAR satellites comparant l'étendue de l'eau en saison sèche et humide. Plus élevé = plus d'inondations historiques détectées.",
    tooltipStructural: "Estime la susceptibilité du bien aux dommages d'inondation selon son altitude, la pente du terrain et le type de propriété.",
    tooltipExtreme: "Probabilité d'impact sévère lors d'événements pluviométriques rares et intenses (99e percentile). Reflète le risque climatique extrême.",

    // Scoring steps
    step1: "Géocodage de l'adresse",
    step2: "Extraction des données satellites",
    step3: "Modèle XGBoost en cours",
    step4: "Génération de l'analyse IA",
  },
} as const;

export type Translations = typeof t.en;
