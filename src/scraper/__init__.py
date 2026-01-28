"""
Web scraping and search module for the AI Foresight Scanner.
"""

from .web_scraper import WebScraper, ScrapedContent
from .search_engine import SearchEngine, SearchResult, SearchResponse
from .source_validator import SourceValidator, SourceValidation

__all__ = [
    "WebScraper",
    "ScrapedContent",
    "SearchEngine",
    "SearchResult",
    "SearchResponse",
    "SourceValidator",
    "SourceValidation",
]
