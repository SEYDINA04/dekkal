# Dëkkal — Code of Ethics
**Company-Wide Standards for Responsible AI Development | v1.0 | April 2026**

---

## Preamble

Dëkkal builds AI systems that directly influence insurance decisions affecting families and communities in Dakar, Senegal. We recognize that our technology has real consequences — a mis-scored address could mean an uninsured family, a denied claim, or a missed flood warning. This Code of Ethics defines the non-negotiable principles that govern how we build, deploy, and maintain our systems.

---

## Principle 1 — Do No Harm

We will not deploy AI systems that we know to be inaccurate, biased, or harmful to the communities we serve. When we discover a flaw, we fix it before it causes harm — not after. We prioritize recall over precision in our model design because missing a real flood risk (false negative) causes more harm than over-scoring a safe address (false positive).

---

## Principle 2 — Fairness and Non-Discrimination

Our AI scores physical terrain — not people. We explicitly exclude income, ethnicity, neighborhood reputation, property ownership status, and all demographic proxies from our feature sets. We conduct quarterly fairness audits to verify that our scores reflect physical flood exposure, not socioeconomic patterns. If we discover systemic bias, we halt the affected scoring and notify all clients within 48 hours.

---

## Principle 3 — Transparency

We publish a full Model Card for every production model. We document our data sources, training methodology, known limitations, and performance metrics. We never claim capabilities our model does not have. We clearly distinguish between deployed features (v1.0) and features in development (LSTM — v2.0).

---

## Principle 4 — Human Dignity and Oversight

Our AI is a tool for human decision-makers, not a replacement for them. We design every system with a human fallback. Scores above 75/100 cannot be processed automatically — a human must review and confirm. We respect the right of any insured party to request a manual review of a risk score affecting their property.

---

## Principle 5 — Data Stewardship

We treat the data we handle — satellite images, climate records, property addresses — as a public trust. We collect only what we need. We store it securely in a sovereign datacenter. We delete it when the purpose expires. We never sell, share, or monetize address data or query logs.

---

## Principle 6 — Community Benefit

Dëkkal operates in West African cities where climate risk is severe and insurance penetration is below 3%. We commit to reinvesting a share of revenues into publishing open-data flood risk maps for Dakar local authorities — making our risk intelligence available to communities, not just corporations.

---

## Principle 7 — Accountability Without Excuses

When our model makes a mistake, we own it. We investigate, we document, we fix, and we communicate. We do not hide behind legal disclaimers. The responsible officer for model outputs — Babacar Ndao, CTO — is named publicly and reachable directly.

---

## Principle 8 — Climate Integrity

Dëkkal exists because climate change is accelerating flood risk in West Africa. We will never downplay, obscure, or misrepresent climate risk data to make our scores more commercially attractive. Our extreme scenario risk component deliberately captures risks that have never occurred historically — because climate change means the past is no longer a reliable guide to the future.

---

## Adherence and Review

This Code of Ethics is reviewed annually by the founding team. It is binding on all employees, contractors, and partners who build or use Dëkkal systems. Violations are treated as serious misconduct.

---

*Adopted by: Babacar Ndao (CTO) & Aminata Sall (CEO)*
*Dëkkal · Keur Massar, Dakar, Senegal · April 2026*
