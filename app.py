"""
AI Foresight Scanner - Lightweight Web Version
A simple, fast version that works within web hosting limits.
"""

import os
import httpx
import anthropic
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# API clients
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')


def search_web(query: str, num_results: int = 5) -> list:
    """Search the web using Serper or Brave API."""
    results = []
    
    if SERPER_API_KEY:
        response = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY},
            json={"q": query, "num": num_results},
            timeout=15.0
        )
        if response.status_code == 200:
            data = response.json()
            for item in data.get("organic", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                })
    
    elif BRAVE_API_KEY:
        response = httpx.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": BRAVE_API_KEY},
            params={"q": query, "count": num_results},
            timeout=15.0
        )
        if response.status_code == 200:
            data = response.json()
            for item in data.get("web", {}).get("results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("description", ""),
                    "link": item.get("url", "")
                })
    
    return results


def analyze_with_claude(topic: str, search_results: list) -> dict:
    """Use Claude to analyze search results and identify trends."""
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    sources_text = ""
    for i, result in enumerate(search_results, 1):
        sources_text += f"\n{i}. {result['title']}\n   {result['snippet']}\n   Source: {result['link']}\n"
    
    prompt = f"""You are a foresight analyst. Based on the search results below about "{topic}", identify 3-5 key phenomena (trends, weak signals, or potential disruptions).

SEARCH RESULTS:
{sources_text}

For each phenomenon, provide:
1. **Title**: A clear, concise name
2. **Type**: One of: "Strengthening Trend", "Weakening Trend", "Weak Signal", or "Wild Card"
3. **Time Horizon**: "Near-term (0-5 years)", "Mid-term (5-10 years)", or "Long-term (10-20 years)"
4. **Summary**: 2-3 sentences explaining what it is and why it matters
5. **Key Drivers**: 2-3 forces driving this phenomenon
6. **Implications**: 1-2 potential impacts or opportunities

Format your response as a JSON array like this:
[
  {{
    "title": "Example Trend",
    "type": "Strengthening Trend",
    "time_horizon": "Near-term (0-5 years)",
    "summary": "Description here...",
    "drivers": ["Driver 1", "Driver 2"],
    "implications": ["Implication 1", "Implication 2"]
  }}
]

Return ONLY the JSON array, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = response.content[0].text.strip()
    
    import json
    try:
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        phenomena = json.loads(response_text)
    except json.JSONDecodeError:
        phenomena = [{
            "title": "Analysis Complete",
            "type": "Note",
            "time_horizon": "N/A",
            "summary": response_text[:500],
            "drivers": [],
            "implications": []
        }]
    
    return {
        "topic": topic,
        "phenomena": phenomena,
        "sources": search_results
    }


@app.route('/')
def home():
    """Show the main page."""
    return render_template('index.html')


@app.route('/scan', methods=['POST'])
def scan_topic():
    """Handle the scan request."""
    try:
        topic = request.form.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': 'Please enter a topic to scan'}), 400
        
        if not ANTHROPIC_API_KEY:
            return jsonify({'error': 'Anthropic API key not configured'}), 500
        if not SERPER_API_KEY and not BRAVE_API_KEY:
            return jsonify({'error': 'No search API key configured'}), 500
        
        search_queries = [
            f"{topic} trends 2024 2025",
            f"{topic} future predictions emerging"
        ]
        
        all_results = []
        for query in search_queries:
            results = search_web(query, num_results=5)
            all_results.extend(results)
        
        if not all_results:
            return jsonify({'error': 'No search results found.'}), 400
        
        seen_links = set()
        unique_results = []
        for r in all_results:
            if r['link'] not in seen_links:
                seen_links.add(r['link'])
                unique_results.append(r)
        
        analysis = analyze_with_claude(topic, unique_results[:8])
        
        return jsonify({
            'success': True,
            'topic': analysis['topic'],
            'phenomena_count': len(analysis['phenomena']),
            'phenomena': analysis['phenomena'],
            'sources': analysis['sources']
        })
        
    except anthropic.APIError as e:
        return jsonify({'error': f'AI API error: {str(e)}'}), 500
    except httpx.TimeoutException:
        return jsonify({'error': 'Search timed out. Please try again.'}), 500
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


@app.route('/debug')
def debug():
    return jsonify({
        'anthropic_key_set': bool(ANTHROPIC_API_KEY),
        'serper_key_set': bool(SERPER_API_KEY),
        'brave_key_set': bool(BRAVE_API_KEY)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
