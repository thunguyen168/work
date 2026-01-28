"""
AI Foresight Scanner

An AI-enabled tool that scrapes the web to identify, structure, and monitor
future-oriented phenomena (trends, weak signals, and potential disruptions)
in a consistent, card-based foresight format.
"""

__version__ = "1.0.0"
__author__ = "AI Foresight Scanner Team"

from .models import (
    Phenomenon,
    PhenomenonType,
    TimeHorizon,
    ThematicTag,
    TimingAssessment,
    Scenario,
    Driver,
    ImpactAssessment,
    DevelopmentPath,
    Source,
)

from .scraper import (
    WebScraper,
    SearchEngine,
    SourceValidator,
)

from .analyzer import (
    ForesightAnalyzer,
    ForesightPrompts,
)

from .visualizer import (
    RadarChart,
    HTMLReportGenerator,
)

__all__ = [
    # Models
    "Phenomenon",
    "PhenomenonType",
    "TimeHorizon",
    "ThematicTag",
    "TimingAssessment",
    "Scenario",
    "Driver",
    "ImpactAssessment",
    "DevelopmentPath",
    "Source",
    # Scraper
    "WebScraper",
    "SearchEngine",
    "SourceValidator",
    # Analyzer
    "ForesightAnalyzer",
    "ForesightPrompts",
    # Visualizer
    "RadarChart",
    "HTMLReportGenerator",
]
