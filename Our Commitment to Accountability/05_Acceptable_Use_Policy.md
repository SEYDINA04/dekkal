# Dëkkal — Acceptable Use Policy
**Rules for Interaction with Dëkkal AI Features | v1.0 | April 2026**

---

## 1. Permitted Uses

Dëkkal's flood risk scoring API may be used exclusively for:

- Underwriting support for IARD (property & casualty) insurance policies
- Portfolio flood exposure analysis by licensed insurers
- Risk-based pricing research and actuarial modeling
- Regulatory reporting of flood exposure by financial institutions
- Academic and non-commercial climate risk research (with written approval)

---

## 2. Prohibited Uses

The following uses are strictly prohibited and constitute a breach of contract:

**2.1 Discriminatory Use**
Using Dëkkal scores to deny insurance coverage based on neighborhood reputation, perceived income level, or any factor unrelated to the physical flood risk of a specific address.

**2.2 Automated Decision-Making**
Using Dëkkal scores as the sole basis for automated approval or denial of insurance policies without human review — particularly for scores above 55/100.

**2.3 Data Resale**
Reselling, licensing, or redistributing Dëkkal risk scores or address data to third parties without written authorization from Dëkkal.

**2.4 Military or Security Use**
Using flood risk or drainage data for military intelligence, population surveillance, or security profiling.

**2.5 Reverse Engineering**
Attempting to reconstruct Dëkkal's model, training data, or proprietary algorithms through systematic API queries or other means.

**2.6 Out-of-Scope Geographic Use**
Applying Dëkkal scores to properties outside the declared coverage area without written confirmation of coverage from Dëkkal.

---

## 3. Insurer Responsibilities

Insurers using Dëkkal's API agree to:

- Treat Dëkkal scores as decision support — not as binding determinations
- Apply mandatory human review for all scores above 75/100
- Document decisions to deny coverage that reference Dëkkal scores
- Report confirmed flood events on scored addresses via POST /api/v1/feedback
- Not share access credentials with third parties

---

## 4. Dëkkal's Responsibilities

Dëkkal commits to:

- Maintaining API uptime of 99.5% during the rainy season (June–October)
- Providing a confidence score and data completeness flag on every response
- Notifying clients of model updates at least 14 days in advance
- Responding to data quality complaints within 48 hours

---

## 5. Enforcement

Violations of this policy may result in:
- Immediate suspension of API access
- Termination of the service agreement
- Legal action for damages where applicable

---

*Dëkkal · Keur Massar, Dakar, Senegal · nbcprof04@gmail.com · +221 78 312 88 32*
*Version 1.0 · April 2026*
