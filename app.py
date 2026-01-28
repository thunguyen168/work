"""
AI Foresight Scanner - Web Interface
A simple Flask web app that lets users scan topics for future trends.
"""

import os
import asyncio
import traceback
import nest_asyncio
from flask import Flask, render_template, request, jsonify

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

app = Flask(__name__)

# Initialize scanner as None first - we'll try to load it
scanner = None
init_error = None

try:
    from src.cli import ForesightScanner
    from src.utils import Config
    config = Config()
    scanner = ForesightScanner(config=config)
except Exception as e:
    init_error = f"Failed to initialize scanner: {str(e)}\n{traceback.format_exc()}"


def run_async(coro):
    """Helper function to run async code safely."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@app.route('/')
def home():
    """Show the main page with the search form."""
    return render_template('index.html')


@app.route('/scan', methods=['POST'])
def scan_topic():
    """
    Handle the scan request.
    Takes a topic from the user and returns foresight analysis.
    """
    # Check if scanner initialized properly
    if scanner is None:
        return jsonify({
            'error': f'Scanner not initialized. {init_error or "Unknown error"}'
        }), 500
    
    try:
        # Get the topic from the form
        topic = request.form.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': 'Please enter a topic to scan'}), 400
        
        # Run the scan using our helper function
        phenomena = run_async(scanner.scan_topic(topic))
        
        # Generate outputs
        outputs = scanner.generate_outputs(phenomena, title=f"Foresight Scan: {topic}")
        
        # Return the results
        return jsonify({
            'success': True,
            'topic': topic,
            'phenomena_count': len(phenomena) if phenomena else 0,
            'phenomena': [p.to_dict() for p in phenomena] if phenomena and hasattr(phenomena[0], 'to_dict') else (phenomena if phenomena else []),
            'radar_chart': outputs.get('radar', ''),
            'html_report': outputs.get('html', '')
        })
        
    except Exception as e:
        error_details = traceback.format_exc()
        return jsonify({
            'error': f'{str(e)}',
            'details': error_details
        }), 500


@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({'status': 'healthy'})


@app.route('/debug')
def debug():
    """Debug endpoint to check if scanner loaded."""
    return jsonify({
        'scanner_loaded': scanner is not None,
        'init_error': init_error,
        'anthropic_key_set': bool(os.environ.get('ANTHROPIC_API_KEY')),
        'serper_key_set': bool(os.environ.get('SERPER_API_KEY')),
        'brave_key_set': bool(os.environ.get('BRAVE_API_KEY'))
    })


if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
