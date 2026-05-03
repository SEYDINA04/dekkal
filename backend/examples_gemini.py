#!/usr/bin/env python
"""
Dëkkal — Gemini Integration Examples
Comprehensive code examples for all features
"""

import requests
import json
import os
from typing import Dict, List

# API BASE URL
API_URL = "http://localhost:8000/api/v1"

# ═══════════════════════════════════════════════════════════════════════════
# 1. BASIC SCORING WITH GEMINI EXPLANATION
# ═══════════════════════════════════════════════════════════════════════════

def example_1_basic_score_with_explanation():
    """Simple address scoring with Gemini explanation"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Score with Gemini Explanation")
    print("="*60)
    
    # Request
    payload = {
        "address": "Pikine Technopole, Dakar",
        "include_llm_explanation": True
    }
    
    response = requests.post(f"{API_URL}/score", json=payload)
    data = response.json()
    
    # Display results
    print(f"\n📍 Location: {data['location']['address_normalized']}")
    print(f"📊 Score: {data['score']}/100")
    print(f"⚠️  Risk Level: {data['risk_level']}")
    print(f"⏱️  Processing: {data['meta']['processing_time_ms']}ms")
    
    print(f"\n📝 Gemini Explanation:")
    print(f"   Provider: {data['llm_explanation']['provider']}")
    print(f"   Status: {data['llm_explanation']['status']}")
    print(f"   Narrative:\n   {data['llm_explanation']['narrative']}\n")
    
    print(f"🔢 Embedding:")
    if data['llm_explanation']['embedding']:
        emb = data['llm_explanation']['embedding']
        print(f"   Dimensions: {len(emb)}")
        print(f"   Sample: {emb[:5]}")
    
    return data


# ═══════════════════════════════════════════════════════════════════════════
# 2. GPS COORDINATES SCORING
# ═══════════════════════════════════════════════════════════════════════════

def example_2_gps_coordinates():
    """Score by GPS coordinates instead of address"""
    print("\n" + "="*60)
    print("EXAMPLE 2: GPS Coordinates Scoring")
    print("="*60)
    
    # Dakar locations
    locations = [
        {"name": "Pikine", "lat": 14.75, "lon": -17.39},
        {"name": "Almadies", "lat": 14.72, "lon": -17.50},
        {"name": "Keur Massar", "lat": 14.72, "lon": -17.45},
    ]
    
    for loc in locations:
        response = requests.post(
            f"{API_URL}/score",
            json={
                "lat": loc["lat"],
                "lon": loc["lon"],
                "include_llm_explanation": False  # Faster for batch
            }
        )
        data = response.json()
        print(f"\n{loc['name']:20} | Score: {data['score']:3d} | Risk: {data['risk_level']}")


# ═══════════════════════════════════════════════════════════════════════════
# 3. BATCH EXPLANATIONS
# ═══════════════════════════════════════════════════════════════════════════

def example_3_batch_explanations():
    """Generate explanations for multiple scores"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Explanations")
    print("="*60)
    
    # First, get scores for multiple addresses
    addresses = [
        "Pikine Technopole, Dakar",
        "Almadies, Dakar",
        "Keur Massar, Dakar",
    ]
    
    scores_data = []
    for addr in addresses:
        response = requests.post(
            f"{API_URL}/score",
            json={"address": addr, "include_llm_explanation": False}
        )
        data = response.json()
        scores_data.append({
            "location": data["location"],
            "score": data["score"],
            "risk_level": data["risk_level"],
            "explanations": data["explanations"],
            "features": {
                "elevation_m": 10,
                "p99_mm_day": 40,
                "clay_pct": 25
            }
        })
    
    # Save scores to file
    with open("batch_scores.json", "w") as f:
        json.dump(scores_data, f)
    
    # Call batch explanation endpoint
    with open("batch_scores.json", "rb") as f:
        files = {"scores_file": f}
        response = requests.post(
            f"{API_URL}/batch-explain",
            files=files,
            data={"use_embeddings": True}
        )
    
    results = response.json()
    print(f"\n✅ Processed: {results['count']} scores")
    print(f"📝 Explanations generated with embeddings")
    
    # Display sample
    if results['results']:
        sample = results['results'][0]
        print(f"\nSample result:")
        print(f"  Location: {sample['location']['address_normalized']}")
        print(f"  LLM Status: {sample['llm_explanation']['status']}")
        print(f"  Embedding size: {len(sample['llm_explanation'].get('embedding', []))}")


# ═══════════════════════════════════════════════════════════════════════════
# 4. SEMANTIC SEARCH
# ═══════════════════════════════════════════════════════════════════════════

def example_4_semantic_search():
    """Find similar flood scenarios using embeddings"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Semantic Search")
    print("="*60)
    
    # First, create a scenario library
    scenarios = [
        {
            "id": "scenario_1",
            "description": "Zone basse (< 10m) avec sols argileux (>25%) et drainage lent",
            "zone": "Pikine",
            "flood_frequency": 0.78,
            "risk_score": 78
        },
        {
            "id": "scenario_2",
            "description": "Plateau élevé (> 30m) avec pentes abruptes et bon drainage",
            "zone": "Almadies",
            "flood_frequency": 0.05,
            "risk_score": 15
        },
        {
            "id": "scenario_3",
            "description": "Moyennes altitudes (15-20m) avec sols mixtes et drainage modéré",
            "zone": "Dakar Centre",
            "flood_frequency": 0.35,
            "risk_score": 42
        }
    ]
    
    # Save scenarios
    with open("flood_scenarios.json", "w") as f:
        json.dump(scenarios, f)
    
    # Vectorize scenario library
    print("\n📊 Vectorizing scenario library...")
    with open("flood_scenarios.json", "rb") as f:
        files = {"scenarios_file": f}
        response = requests.post(
            f"{API_URL}/vectorize-scenarios",
            files=files
        )
    
    result = response.json()
    print(f"   ✅ {result['scenarios_vectorized']} scenarios vectorized")
    vectorized_path = result['output_file']
    
    # Now perform semantic search
    print("\n🔍 Searching for similar scenarios...")
    query = "Zone inondable avec sols imperméables et pluies extrêmes"
    
    response = requests.post(
        f"{API_URL}/semantic-search",
        params={
            "query": query,
            "embedding_db_file": vectorized_path,
            "top_k": 2
        }
    )
    
    search_results = response.json()
    print(f"\n   Query: '{query}'")
    print(f"   Found: {search_results['results_count']} similar scenarios\n")
    
    for i, result in enumerate(search_results['results'], 1):
        print(f"   {i}. Similarity: {result['similarity_score']:.3f}")
        print(f"      Zone: {result['location'].get('zone', 'Unknown')}")
        print(f"      Score: {result['score']}")
        print(f"      Risk: {result['risk_level']}")


# ═══════════════════════════════════════════════════════════════════════════
# 5. MULTI-LOCATION COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

def example_5_multi_location_comparison():
    """Compare flood risk across multiple locations"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Multi-Location Comparison")
    print("="*60)
    
    locations = {
        "Pikine": {"lat": 14.75, "lon": -17.39},
        "Keur Massar": {"lat": 14.72, "lon": -17.45},
        "Guediawaye": {"lat": 14.70, "lon": -17.42},
        "Almadies": {"lat": 14.72, "lon": -17.50},
    }
    
    results = []
    
    print("\n📊 Scoring locations...")
    for name, coords in locations.items():
        response = requests.post(
            f"{API_URL}/score",
            json={
                "lat": coords["lat"],
                "lon": coords["lon"],
                "include_llm_explanation": True
            }
        )
        data = response.json()
        results.append({
            "name": name,
            "score": data["score"],
            "risk_level": data["risk_level"],
            "explanation": data["llm_explanation"]["narrative"][:150]
        })
    
    # Display comparison table
    print("\n" + "─"*80)
    print(f"{'Location':<20} {'Score':<10} {'Risk Level':<15} {'Explanation':<50}")
    print("─"*80)
    
    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        print(f"{r['name']:<20} {r['score']:<10} {r['risk_level']:<15} {r['explanation']:<50}...")
    
    print("─"*80)


# ═══════════════════════════════════════════════════════════════════════════
# 6. LLM STATUS CHECK
# ═══════════════════════════════════════════════════════════════════════════

def example_6_llm_status():
    """Check LLM service configuration and health"""
    print("\n" + "="*60)
    print("EXAMPLE 6: LLM Service Status")
    print("="*60)
    
    response = requests.get(f"{API_URL}/llm-status")
    status = response.json()
    
    print(f"\n🤖 LLM Provider: {status['llm_provider']}")
    print(f"✅ Gemini Configured: {status['gemini_configured']}")
    print(f"✅ OpenAI Configured: {status['openai_configured']}")
    print(f"✅ Ollama Configured: {status['ollama_configured']}")
    
    print(f"\nModels:")
    for model_type, model_name in status['gemini_models'].items():
        print(f"  • {model_type}: {model_name}")


# ═══════════════════════════════════════════════════════════════════════════
# 7. SAVING AND ANALYZING RESULTS
# ═══════════════════════════════════════════════════════════════════════════

def example_7_save_and_analyze():
    """Save results to file and analyze patterns"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Save and Analyze Results")
    print("="*60)
    
    # Score multiple addresses
    addresses = [
        "Pikine",
        "Keur Massar",
        "Guediawaye",
        "Almadies",
        "Dakar Centre"
    ]
    
    print("\n📍 Scoring addresses...")
    all_results = []
    
    for addr in addresses:
        response = requests.post(
            f"{API_URL}/score",
            json={
                "address": addr + ", Dakar",
                "include_llm_explanation": True
            }
        )
        all_results.append(response.json())
    
    # Save to JSON
    with open("dekkal_results.json", "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # Analyze
    print("\n📊 Analysis:")
    print(f"   Total scores: {len(all_results)}")
    print(f"   Average score: {sum(r['score'] for r in all_results)/len(all_results):.1f}")
    print(f"   High risk: {sum(1 for r in all_results if r['score'] > 75)}")
    print(f"   Moderate risk: {sum(1 for r in all_results if 55 <= r['score'] <= 75)}")
    print(f"   Low risk: {sum(1 for r in all_results if r['score'] < 30)}")
    
    print(f"\n💾 Results saved to: dekkal_results.json")


# ═══════════════════════════════════════════════════════════════════════════
# 8. ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════

def example_8_error_handling():
    """Handle API errors gracefully"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Error Handling")
    print("="*60)
    
    # Test case 1: Invalid address (out of coverage)
    print("\n❌ Test 1: Out of coverage area")
    response = requests.post(
        f"{API_URL}/score",
        json={"address": "Paris, France"}
    )
    if response.status_code != 200:
        error = response.json()
        print(f"   Error: {error['detail']['error']}")
        print(f"   Message: {error['detail']['message']}")
    
    # Test case 2: Missing required fields
    print("\n❌ Test 2: Missing required fields")
    response = requests.post(
        f"{API_URL}/score",
        json={}
    )
    if response.status_code != 200:
        print(f"   HTTP {response.status_code}: {response.text}")
    
    # Test case 3: Handling timeout
    print("\n❌ Test 3: Timeout handling")
    try:
        response = requests.post(
            f"{API_URL}/score",
            json={"address": "Pikine, Dakar"},
            timeout=2  # Short timeout
        )
        print(f"   ✅ Response received in time")
    except requests.Timeout:
        print(f"   ⚠️  Request timed out after 2 seconds")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Run all examples"""
    print("\n🌊 Dëkkal — Gemini Integration Examples")
    print("=" * 60)
    print("Make sure the API is running on http://localhost:8000")
    print("=" * 60)
    
    try:
        example_1_basic_score_with_explanation()
        example_2_gps_coordinates()
        example_3_batch_explanations()
        example_4_semantic_search()
        example_5_multi_location_comparison()
        example_6_llm_status()
        example_7_save_and_analyze()
        example_8_error_handling()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print("Start the server with:")
        print("  cd /home/seydina/dekkal/backend")
        print("  python -m uvicorn main:app --reload --port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
