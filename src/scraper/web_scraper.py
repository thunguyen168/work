"""
Web scraping functionality for fetching and processing web content.
"""

import asyncio
import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ScrapedContent:
    """Container for scraped web content."""
    url: str
    title: str
    content: str
    publication_date: Optional[str]
    author: Optional[str]
    organization: Optional[str]
    fetch_timestamp: datetime
    content_hash: str
    word_count: int
    success: bool
    error_message: Optional[str] = None


class WebScraper:
    """
    Async web scraper for fetching and processing content from URLs.

    Features:
    - Async fetching for parallel requests
    - Content extraction and cleaning
    - Metadata extraction (title, date, author)
    - Caching to avoid duplicate fetches
    - Rate limiting to respect servers
    """

    def __init__(
        self,
        timeout: int = 30,
        max_concurrent: int = 5,
        cache_ttl_minutes: int = 60,
        user_agent: str = "AI-Foresight-Scanner/1.0 (Research Tool)",
    ):
        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.user_agent = user_agent
        self._cache: dict[str, tuple[ScrapedContent, datetime]] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)

    def _get_cache_key(self, url: str) -> str:
        """Generate a cache key for a URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _is_cached(self, url: str) -> bool:
        """Check if URL content is in cache and still valid."""
        key = self._get_cache_key(url)
        if key in self._cache:
            _, timestamp = self._cache[key]
            if datetime.now() - timestamp < self.cache_ttl:
                return True
            del self._cache[key]
        return False

    def _get_cached(self, url: str) -> Optional[ScrapedContent]:
        """Get cached content if available."""
        if self._is_cached(url):
            key = self._get_cache_key(url)
            return self._cache[key][0]
        return None

    def _cache_content(self, content: ScrapedContent) -> None:
        """Cache scraped content."""
        key = self._get_cache_key(content.url)
        self._cache[key] = (content, datetime.now())

    async def fetch_url(self, url: str, session: aiohttp.ClientSession) -> ScrapedContent:
        """
        Fetch and process content from a single URL.

        Args:
            url: The URL to fetch
            session: aiohttp session for making requests

        Returns:
            ScrapedContent with extracted information
        """
        # Check cache first
        cached = self._get_cached(url)
        if cached:
            logger.debug(f"Cache hit for {url}")
            return cached

        async with self._semaphore:
            try:
                headers = {"User-Agent": self.user_agent}
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=self.timeout), headers=headers
                ) as response:
                    if response.status != 200:
                        return ScrapedContent(
                            url=url,
                            title="",
                            content="",
                            publication_date=None,
                            author=None,
                            organization=None,
                            fetch_timestamp=datetime.now(),
                            content_hash="",
                            word_count=0,
                            success=False,
                            error_message=f"HTTP {response.status}",
                        )

                    html = await response.text()
                    content = self._extract_content(html, url)
                    self._cache_content(content)
                    return content

            except asyncio.TimeoutError:
                return self._error_content(url, "Request timeout")
            except aiohttp.ClientError as e:
                return self._error_content(url, f"Client error: {str(e)}")
            except Exception as e:
                return self._error_content(url, f"Unexpected error: {str(e)}")

    def _error_content(self, url: str, error_message: str) -> ScrapedContent:
        """Create an error ScrapedContent."""
        return ScrapedContent(
            url=url,
            title="",
            content="",
            publication_date=None,
            author=None,
            organization=None,
            fetch_timestamp=datetime.now(),
            content_hash="",
            word_count=0,
            success=False,
            error_message=error_message,
        )

    def _extract_content(self, html: str, url: str) -> ScrapedContent:
        """
        Extract meaningful content from HTML.

        Args:
            html: Raw HTML content
            url: Source URL for metadata extraction

        Returns:
            ScrapedContent with extracted and cleaned data
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "aside", "header"]):
            element.decompose()

        # Extract title
        title = self._extract_title(soup)

        # Extract main content
        content = self._extract_main_content(soup)

        # Extract metadata
        publication_date = self._extract_date(soup)
        author = self._extract_author(soup)
        organization = self._extract_organization(url, soup)

        # Calculate content hash and word count
        content_hash = hashlib.md5(content.encode()).hexdigest()
        word_count = len(content.split())

        return ScrapedContent(
            url=url,
            title=title,
            content=content,
            publication_date=publication_date,
            author=author,
            organization=organization,
            fetch_timestamp=datetime.now(),
            content_hash=content_hash,
            word_count=word_count,
            success=True,
        )

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        # Try og:title first
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Try title tag
        title_tag = soup.find("title")
        if title_tag:
            return title_tag.get_text().strip()

        # Try h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text().strip()

        return ""

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content text."""
        # Try common article containers
        content_selectors = [
            "article",
            "[role='main']",
            ".content",
            ".article-content",
            ".post-content",
            "#content",
            "main",
        ]

        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator=" ", strip=True)
                if len(text) > 200:  # Minimum content threshold
                    return self._clean_text(text)

        # Fallback to body
        body = soup.find("body")
        if body:
            return self._clean_text(body.get_text(separator=" ", strip=True))

        return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove multiple spaces and newlines
        text = re.sub(r"\s+", " ", text)
        # Remove common noise patterns
        text = re.sub(r"(Cookie|Privacy|Terms|Subscribe|Sign up|Newsletter)\s*\|?", "", text, flags=re.IGNORECASE)
        return text.strip()

    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract publication date."""
        # Try meta tags
        date_meta_names = [
            "article:published_time",
            "datePublished",
            "date",
            "DC.date",
            "publishDate",
        ]

        for name in date_meta_names:
            meta = soup.find("meta", {"property": name}) or soup.find("meta", {"name": name})
            if meta and meta.get("content"):
                return meta["content"]

        # Try time element
        time_elem = soup.find("time")
        if time_elem:
            return time_elem.get("datetime") or time_elem.get_text().strip()

        return None

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author information."""
        # Try meta tags
        author_meta = soup.find("meta", {"name": "author"}) or soup.find("meta", {"property": "article:author"})
        if author_meta and author_meta.get("content"):
            return author_meta["content"]

        # Try common author elements
        author_selectors = [".author", ".byline", "[rel='author']"]
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text().strip()

        return None

    def _extract_organization(self, url: str, soup: BeautifulSoup) -> Optional[str]:
        """Extract organization/publisher information."""
        # Try og:site_name
        site_name = soup.find("meta", property="og:site_name")
        if site_name and site_name.get("content"):
            return site_name["content"]

        # Fall back to domain name
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain

    async def fetch_multiple(self, urls: list[str]) -> list[ScrapedContent]:
        """
        Fetch multiple URLs concurrently.

        Args:
            urls: List of URLs to fetch

        Returns:
            List of ScrapedContent results
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url(url, session) for url in urls]
            return await asyncio.gather(*tasks)

    def fetch_sync(self, urls: list[str]) -> list[ScrapedContent]:
        """
        Synchronous wrapper for fetching multiple URLs.

        Args:
            urls: List of URLs to fetch

        Returns:
            List of ScrapedContent results
        """
        return asyncio.run(self.fetch_multiple(urls))
