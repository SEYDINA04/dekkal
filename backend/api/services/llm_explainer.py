"""
Dëkkal — LLM Explainer Service v2.0
Google Gemini (nouveau SDK google-genai)
Author : Babacar Ndao
"""
import os
import json
from google import genai
from google.genai import types

_client = None
LLM_PROVIDER = "gemini"


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_explanation(
    score: int,
    risk_level: str,
    zone_name: str,
    components: dict,
    explanations: list,
    address: str = "",
    lang: str = "en"
) -> dict:
    hist   = components.get('historical_risk', 0)
    struct = components.get('structural_vulnerability', 0)
    extreme = components.get('extreme_scenario_risk', 0)
    facts  = "\n".join([f"- {e['factor']} (impact: {e['impact']})" for e in explanations])

    if lang == "fr":
        prompt = f"""Tu es un expert en risque d'inondation pour les assureurs IARD au Sénégal.
Analyse ce score de risque et génère une réponse JSON structurée pour un souscripteur.

Adresse : {address or zone_name}
Score global : {score}/100 | Niveau : {risk_level}
Composants :
  - Risque historique       : {hist}/100
  - Vulnérabilité structurelle : {struct}/100
  - Risque scénario extrême : {extreme}/100
Facteurs clés :
{facts}

Réponds UNIQUEMENT avec ce JSON (sans markdown, sans texte autour) :
{{
  "narrative": "<synthèse professionnelle en 2-3 phrases : pourquoi ce score global, facteur principal, recommandation de souscription>",
  "breakdown": {{
    "historical_risk": "<explication du score {hist}/100 : ce que signifie ce chiffre, l'impact sur le risque>",
    "structural_vulnerability": "<explication du score {struct}/100 : ce que signifie ce chiffre, pourquoi cette vulnérabilité>",
    "extreme_scenario_risk": "<explication du score {extreme}/100 : ce que représente ce risque extrême pour cette zone>"
  }}
}}"""
    else:
        prompt = f"""You are a flood risk expert for IARD insurers in Senegal.
Analyze this risk score and generate a structured JSON response for an underwriter.

Address: {address or zone_name}
Overall score: {score}/100 | Level: {risk_level}
Components:
  - Historical risk            : {hist}/100
  - Structural vulnerability   : {struct}/100
  - Extreme scenario risk      : {extreme}/100
Key factors:
{facts}

Reply ONLY with this JSON (no markdown, no surrounding text):
{{
  "narrative": "<professional 2-3 sentence summary: why this overall score, main driver, underwriting recommendation>",
  "breakdown": {{
    "historical_risk": "<explanation of the {hist}/100 score: what this figure means, impact on risk>",
    "structural_vulnerability": "<explanation of the {struct}/100 score: what drives this vulnerability>",
    "extreme_scenario_risk": "<explanation of the {extreme}/100 score: what this extreme scenario represents for this zone>"
  }}
}}"""

    models_to_try = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.0-flash-001", "gemini-2.5-flash-lite"]
    last_error = None

    for model in models_to_try:
        try:
            response = _get_client().models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            raw = response.text.strip()
            parsed = json.loads(raw)
            return {
                "status"        : "success",
                "narrative"     : parsed.get("narrative", ""),
                "breakdown"     : parsed.get("breakdown"),
                "provider"      : "gemini",
                "context_length": len(prompt)
            }
        except json.JSONDecodeError:
            return {
                "status"        : "success",
                "narrative"     : response.text.strip(),
                "breakdown"     : None,
                "provider"      : "gemini",
                "context_length": len(prompt)
            }
        except Exception as e:
            last_error = e
            print(f"⚠️  Gemini {model} failed: {type(e).__name__}: {str(e)[:120]}")
            continue

    print(f"⚠️  All Gemini models failed. Last error: {last_error}")
    return {
        "status"        : "error",
        "narrative"     : f"AI analysis unavailable ({type(last_error).__name__}).",
        "breakdown"     : None,
        "provider"      : "gemini",
        "context_length": 0
    }


_SENEGAL_KEYWORDS = {'dakar', 'pikine', 'sénégal', 'senegal', 'thiès', 'rufisque', 'mbour', 'saint-louis'}


def _resolve_lang(score_obj: dict) -> str:
    lang = score_obj.get('lang', 'auto')
    if lang in ('fr', 'en'):
        return lang
    address = (score_obj.get('address', '') or score_obj.get('zone_name', '')).lower()
    return 'fr' if any(kw in address for kw in _SENEGAL_KEYWORDS) else 'en'


def generate_batch_explanations(scores: list, use_embeddings: bool = False) -> list:
    results = []
    for score_obj in scores:
        try:
            llm_result = generate_explanation(
                score        = score_obj.get('score', 0),
                risk_level   = score_obj.get('risk_level', 'Unknown'),
                zone_name    = score_obj.get('zone_name', 'Unknown'),
                components   = score_obj.get('components', {}),
                explanations = score_obj.get('explanations', []),
                address      = score_obj.get('address', ''),
                lang         = _resolve_lang(score_obj)
            )
            score_obj['llm_explanation'] = {
                "status"        : llm_result.get("status", "error"),
                "narrative"     : llm_result.get("narrative", ""),
                "breakdown"     : llm_result.get("breakdown"),
                "provider"      : llm_result.get("provider", "gemini"),
                "context_length": llm_result.get("context_length", 0),
                "embedding"     : None
            }
        except Exception as e:
            score_obj['llm_explanation'] = {
                "status"   : "error",
                "narrative": str(e),
                "breakdown": None,
                "provider" : "gemini",
                "context_length": 0,
                "embedding": None
            }
        results.append(score_obj)
    return results


def similarity_search(query: str, embedding_db: list, top_k: int = 3) -> list:
    query_lower = query.lower()
    scored = []
    for item in embedding_db:
        text = json.dumps(item).lower()
        common = sum(1 for w in query_lower.split() if w in text)
        scored.append({
            "similarity_score": common / max(len(query_lower.split()), 1),
            "item": item
        })
    scored.sort(key=lambda x: x['similarity_score'], reverse=True)
    return scored[:top_k]


def vectorize_scenario_library(input_path: str, output_path: str):
    with open(input_path) as f:
        scenarios = json.load(f)
    for s in scenarios:
        s['embedding'] = []
    with open(output_path, 'w') as f:
        json.dump(scenarios, f)
