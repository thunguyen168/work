"""
AI Foresight Scanner - Lightweight Web Version
A simple, fast version that works within web hosting limits.
"""

import os
import re
import json
from datetime import datetime, timezone
from functools import wraps

import httpx
import anthropic
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32))

# Site password
SITE_PASSWORD = "Lockton2026!!"

# API clients
SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

# --- Input validation constants ---
MAX_TOPIC_LENGTH = 200
# Patterns that suggest sensitive data
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN = re.compile(r'(?:\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}')
# Policy / claim reference patterns (e.g., POL-123456, CLM-2024-001, etc.)
POLICY_CLAIM_PATTERN = re.compile(
    r'\b(?:POL|CLM|REF|INV|ACC|CLAIM|POLICY|CERT)[\s\-#]?\d{3,}',
    re.IGNORECASE
)
MULTI_PARAGRAPH_PATTERN = re.compile(r'\n\s*\n')


def validate_topic_input(topic: str) -> str | None:
    """Validate topic input and return error message if invalid, else None."""
    if len(topic) > MAX_TOPIC_LENGTH:
        return f'Input too long. Please keep your topic under {MAX_TOPIC_LENGTH} characters.'

    if EMAIL_PATTERN.search(topic):
        return 'Input appears to contain an email address. Please enter only a general topic using publicly available terms.'

    if PHONE_PATTERN.search(topic):
        return 'Input appears to contain a phone number. Please enter only a general topic using publicly available terms.'

    if POLICY_CLAIM_PATTERN.search(topic):
        return 'Input appears to contain a policy, claim, or reference number. Please enter only a general topic using publicly available terms.'

    if MULTI_PARAGRAPH_PATTERN.search(topic):
        return 'Multi-paragraph text is not accepted. Please enter a short topic description (one line).'

    return None


def require_auth(f):
    """Decorator to require password authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def search_web(query: str, num_results: int = 10) -> list:
    """Search the web using Serper or Brave API."""
    results = []

    if SERPER_API_KEY:
        # Use Serper
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
        # Use Brave
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

    # Format search results for the prompt
    sources_text = ""
    for i, result in enumerate(search_results, 1):
        sources_text += f"\n{i}. {result['title']}\n   {result['snippet']}\n   Source: {result['link']}\n"

    prompt = f"""You are a strategic foresight analyst following a systematic methodology for identifying phenomena. Based on the search results below about "{topic}", identify exactly 20 key phenomena.

PHENOMENON CRITERIA - Each phenomenon must meet ALL of these:
1. It must have a significant impact on several industries in the future.
2. Its potential impact is informed by the available evidence (not speculation alone).
3. It must be covered in several trustworthy publications for verification purposes (wild cards and weak signals are treated more flexibly here).
4. It must have a direction: either getting stronger, broader, deeper, or weaker, or merging with other phenomena. General themes like "Use of fossil fuels" or "Sharing economy" alone are NOT phenomena.
5. It must have a sufficiently independent and robust core description that can be verified.

Categorize each phenomenon into one of these four categories:
- "Strategic" - Long-term direction, competitive positioning, market shifts
- "Operational" - Day-to-day processes, technology, workforce, supply chain
- "Financial" - Economic factors, costs, investments, market valuations
- "Regulatory" - Laws, compliance, policy changes, governance

COLOUR-CODED SIGNAL TYPES - You MUST include at least one of each:
- "Strengthening" (GREEN): The issue is becoming more common or acute during the given timeframe. Most of its change potential is still ahead.
- "Weakening" (BLUE): The issue is becoming more unusual. During the given timeframe, most of its change potential or value has already occurred.
- "Established" (PURPLE): The issue has stabilised in its development. It has future relevance, but there is no indication it will significantly strengthen or weaken within the given timeframe.
- "Weak Signal" (GREY): A small emerging issue. At the given timeframe, it is still hard to say whether it will become a trend or fade away without substantial impact.
- "Wild Card" (RED): A possible but not probable event or change. Early information about a potential emerging risk or opportunity. Probability within the given timeframe is between 5% to 30%.

TIME HORIZON: Each phenomenon has a time range indicating when it is expected to accelerate in speed of change, stabilise, or begin to decline.
- "Near-term (0-5 years)"
- "Mid-term (5-10 years)"
- "Long-term (10-20 years)"

WRITING STYLE - VALUE RATIONALITY:
- Avoid dichotomous good-bad appraisals. Present descriptions in a neutral manner.
- Write descriptions as versatile and multifaceted analyses, originating from one single set of values but applicable to multiple perspectives.
- The summary should help the reader recognise the point of view the text represents, the formulation used, and the potential way to use it.
- Phenomenon descriptions are not truths carved in stone; they are analyses from one set of values that can be interpreted from multiple angles.

SOURCE RELIABILITY:
- The core of each phenomenon must be backed up by reliable sources.
- Prioritise: peer-reviewed scientific journals (Nature, Science), self-evidently proper scientific journals, Reuters, CNN, BBC, Financial Times, The Guardian, Wired, Scientific American.
- Also consider publications by universities, international research organisations (World Economic Forum, OECD).
- Internet-based, mainly ad-supported and freelance driven news distribution sites such as Popular Mechanics or Interesting Engineering are considered sufficiently reliable to be used as sources.

SEARCH RESULTS:
{sources_text}

For each phenomenon, provide:
1. **Title**: A clear, concise name (not a generic theme)
2. **Type**: One of: "Strengthening", "Weakening", "Established", "Weak Signal", or "Wild Card"
3. **Time Horizon**: "Near-term (0-5 years)", "Mid-term (5-10 years)", or "Long-term (10-20 years)"
4. **Category**: One of: "Strategic", "Operational", "Financial", or "Regulatory"
5. **Summary**: 2-3 sentences explaining what it is and why it matters, written in a neutral, multifaceted style
6. **Key Drivers**: 2-3 forces driving this phenomenon
7. **Implications**: 1-2 potential impacts or opportunities

Format your response as a JSON array like this:
[
  {{
    "title": "Example Trend",
    "type": "Strengthening",
    "time_horizon": "Near-term (0-5 years)",
    "category": "Strategic",
    "summary": "Description here...",
    "drivers": ["Driver 1", "Driver 2"],
    "implications": ["Implication 1", "Implication 2"]
  }}
]

Return ONLY the JSON array, no other text."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse the response
    response_text = response.content[0].text.strip()

    # Try to extract JSON from the response
    try:
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        phenomena = json.loads(response_text)
    except json.JSONDecodeError:
        # If parsing fails, return a simple error structure
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Password gate."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == SITE_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('home'))
        return render_template('login.html', error='Incorrect password.')
    return render_template('login.html', error=None)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@require_auth
def home():
    """Show the main page."""
    return render_template('index.html')


@app.route('/scan', methods=['POST'])
@require_auth
def scan_topic():
    """Handle the scan request."""
    try:
        topic = request.form.get('topic', '').strip()
        attestation = request.form.get('attestation', '')

        if not topic:
            return jsonify({'error': 'Please enter a topic to scan'}), 400

        # Require attestation
        if attestation != 'confirmed':
            return jsonify({'error': 'You must confirm the public-data attestation before submitting.'}), 400

        # Log attestation timestamp
        attestation_time = datetime.now(timezone.utc).isoformat()
        app.logger.info(f"Public-data attestation confirmed at {attestation_time} for topic: {topic[:50]}")

        # Validate input against sensitive patterns
        validation_error = validate_topic_input(topic)
        if validation_error:
            return jsonify({'error': validation_error}), 400

        # Check API keys
        if not ANTHROPIC_API_KEY:
            return jsonify({'error': 'Anthropic API key not configured'}), 500
        if not SERPER_API_KEY and not BRAVE_API_KEY:
            return jsonify({'error': 'No search API key configured (need SERPER_API_KEY or BRAVE_API_KEY)'}), 500

        # Step 1: Search the web (just 2 quick searches)
        search_queries = [
            f"{topic} trends 2024 2025",
            f"{topic} future predictions emerging"
        ]

        all_results = []
        results_per_query = 10
        for query in search_queries:
            results = search_web(query, num_results=results_per_query)
            all_results.extend(results)

        if not all_results:
            return jsonify({'error': 'No search results found. Please try a different topic.'}), 400

        # Remove duplicates based on link
        seen_links = set()
        unique_results = []
        for r in all_results:
            if r['link'] not in seen_links:
                seen_links.add(r['link'])
                unique_results.append(r)

        # Step 2: Analyze with Claude (single API call)
        analysis_sources = unique_results[:15]
        analysis = analyze_with_claude(topic, analysis_sources)  # Limit to 15 sources

        return jsonify({
            'success': True,
            'topic': analysis['topic'],
            'phenomena_count': len(analysis['phenomena']),
            'phenomena': analysis['phenomena'],
            'sources': unique_results,
            'attestation_timestamp': attestation_time
        })

    except anthropic.APIError as e:
        return jsonify({'error': f'AI API error: {str(e)}'}), 500
    except httpx.TimeoutException:
        return jsonify({'error': 'Search timed out. Please try again.'}), 500
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@app.route('/health')
def health():
    """Health check."""
    return jsonify({'status': 'healthy'})


@app.route('/debug')
def debug():
    """Debug endpoint - restricted to local/dev mode only."""
    if not app.debug:
        return jsonify({'error': 'Not available in production'}), 403
    return jsonify({
        'anthropic_key_set': bool(ANTHROPIC_API_KEY),
        'serper_key_set': bool(SERPER_API_KEY),
        'brave_key_set': bool(BRAVE_API_KEY)
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
