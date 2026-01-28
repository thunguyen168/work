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
 
 
-def search_web(query: str, num_results: int = 5) -> list:
+def search_web(query: str, num_results: int = 10) -> list:
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
     
-    prompt = f"""You are a foresight analyst. Based on the search results below about "{topic}", identify 3-5 key phenomena (trends, weak signals, or potential disruptions).
+    prompt = f"""You are a foresight analyst. Based on the search results below about "{topic}", identify exactly 10 key phenomena (trends, weak signals, or potential disruptions).
+
+First, decide on 2-4 concise category labels that describe the landscape (e.g., "Technology", "Policy", "Market", "Society"). Use only these category labels for every phenomenon.
 
 SEARCH RESULTS:
 {sources_text}
 
 For each phenomenon, provide:
 1. **Title**: A clear, concise name
 2. **Type**: One of: "Strengthening Trend", "Weakening Trend", "Weak Signal", or "Wild Card"
 3. **Time Horizon**: "Near-term (0-5 years)", "Mid-term (5-10 years)", or "Long-term (10-20 years)"
-4. **Summary**: 2-3 sentences explaining what it is and why it matters
-5. **Key Drivers**: 2-3 forces driving this phenomenon
-6. **Implications**: 1-2 potential impacts or opportunities
+4. **Category**: One of your 2-4 category labels
+5. **Summary**: 2-3 sentences explaining what it is and why it matters
+6. **Key Drivers**: 2-3 forces driving this phenomenon
+7. **Implications**: 1-2 potential impacts or opportunities
 
 Format your response as a JSON array like this:
 [
   {{
     "title": "Example Trend",
     "type": "Strengthening Trend",
     "time_horizon": "Near-term (0-5 years)",
+    "category": "Technology",
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
     
     # Parse the response
     response_text = response.content[0].text.strip()
     
     # Try to extract JSON from the response
     import json
     try:
         # Remove markdown code blocks if present
         if response_text.startswith("```"):
             response_text = response_text.split("```")[1]
             if response_text.startswith("json"):
                 response_text = response_text[4:]
@@ -136,67 +140,68 @@ def home():
     return render_template('index.html')
 
 
 @app.route('/scan', methods=['POST'])
 def scan_topic():
     """Handle the scan request."""
     try:
         topic = request.form.get('topic', '').strip()
         
         if not topic:
             return jsonify({'error': 'Please enter a topic to scan'}), 400
         
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
+        results_per_query = 10
         for query in search_queries:
-            results = search_web(query, num_results=5)
+            results = search_web(query, num_results=results_per_query)
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
-        analysis = analyze_with_claude(topic, unique_results[:8])  # Limit to 8 sources
+        analysis = analyze_with_claude(topic, unique_results[:10])  # Limit to 10 sources
         
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
     """Health check."""
     return jsonify({'status': 'healthy'})
 
 
 @app.route('/debug')
 def debug():
 
EOF
)
