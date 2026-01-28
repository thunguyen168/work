"""
AI Foresight Scanner - Web Interface
A simple Flask web app that lets users scan topics for future trends.
"""

import os
import asyncio
from flask import Flask, render_template, request, jsonify

# Import the scanner components (from the existing src folder)
from src.cli import ForesightScanner
from src.utils import Config

app = Flask(__name__)

# Initialize the scanner
config = Config()
scanner = ForesightScanner(config=config)


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
    try:
        # Get the topic from the form
        topic = request.form.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': 'Please enter a topic to scan'}), 400
        
        # Run the scan (this may take a while)
        phenomena = asyncio.run(scanner.scan_topic(topic))
        
        # Generate outputs
        outputs = scanner.generate_outputs(phenomena, title=f"Foresight Scan: {topic}")
        
        # Return the results
        return jsonify({
            'success': True,
            'topic': topic,
            'phenomena_count': len(phenomena),
            'phenomena': [p.to_dict() for p in phenomena] if hasattr(phenomena[0], 'to_dict') else phenomena,
            'radar_chart': outputs.get('radar', ''),
            'html_report': outputs.get('html', '')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
