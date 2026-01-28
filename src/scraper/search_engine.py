"""
Search engine integration for discovering relevant content.

Supports multiple search backends and implements the Johari Window
heuristic for comprehensive coverage.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class JohariQuadrant(Enum):
    """
    Johari Window quadrants for sense-checking search coverage.

    Used as an internal heuristic to broaden coverage and reduce blind spots.
    Results are NOT labeled with these categories in output.
    """
    OPEN = "open"       # Well-documented dynamics, widely known
    BLIND = "blind"     # Widely discussed but under-recognized implications
    HIDDEN = "hidden"   # Emerging/sensitive signals with limited disclosure
    UNKNOWN = "unknown" # Genuine unknowns or contested uncertainties


@dataclass
class SearchResult:
    """A single search result."""
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[str] = None
    relevance_score: float = 0.0


@dataclass
class SearchResponse:
    """Container for search results."""
    query: str
    results: list[SearchResult]
    total_results: int
    search_timestamp: datetime
    johari_quadrant: Optional[JohariQuadrant] = None


class SearchBackend(ABC):
    """Abstract base class for search backends."""

    @abstractmethod
    async def search(
        self,
        query: str,
        num_results: int = 10,
        date_restrict: Optional[str] = None,
    ) -> SearchResponse:
        """Execute a search query."""
        pass


class BraveSearchBackend(SearchBackend):
    """
    Brave Search API backend.

    Requires BRAVE_API_KEY environment variable.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(
        self,
        query: str,
        num_results: int = 10,
        date_restrict: Optional[str] = None,
    ) -> SearchResponse:
        if not self.api_key:
            raise ValueError("BRAVE_API_KEY not set")

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }

        params = {
            "q": query,
            "count": num_results,
        }

        if date_restrict:
            params["freshness"] = date_restrict

        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url, headers=headers, params=params, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    source=item.get("meta_url", {}).get("hostname", ""),
                    published_date=item.get("age"),
                )
            )

        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_timestamp=datetime.now(),
        )


class SerperSearchBackend(SearchBackend):
    """
    Serper.dev Google Search API backend.

    Requires SERPER_API_KEY environment variable.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"

    async def search(
        self,
        query: str,
        num_results: int = 10,
        date_restrict: Optional[str] = None,
    ) -> SearchResponse:
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not set")

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "num": num_results,
        }

        if date_restrict:
            payload["tbs"] = f"qdr:{date_restrict}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url, headers=headers, json=payload, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("organic", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source=item.get("domain", ""),
                    published_date=item.get("date"),
                )
            )

        return SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_timestamp=datetime.now(),
        )


class SearchEngine:
    """
    Main search engine that coordinates search across backends
    and implements the Johari Window heuristic for comprehensive coverage.
    """

    # Credible source domains for foresight research
    CREDIBLE_DOMAINS = [
        # Intergovernmental
        "un.org", "oecd.org", "worldbank.org", "imf.org", "who.int",
        "weforum.org", "iea.org", "ipcc.ch",
        # Academic
        "nature.com", "science.org", "sciencedirect.com", "springer.com",
        "wiley.com", "tandfonline.com", "jstor.org", "arxiv.org",
        # Think tanks and research
        "brookings.edu", "rand.org", "cfr.org", "chathamhouse.org",
        "pewresearch.org", "mckinsey.com", "bcg.com", "bain.com",
        "gartner.com", "forrester.com", "idc.com",
        # Government and policy
        "gov.uk", "europa.eu", "state.gov", "congress.gov",
        # Reputable media (for current events)
        "reuters.com", "ft.com", "economist.com", "bloomberg.com",
        "bbc.com", "nytimes.com", "theguardian.com", "washingtonpost.com",
    ]

    def __init__(
        self,
        backend: Optional[SearchBackend] = None,
        preferred_domains: Optional[list[str]] = None,
    ):
        self.backend = backend or self._detect_backend()
        self.preferred_domains = preferred_domains or self.CREDIBLE_DOMAINS

    def _detect_backend(self) -> SearchBackend:
        """Detect available search backend from environment."""
        if os.getenv("SERPER_API_KEY"):
            return SerperSearchBackend()
        if os.getenv("BRAVE_API_KEY"):
            return BraveSearchBackend()
        raise ValueError(
            "No search API key found. Set SERPER_API_KEY or BRAVE_API_KEY."
        )

    def _generate_johari_queries(self, base_topic: str) -> dict[JohariQuadrant, list[str]]:
        """
        Generate search queries for each Johari Window quadrant.

        This heuristic helps ensure comprehensive coverage by actively
        looking for different types of information about a topic.
        """
        return {
            JohariQuadrant.OPEN: [
                # Well-documented dynamics
                f"{base_topic} trend report 2024 2025",
                f"{base_topic} market research statistics",
                f"{base_topic} industry analysis forecast",
                f"{base_topic} academic study peer reviewed",
            ],
            JohariQuadrant.BLIND: [
                # Under-recognized implications
                f"{base_topic} unintended consequences",
                f"{base_topic} hidden risks overlooked",
                f"{base_topic} second order effects",
                f"{base_topic} unexpected implications",
            ],
            JohariQuadrant.HIDDEN: [
                # Emerging or sensitive signals
                f"{base_topic} emerging weak signals",
                f"{base_topic} early indicators disruption",
                f"{base_topic} startup innovation breakthrough",
                f"{base_topic} patent filing new technology",
            ],
            JohariQuadrant.UNKNOWN: [
                # Genuine unknowns
                f"{base_topic} wildcard scenario uncertainty",
                f"{base_topic} unknown unknowns black swan",
                f"{base_topic} contested debate controversy",
                f"{base_topic} future scenarios speculation",
            ],
        }

    async def comprehensive_search(
        self,
        topic: str,
        results_per_quadrant: int = 5,
    ) -> dict[JohariQuadrant, list[SearchResponse]]:
        """
        Execute comprehensive search using Johari Window heuristic.

        Args:
            topic: The foresight topic to research
            results_per_quadrant: Number of results per search query

        Returns:
            Dictionary mapping quadrants to search responses
        """
        queries = self._generate_johari_queries(topic)
        results: dict[JohariQuadrant, list[SearchResponse]] = {}

        for quadrant, query_list in queries.items():
            quadrant_results = []
            for query in query_list:
                try:
                    response = await self.backend.search(
                        query, num_results=results_per_quadrant
                    )
                    response.johari_quadrant = quadrant
                    quadrant_results.append(response)
                    logger.info(f"[{quadrant.value}] Query '{query}': {len(response.results)} results")
                except Exception as e:
                    logger.warning(f"Search failed for '{query}': {e}")
            results[quadrant] = quadrant_results

        return results

    async def targeted_search(
        self,
        query: str,
        num_results: int = 20,
        site_restrict: Optional[list[str]] = None,
    ) -> SearchResponse:
        """
        Execute a targeted search with optional site restriction.

        Args:
            query: Search query
            num_results: Maximum results to return
            site_restrict: Optional list of domains to restrict to

        Returns:
            SearchResponse with results
        """
        if site_restrict:
            sites = " OR ".join(f"site:{domain}" for domain in site_restrict)
            query = f"({query}) ({sites})"

        return await self.backend.search(query, num_results=num_results)

    async def search_credible_sources(
        self,
        topic: str,
        num_results: int = 20,
    ) -> SearchResponse:
        """
        Search only credible, authoritative sources.

        Args:
            topic: Topic to search for
            num_results: Maximum results

        Returns:
            SearchResponse with results from credible sources
        """
        return await self.targeted_search(
            topic,
            num_results=num_results,
            site_restrict=self.preferred_domains[:15],  # Limit site: operators
        )

    def filter_by_credibility(
        self,
        results: list[SearchResult],
        min_score: float = 0.5,
    ) -> list[SearchResult]:
        """
        Filter search results by source credibility.

        Args:
            results: List of search results
            min_score: Minimum credibility score (0-1)

        Returns:
            Filtered list of credible results
        """
        filtered = []
        for result in results:
            score = self._calculate_credibility_score(result)
            if score >= min_score:
                result.relevance_score = score
                filtered.append(result)

        return sorted(filtered, key=lambda x: x.relevance_score, reverse=True)

    def _calculate_credibility_score(self, result: SearchResult) -> float:
        """
        Calculate credibility score for a search result.

        Factors:
        - Domain reputation
        - URL patterns (academic, government, etc.)
        - Content indicators
        """
        score = 0.3  # Base score

        # Domain reputation
        for domain in self.preferred_domains:
            if domain in result.url:
                score += 0.4
                break

        # Academic/research indicators
        academic_patterns = [".edu", ".ac.", "research", "journal", "study"]
        for pattern in academic_patterns:
            if pattern in result.url.lower():
                score += 0.1
                break

        # Government/intergovernmental indicators
        gov_patterns = [".gov", ".int", ".eu", "official"]
        for pattern in gov_patterns:
            if pattern in result.url.lower():
                score += 0.1
                break

        # Date freshness (prefer recent)
        if result.published_date:
            score += 0.1

        return min(score, 1.0)

    def deduplicate_results(
        self,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        """Remove duplicate URLs from results."""
        seen_urls = set()
        unique = []
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique.append(result)
        return unique
