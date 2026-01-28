"""
AI-powered foresight analyzer that structures information into
the card-based foresight format.
"""

import json
import logging
import os
import re
import uuid
from datetime import datetime
from typing import Any, Optional

from anthropic import Anthropic

from ..models import (
    DevelopmentPath,
    Driver,
    ImpactAssessment,
    Phenomenon,
    PhenomenonType,
    Scenario,
    Source,
    ThematicTag,
    TimeHorizon,
    TimingAssessment,
)
from ..scraper import ScrapedContent, SearchResult, SourceValidator
from .prompts import ForesightPrompts

logger = logging.getLogger(__name__)


class ForesightAnalyzer:
    """
    AI-powered analyzer that transforms raw web content into
    structured foresight phenomena.

    Uses Claude API for intelligent analysis and structuring.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514",
        source_validator: Optional[SourceValidator] = None,
    ):
        """
        Initialize the analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Claude model to use
            source_validator: Optional source validator instance
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.source_validator = source_validator or SourceValidator()
        self.prompts = ForesightPrompts()

    def _call_llm(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """
        Make a call to the Claude API.

        Args:
            prompt: User prompt
            system: Optional system prompt
            max_tokens: Maximum tokens in response

        Returns:
            Model response text
        """
        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system or self.prompts.SYSTEM_PROMPT,
            messages=messages,
        )

        return response.content[0].text

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """
        Parse JSON from LLM response, handling markdown code blocks.

        Args:
            response: Raw LLM response

        Returns:
            Parsed JSON dictionary
        """
        # Try to extract JSON from code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # Try to find JSON directly
            json_str = response.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Try to fix common issues
            json_str = re.sub(r",\s*}", "}", json_str)
            json_str = re.sub(r",\s*]", "]", json_str)
            return json.loads(json_str)

    def _prepare_content_for_analysis(
        self,
        scraped_contents: list[ScrapedContent],
        search_results: list[SearchResult],
    ) -> tuple[str, str]:
        """
        Prepare scraped content and search results for analysis.

        Returns:
            Tuple of (content_text, sources_text)
        """
        content_parts = []
        source_parts = []

        # Add scraped content
        for sc in scraped_contents:
            if sc.success and sc.content:
                content_parts.append(f"## {sc.title}\n\n{sc.content[:3000]}")
                source_parts.append(f"- [{sc.title}]({sc.url}) ({sc.organization})")

        # Add search result snippets
        for sr in search_results:
            if sr.snippet:
                content_parts.append(f"## {sr.title}\n\n{sr.snippet}")
                if sr.url not in [s.url for s in scraped_contents if s.success]:
                    source_parts.append(f"- [{sr.title}]({sr.url}) ({sr.source})")

        content_text = "\n\n---\n\n".join(content_parts)
        sources_text = "\n".join(source_parts)

        return content_text, sources_text

    def _create_sources_from_results(
        self,
        scraped_contents: list[ScrapedContent],
        search_results: list[SearchResult],
    ) -> list[Source]:
        """Create Source objects from scraped content and search results."""
        sources = []
        seen_urls = set()

        for sc in scraped_contents:
            if sc.success and sc.url not in seen_urls:
                validation = self.source_validator.validate(sc.url)
                sources.append(
                    Source(
                        title=sc.title,
                        url=sc.url,
                        source_type=validation.source_type.value,
                        publication_date=sc.publication_date,
                        organization=sc.organization,
                    )
                )
                seen_urls.add(sc.url)

        for sr in search_results:
            if sr.url not in seen_urls:
                validation = self.source_validator.validate(sr.url)
                sources.append(
                    Source(
                        title=sr.title,
                        url=sr.url,
                        source_type=validation.source_type.value,
                        publication_date=sr.published_date,
                        organization=sr.source,
                    )
                )
                seen_urls.add(sr.url)

        return sources

    async def analyze_phenomenon(
        self,
        query: str,
        scraped_contents: list[ScrapedContent],
        search_results: list[SearchResult],
    ) -> Phenomenon:
        """
        Analyze gathered content and create a structured Phenomenon.

        Args:
            query: Original search query
            scraped_contents: List of scraped web content
            search_results: List of search results

        Returns:
            Structured Phenomenon object
        """
        # Prepare content
        content_text, sources_text = self._prepare_content_for_analysis(
            scraped_contents, search_results
        )

        # Create source objects
        sources = self._create_sources_from_results(scraped_contents, search_results)

        # Step 1: Generate title
        logger.info("Generating title...")
        title = self._generate_title(content_text)

        # Step 2: Classify phenomenon
        logger.info("Classifying phenomenon...")
        classification = self._classify_phenomenon(content_text, sources_text)

        # Step 3: Generate summary
        logger.info("Generating summary...")
        summary = self._generate_summary(
            title, classification["phenomenon_type"], content_text, sources_text
        )

        # Step 4: Analyze drivers
        logger.info("Analyzing drivers...")
        drivers = self._analyze_drivers(title, summary, content_text)

        # Step 5: Generate timing assessment
        logger.info("Assessing timing...")
        timing = self._assess_timing(
            title,
            classification["phenomenon_type"],
            summary,
            drivers,
        )

        # Step 6: Generate scenarios
        logger.info("Generating scenarios...")
        scenarios = self._generate_scenarios(
            title, summary, drivers, classification.get("time_horizon", "mid_term")
        )

        # Step 7: Analyze connections
        logger.info("Analyzing connections...")
        connections = self._analyze_connections(title, summary, scenarios)

        # Build the Phenomenon object
        phenomenon = Phenomenon(
            id=str(uuid.uuid4()),
            title=title,
            tags=self._parse_tags(classification.get("tags", [])),
            phenomenon_type=self._parse_phenomenon_type(
                classification["phenomenon_type"]
            ),
            timing=timing,
            summary=summary,
            background="",  # Can be populated with additional content
            sources=sources,
            drivers=drivers,
            scenarios=scenarios,
            related_phenomena=[c["phenomenon"] for c in connections.get("related_phenomena", [])],
            second_order_effects=connections.get("second_order_effects", []),
            areas_for_exploration=connections.get("areas_for_exploration", []),
            additional_readings=[],
            confidence_level=classification.get("confidence_level", "moderate"),
            data_quality="mixed",
            scan_query=query,
        )

        # Calculate radar position
        phenomenon.calculate_radar_position()

        return phenomenon

    def _generate_title(self, content: str) -> str:
        """Generate a concise title for the phenomenon."""
        prompt = self.prompts.TITLE_GENERATION.format(content=content[:2000])
        response = self._call_llm(prompt, max_tokens=100)
        return response.strip().strip('"').strip("'")

    def _classify_phenomenon(
        self, content: str, sources: str
    ) -> dict[str, Any]:
        """Classify the phenomenon type and characteristics."""
        prompt = self.prompts.PHENOMENON_CLASSIFICATION.format(
            content=content[:4000], sources=sources
        )
        response = self._call_llm(prompt)
        return self._parse_json_response(response)

    def _generate_summary(
        self,
        title: str,
        phenomenon_type: str,
        content: str,
        sources: str,
    ) -> str:
        """Generate the main summary paragraph."""
        prompt = self.prompts.SUMMARY_GENERATION.format(
            title=title,
            phenomenon_type=phenomenon_type,
            content=content[:4000],
            sources=sources,
        )
        return self._call_llm(prompt)

    def _analyze_drivers(
        self, title: str, summary: str, content: str
    ) -> list[Driver]:
        """Analyze key drivers of the phenomenon."""
        prompt = self.prompts.DRIVER_ANALYSIS.format(
            title=title, summary=summary, content=content[:3000]
        )
        response = self._call_llm(prompt)
        data = self._parse_json_response(response)

        drivers = []
        for d in data.get("drivers", []):
            drivers.append(
                Driver(
                    name=d["name"],
                    description=d["description"],
                    category=d["category"],
                    strength=d["strength"],
                    sources=[],  # Could be populated from source_references
                )
            )
        return drivers

    def _assess_timing(
        self,
        title: str,
        phenomenon_type: str,
        summary: str,
        drivers: list[Driver],
    ) -> TimingAssessment:
        """Generate timing assessment for the phenomenon."""
        drivers_text = "\n".join(
            [f"- {d.name}: {d.description} (strength: {d.strength})" for d in drivers]
        )

        prompt = self.prompts.TIMING_ASSESSMENT.format(
            title=title,
            phenomenon_type=phenomenon_type,
            summary=summary,
            drivers=drivers_text,
        )
        response = self._call_llm(prompt)
        data = self._parse_json_response(response)

        horizon_map = {
            "near_term": TimeHorizon.NEAR_TERM,
            "mid_term": TimeHorizon.MID_TERM,
            "long_term": TimeHorizon.LONG_TERM,
            "uncertain": TimeHorizon.UNCERTAIN,
        }

        return TimingAssessment(
            primary_horizon=horizon_map.get(
                data.get("primary_horizon", "mid_term"), TimeHorizon.MID_TERM
            ),
            acceleration_phase=data.get("acceleration_phase"),
            peak_phase=data.get("peak_phase"),
            decline_phase=data.get("decline_phase"),
            rationale=data.get("rationale", ""),
            uncertainty_acknowledgement=data.get("uncertainty_acknowledgement", ""),
        )

    def _generate_scenarios(
        self,
        title: str,
        summary: str,
        drivers: list[Driver],
        time_horizon: str,
    ) -> list[Scenario]:
        """Generate contrasting future scenarios."""
        drivers_text = "\n".join(
            [f"- {d.name} ({d.category}): {d.description}" for d in drivers]
        )

        prompt = self.prompts.SCENARIO_GENERATION.format(
            title=title,
            summary=summary,
            drivers=drivers_text,
            time_horizon=time_horizon,
        )
        response = self._call_llm(prompt)
        data = self._parse_json_response(response)

        scenarios = []
        for s in data.get("scenarios", []):
            impact = s.get("impact_assessment", {})
            dev_path = []
            for dp in s.get("development_path", []):
                dev_path.append(
                    DevelopmentPath(
                        step_number=dp.get("step_number", len(dev_path) + 1),
                        description=dp.get("description", ""),
                        indicative_timeline=dp.get("indicative_timeline", ""),
                        indicators_to_monitor=dp.get("indicators_to_monitor", []),
                    )
                )

            scenarios.append(
                Scenario(
                    name=s.get("name", ""),
                    description=s.get("description", ""),
                    probability_assessment=s.get("probability_assessment", "possible"),
                    impact_assessment=ImpactAssessment(
                        risks=impact.get("risks", []),
                        opportunities=impact.get("opportunities", []),
                        affected_sectors=impact.get("affected_sectors", []),
                        affected_stakeholders=impact.get("affected_stakeholders", []),
                    ),
                    development_path=dev_path,
                    key_assumptions=s.get("key_assumptions", []),
                )
            )
        return scenarios

    def _analyze_connections(
        self,
        title: str,
        summary: str,
        scenarios: list[Scenario],
    ) -> dict[str, Any]:
        """Analyze connections and implications."""
        scenarios_text = "\n".join(
            [f"- {s.name}: {s.description[:200]}..." for s in scenarios]
        )

        prompt = self.prompts.CONNECTIONS_ANALYSIS.format(
            title=title, summary=summary, scenarios=scenarios_text
        )
        response = self._call_llm(prompt)
        return self._parse_json_response(response)

    def _parse_tags(self, tags: list[str]) -> list[ThematicTag]:
        """Parse tag strings to ThematicTag enums."""
        tag_map = {
            "technology": ThematicTag.TECHNOLOGY,
            "society": ThematicTag.SOCIETY,
            "economy": ThematicTag.ECONOMY,
            "environment": ThematicTag.ENVIRONMENT,
            "geopolitics": ThematicTag.GEOPOLITICS,
            "health": ThematicTag.HEALTH,
            "governance": ThematicTag.GOVERNANCE,
            "security": ThematicTag.SECURITY,
            "demographics": ThematicTag.DEMOGRAPHICS,
            "culture": ThematicTag.CULTURE,
        }

        result = []
        for tag in tags:
            tag_lower = tag.lower().strip()
            if tag_lower in tag_map:
                result.append(tag_map[tag_lower])
        return result

    def _parse_phenomenon_type(self, type_str: str) -> PhenomenonType:
        """Parse phenomenon type string to enum."""
        type_map = {
            "strengthening": PhenomenonType.STRENGTHENING,
            "weakening": PhenomenonType.WEAKENING,
            "weak_signal": PhenomenonType.WEAK_SIGNAL,
            "wild_card": PhenomenonType.WILD_CARD,
        }
        return type_map.get(type_str.lower(), PhenomenonType.WEAK_SIGNAL)

    def quality_check(self, phenomenon: Phenomenon) -> dict[str, Any]:
        """
        Run a quality check on the generated phenomenon.

        Args:
            phenomenon: The phenomenon to check

        Returns:
            Quality check results
        """
        analysis_json = json.dumps(phenomenon.to_dict(), indent=2)
        prompt = self.prompts.QUALITY_CHECK.format(analysis=analysis_json)
        response = self._call_llm(prompt)
        return self._parse_json_response(response)
