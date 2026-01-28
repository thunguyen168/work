# AI Foresight Scanner

An AI-enabled tool that scrapes the web to identify, structure, and monitor future-oriented phenomena (trends, weak signals, and potential disruptions) in a consistent, card-based foresight format suitable for strategy and risk discussions.

## Features

- **Web Scanning**: Automated search and scraping of credible sources (academic, intergovernmental, think tanks, industry research)
- **AI-Powered Analysis**: Uses Claude to structure findings into professional foresight format
- **Johari Window Heuristic**: Comprehensive scanning across known/unknown dimensions to reduce blind spots
- **Card-Based Output**: Each phenomenon follows a repeatable structure with title, classification, drivers, scenarios, and impacts
- **Radar Visualization**: Interactive web/radar chart showing phenomena by time horizon and thematic area
- **Multiple Formats**: Outputs in HTML, Markdown, and JSON

## Installation

### Prerequisites

- Python 3.10+
- Anthropic API key
- Search API key (Serper or Brave)

### Setup

```bash
# Clone the repository
git clone https://github.com/example/ai-foresight-scanner.git
cd ai-foresight-scanner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Environment Variables

Set your API keys:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export SERPER_API_KEY="..."  # or BRAVE_API_KEY
```

## Quick Start

```bash
# Scan a single topic
foresight-scan "artificial intelligence in healthcare"

# Scan multiple topics
foresight-scan "quantum computing" "synthetic biology" "space economy"

# Use custom output directory
foresight-scan --output ./my_scans "future of work"

# Generate only specific formats
foresight-scan --format html "climate adaptation technologies"
```

## Output Structure

### Phenomenon Card Format

Each identified phenomenon includes:

1. **Title and Tags**: Concise title with thematic tags (technology, society, economy, etc.)

2. **Classification**:
   - Type: Strengthening, Weakening, Weak Signal, or Wild Card
   - Time Horizon: Near-term (0-5y), Mid-term (5-10y), Long-term (10-20y)
   - Confidence Level: Low, Moderate, High

3. **Summary**: Single paragraph explaining what, why it matters, current state, and plausible futures (with hyperlinked sources)

4. **Key Drivers**: STEEP+G categorized forces shaping the phenomenon

5. **Future Scenarios**: Two contrasting but plausible directions with:
   - Impact assessment (risks, opportunities)
   - Development path with milestones and indicators

6. **Connections**: Related phenomena, second-order effects, areas for exploration

### Radar Visualization

The radar chart displays phenomena where:
- **Distance from center** = Time horizon (closer = nearer term)
- **Angle** = Thematic area
- **Color** = Phenomenon type
- **Size** = Confidence level

## Configuration

Copy `config.example.yaml` to `config.yaml` and customize:

```yaml
search:
  backend: auto
  results_per_query: 10
  use_johari_heuristic: true

analyzer:
  model: claude-sonnet-4-20250514
  strict_source_validation: false

output:
  output_dir: ./output
  formats: [html, json, markdown]
  generate_radar: true
```

## Johari Window Heuristic

The scanner uses the Johari Window as an internal sense-checking framework:

| Quadrant | Description | Search Strategy |
|----------|-------------|-----------------|
| **Open** | Well-documented dynamics | Reports, statistics, academic studies |
| **Blind** | Under-recognized implications | Cross-sector impacts, contrarian views |
| **Hidden** | Emerging signals | Patents, startups, preprints |
| **Unknown** | Genuine unknowns | Scenarios, wild cards, contested areas |

This heuristic informs search coverage but is not exposed in outputs—all results use the standard foresight structure.

## Source Quality

The scanner prioritizes credible, publicly available sources:

- **Tier 1**: Peer-reviewed journals (Nature, Science, etc.)
- **Tier 2**: Intergovernmental (UN, OECD, World Bank, WHO)
- **Tier 3**: Think tanks (Brookings, RAND, Chatham House)
- **Tier 4**: Industry research (Gartner, McKinsey, BCG)
- **Tier 5**: Established media (Reuters, FT, Economist)

## Programmatic Usage

```python
import asyncio
from src.cli import ForesightScanner
from src.utils import Config

# Create scanner with custom config
config = Config()
config.output.output_dir = "./my_output"
scanner = ForesightScanner(config=config)

# Run scan
phenomena = asyncio.run(scanner.scan_topic("renewable energy storage"))

# Generate outputs
outputs = scanner.generate_outputs(phenomena, title="Energy Futures")
print(f"Radar chart: {outputs['radar']}")
```

## Project Structure

```
ai-foresight-scanner/
├── src/
│   ├── models/           # Data models for phenomena
│   │   └── phenomenon.py # Core foresight card structure
│   ├── scraper/          # Web scraping and search
│   │   ├── web_scraper.py
│   │   ├── search_engine.py
│   │   └── source_validator.py
│   ├── analyzer/         # AI-powered analysis
│   │   ├── foresight_analyzer.py
│   │   └── prompts.py
│   ├── visualizer/       # Radar chart and reports
│   │   ├── radar_chart.py
│   │   └── html_generator.py
│   ├── utils/            # Configuration and logging
│   └── cli.py            # Command-line interface
├── output/               # Generated outputs
├── tests/                # Unit tests
├── config.example.yaml   # Example configuration
├── requirements.txt
└── pyproject.toml
```

## Principles

The scanner adheres to professional foresight standards:

- **Analytical Neutrality**: Operates without assuming specific organization or sector
- **Evidence-Based**: Distinguishes facts from assumptions, signals from trends
- **No Hype**: Avoids deterministic language and sensationalism
- **Uncertainty Acknowledgement**: Clearly states what is known vs unknown
- **Exploratory Scenarios**: Frames futures as alternatives, not predictions

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.
