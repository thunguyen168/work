"""
Source validation for ensuring credibility of foresight sources.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from urllib.parse import urlparse


class SourceType(Enum):
    """Classification of source types by credibility tier."""
    PEER_REVIEWED = "peer_reviewed"           # Academic journals
    INTERGOVERNMENTAL = "intergovernmental"   # UN, OECD, World Bank, etc.
    GOVERNMENT = "government"                 # Government publications
    THINK_TANK = "think_tank"                 # Policy research institutes
    INDUSTRY_RESEARCH = "industry_research"   # Gartner, McKinsey, etc.
    ESTABLISHED_MEDIA = "established_media"   # Major reputable outlets
    TRADE_PUBLICATION = "trade_publication"   # Industry-specific publications
    GENERAL_WEB = "general_web"               # Other web sources
    UNKNOWN = "unknown"


@dataclass
class SourceValidation:
    """Result of source validation."""
    url: str
    source_type: SourceType
    credibility_score: float  # 0-1
    organization: str
    domain: str
    is_acceptable: bool
    warnings: list[str]


class SourceValidator:
    """
    Validates sources for credibility and appropriateness
    for foresight research.
    """

    # Domain classifications
    PEER_REVIEWED_DOMAINS = {
        "nature.com", "science.org", "sciencedirect.com", "springer.com",
        "wiley.com", "tandfonline.com", "jstor.org", "arxiv.org",
        "plos.org", "cell.com", "pnas.org", "oup.com", "sagepub.com",
        "mdpi.com", "frontiersin.org", "ieee.org", "acm.org",
    }

    INTERGOVERNMENTAL_DOMAINS = {
        "un.org", "who.int", "worldbank.org", "imf.org", "oecd.org",
        "wto.org", "iea.org", "ipcc.ch", "weforum.org", "ilo.org",
        "fao.org", "wipo.int", "unep.org", "unctad.org",
    }

    GOVERNMENT_PATTERNS = [
        r"\.gov$", r"\.gov\.", r"\.mil$", r"\.gc\.ca$",
        r"europa\.eu", r"\.gouv\.", r"\.gob\.",
    ]

    THINK_TANK_DOMAINS = {
        "brookings.edu", "rand.org", "cfr.org", "chathamhouse.org",
        "csis.org", "piie.com", "heritage.org", "aei.org",
        "pewresearch.org", "carnegieendowment.org", "wilsoncenter.org",
        "cato.org", "newamerica.org", "rusi.org", "iiasa.ac.at",
        "bruegel.org", "iiss.org", "atlanticcouncil.org",
    }

    INDUSTRY_RESEARCH_DOMAINS = {
        "mckinsey.com", "bcg.com", "bain.com", "deloitte.com",
        "pwc.com", "kpmg.com", "ey.com", "accenture.com",
        "gartner.com", "forrester.com", "idc.com", "ihs.com",
        "statista.com", "euromonitor.com",
    }

    ESTABLISHED_MEDIA_DOMAINS = {
        "reuters.com", "ft.com", "economist.com", "bloomberg.com",
        "bbc.com", "bbc.co.uk", "nytimes.com", "washingtonpost.com",
        "theguardian.com", "wsj.com", "apnews.com", "afp.com",
        "dw.com", "aljazeera.com", "scmp.com", "japantimes.co.jp",
    }

    TRADE_PUBLICATION_DOMAINS = {
        "techcrunch.com", "wired.com", "arstechnica.com",
        "technologyreview.com", "zdnet.com", "venturebeat.com",
        "hbr.org", "fastcompany.com", "forbes.com", "fortune.com",
        "scientificamerican.com", "newscientist.com",
    }

    # Warning patterns
    SUSPICIOUS_PATTERNS = [
        r"blog\.", r"wordpress\.com", r"medium\.com",
        r"substack\.com", r"tumblr\.com",
    ]

    POTENTIALLY_BIASED_PATTERNS = [
        r"(activist|advocacy|campaign)",
        r"(sponsored|advertorial|partner-content)",
    ]

    def __init__(self, strict_mode: bool = False):
        """
        Initialize the validator.

        Args:
            strict_mode: If True, only accept highest-tier sources
        """
        self.strict_mode = strict_mode

    def validate(self, url: str) -> SourceValidation:
        """
        Validate a source URL for credibility.

        Args:
            url: The URL to validate

        Returns:
            SourceValidation with assessment results
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        warnings = []

        # Classify source type
        source_type = self._classify_source(domain, url)

        # Calculate credibility score
        credibility_score = self._calculate_score(source_type, url)

        # Check for warnings
        warnings = self._check_warnings(url, domain)

        # Determine acceptability
        is_acceptable = self._is_acceptable(source_type, credibility_score)

        # Extract organization name
        organization = self._extract_organization(domain, source_type)

        return SourceValidation(
            url=url,
            source_type=source_type,
            credibility_score=credibility_score,
            organization=organization,
            domain=domain,
            is_acceptable=is_acceptable,
            warnings=warnings,
        )

    def _classify_source(self, domain: str, url: str) -> SourceType:
        """Classify the source type based on domain and URL patterns."""
        # Check exact domain matches first
        if domain in self.PEER_REVIEWED_DOMAINS:
            return SourceType.PEER_REVIEWED

        if domain in self.INTERGOVERNMENTAL_DOMAINS:
            return SourceType.INTERGOVERNMENTAL

        if domain in self.THINK_TANK_DOMAINS:
            return SourceType.THINK_TANK

        if domain in self.INDUSTRY_RESEARCH_DOMAINS:
            return SourceType.INDUSTRY_RESEARCH

        if domain in self.ESTABLISHED_MEDIA_DOMAINS:
            return SourceType.ESTABLISHED_MEDIA

        if domain in self.TRADE_PUBLICATION_DOMAINS:
            return SourceType.TRADE_PUBLICATION

        # Check patterns
        for pattern in self.GOVERNMENT_PATTERNS:
            if re.search(pattern, domain):
                return SourceType.GOVERNMENT

        # Check for academic domains
        if ".edu" in domain or ".ac." in domain:
            return SourceType.PEER_REVIEWED

        return SourceType.GENERAL_WEB

    def _calculate_score(self, source_type: SourceType, url: str) -> float:
        """Calculate credibility score based on source type."""
        base_scores = {
            SourceType.PEER_REVIEWED: 0.95,
            SourceType.INTERGOVERNMENTAL: 0.90,
            SourceType.GOVERNMENT: 0.85,
            SourceType.THINK_TANK: 0.80,
            SourceType.INDUSTRY_RESEARCH: 0.75,
            SourceType.ESTABLISHED_MEDIA: 0.70,
            SourceType.TRADE_PUBLICATION: 0.60,
            SourceType.GENERAL_WEB: 0.30,
            SourceType.UNKNOWN: 0.10,
        }

        score = base_scores.get(source_type, 0.10)

        # Adjust for URL quality indicators
        if "/research/" in url or "/publications/" in url:
            score = min(score + 0.05, 1.0)
        if "/report/" in url or "/study/" in url:
            score = min(score + 0.05, 1.0)
        if "/blog/" in url or "/opinion/" in url:
            score = max(score - 0.10, 0.0)

        return round(score, 2)

    def _check_warnings(self, url: str, domain: str) -> list[str]:
        """Check for potential issues with the source."""
        warnings = []

        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, url.lower()):
                warnings.append(f"URL matches pattern suggesting user-generated content")
                break

        # Check for potential bias indicators
        for pattern in self.POTENTIALLY_BIASED_PATTERNS:
            if re.search(pattern, url.lower()):
                warnings.append("URL contains patterns suggesting potential bias")
                break

        # Check for very long URLs (often low quality)
        if len(url) > 300:
            warnings.append("Unusually long URL may indicate low-quality source")

        return warnings

    def _is_acceptable(
        self,
        source_type: SourceType,
        credibility_score: float,
    ) -> bool:
        """Determine if source is acceptable for foresight research."""
        if self.strict_mode:
            acceptable_types = {
                SourceType.PEER_REVIEWED,
                SourceType.INTERGOVERNMENTAL,
                SourceType.GOVERNMENT,
                SourceType.THINK_TANK,
            }
            return source_type in acceptable_types

        # In normal mode, accept sources with sufficient credibility
        return credibility_score >= 0.50

    def _extract_organization(self, domain: str, source_type: SourceType) -> str:
        """Extract organization name from domain."""
        # Known organization mappings
        org_map = {
            "un.org": "United Nations",
            "who.int": "World Health Organization",
            "worldbank.org": "World Bank",
            "imf.org": "International Monetary Fund",
            "oecd.org": "OECD",
            "weforum.org": "World Economic Forum",
            "nature.com": "Nature",
            "science.org": "Science",
            "brookings.edu": "Brookings Institution",
            "rand.org": "RAND Corporation",
            "mckinsey.com": "McKinsey & Company",
            "gartner.com": "Gartner",
            "reuters.com": "Reuters",
            "economist.com": "The Economist",
            "ft.com": "Financial Times",
        }

        if domain in org_map:
            return org_map[domain]

        # Clean up domain as fallback
        org = domain.split(".")[0].replace("-", " ").title()
        return org

    def validate_batch(self, urls: list[str]) -> list[SourceValidation]:
        """
        Validate multiple URLs.

        Args:
            urls: List of URLs to validate

        Returns:
            List of validation results
        """
        return [self.validate(url) for url in urls]

    def filter_acceptable(
        self,
        urls: list[str],
        min_score: Optional[float] = None,
    ) -> list[tuple[str, SourceValidation]]:
        """
        Filter URLs to only acceptable sources.

        Args:
            urls: List of URLs to filter
            min_score: Optional minimum credibility score

        Returns:
            List of (url, validation) tuples for acceptable sources
        """
        results = []
        for url in urls:
            validation = self.validate(url)
            if validation.is_acceptable:
                if min_score is None or validation.credibility_score >= min_score:
                    results.append((url, validation))

        return sorted(results, key=lambda x: x[1].credibility_score, reverse=True)
