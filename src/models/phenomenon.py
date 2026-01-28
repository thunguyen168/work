"""
Core data models for foresight phenomena (trends, weak signals, disruptions).

These models implement the card-based foresight format suitable for strategy
and risk discussions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class PhenomenonType(Enum):
    """Classification of the phenomenon's trajectory."""
    STRENGTHENING = "strengthening"  # Growing trend with increasing momentum
    WEAKENING = "weakening"          # Declining trend losing momentum
    WEAK_SIGNAL = "weak_signal"      # Early indicator, uncertain trajectory
    WILD_CARD = "wild_card"          # Low probability, high impact event


class TimeHorizon(Enum):
    """Time bands for phenomenon timing assessment."""
    NEAR_TERM = "near_term"      # 0-5 years
    MID_TERM = "mid_term"        # 5-10 years
    LONG_TERM = "long_term"      # 10-20 years
    UNCERTAIN = "uncertain"      # For weak signals with unclear timing


class ThematicTag(Enum):
    """High-level thematic categories for phenomena."""
    TECHNOLOGY = "technology"
    SOCIETY = "society"
    ECONOMY = "economy"
    ENVIRONMENT = "environment"
    GEOPOLITICS = "geopolitics"
    HEALTH = "health"
    GOVERNANCE = "governance"
    SECURITY = "security"
    DEMOGRAPHICS = "demographics"
    CULTURE = "culture"


@dataclass
class Source:
    """A credible, hyperlinked source for evidence."""
    title: str
    url: str
    source_type: str  # e.g., "peer-reviewed", "intergovernmental", "think tank"
    publication_date: Optional[str] = None
    organization: Optional[str] = None

    def to_markdown_link(self) -> str:
        """Return a markdown formatted hyperlink."""
        return f"[{self.title}]({self.url})"


@dataclass
class Driver:
    """
    Key underlying force shaping a phenomenon's trajectory.

    Drivers can be technological, social, economic, environmental,
    or political in nature.
    """
    name: str
    description: str
    category: str  # STEEP+G category
    strength: str  # "strong", "moderate", "emerging"
    sources: list[Source] = field(default_factory=list)


@dataclass
class DevelopmentPath:
    """
    A concrete step or milestone toward a scenario.

    These are framed as signs and indicators to monitor over time.
    """
    step_number: int
    description: str
    indicative_timeline: str  # e.g., "2025-2027", "Within 3 years"
    indicators_to_monitor: list[str] = field(default_factory=list)


@dataclass
class ImpactAssessment:
    """
    Assessment of implications for organizations and systems.
    """
    risks: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    affected_sectors: list[str] = field(default_factory=list)
    affected_stakeholders: list[str] = field(default_factory=list)


@dataclass
class Scenario:
    """
    A plausible future direction for a phenomenon.

    Scenarios are exploratory, not predictive, and represent
    contrasting but plausible alternatives.
    """
    name: str
    description: str
    probability_assessment: str  # qualitative: "plausible", "possible", "emerging"
    impact_assessment: ImpactAssessment
    development_path: list[DevelopmentPath] = field(default_factory=list)
    key_assumptions: list[str] = field(default_factory=list)


@dataclass
class TimingAssessment:
    """
    Expert-style assessment of when the phenomenon is most likely
    to accelerate, peak, or decline.
    """
    primary_horizon: TimeHorizon
    acceleration_phase: Optional[str] = None  # When momentum builds
    peak_phase: Optional[str] = None          # When at maximum influence
    decline_phase: Optional[str] = None       # When waning
    rationale: str = ""
    uncertainty_acknowledgement: str = ""


@dataclass
class Phenomenon:
    """
    Core foresight card representing a trend, weak signal, or potential disruption.

    This is the primary data structure for the foresight scanning tool,
    implementing a consistent, card-based format suitable for strategy
    and risk discussions.
    """
    # Identity
    id: str
    title: str
    tags: list[ThematicTag]

    # Classification
    phenomenon_type: PhenomenonType
    timing: Optional[TimingAssessment] = None

    # Core content
    summary: str = ""  # Single paragraph overview
    background: str = ""  # Extended context
    sources: list[Source] = field(default_factory=list)

    # Analysis
    drivers: list[Driver] = field(default_factory=list)
    scenarios: list[Scenario] = field(default_factory=list)

    # Connections
    related_phenomena: list[str] = field(default_factory=list)
    second_order_effects: list[str] = field(default_factory=list)
    areas_for_exploration: list[str] = field(default_factory=list)
    additional_readings: list[Source] = field(default_factory=list)

    # Metadata
    confidence_level: str = "moderate"  # low, moderate, high
    data_quality: str = "mixed"         # limited, mixed, robust
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    scan_query: str = ""  # Original query that generated this

    # Visualization positioning
    radar_distance: float = 0.5  # 0.0 = center (present), 1.0 = edge (far future)
    radar_angle: float = 0.0     # Position on the radar (0-360 degrees)

    def get_horizon_years(self) -> tuple[int, int]:
        """Return the year range for this phenomenon's timing."""
        current_year = datetime.now().year
        if self.timing is None or self.timing.primary_horizon == TimeHorizon.UNCERTAIN:
            return (current_year, current_year + 20)

        horizon_map = {
            TimeHorizon.NEAR_TERM: (current_year, current_year + 5),
            TimeHorizon.MID_TERM: (current_year + 5, current_year + 10),
            TimeHorizon.LONG_TERM: (current_year + 10, current_year + 20),
        }
        return horizon_map.get(self.timing.primary_horizon, (current_year, current_year + 20))

    def calculate_radar_position(self) -> None:
        """Calculate radar visualization position based on timing and type."""
        # Distance from center based on time horizon
        horizon_distances = {
            TimeHorizon.NEAR_TERM: 0.25,
            TimeHorizon.MID_TERM: 0.55,
            TimeHorizon.LONG_TERM: 0.85,
            TimeHorizon.UNCERTAIN: 0.7,
        }

        if self.timing:
            self.radar_distance = horizon_distances.get(
                self.timing.primary_horizon, 0.5
            )

        # Adjust for phenomenon type
        if self.phenomenon_type == PhenomenonType.WILD_CARD:
            self.radar_distance = min(self.radar_distance + 0.1, 0.95)
        elif self.phenomenon_type == PhenomenonType.WEAK_SIGNAL:
            self.radar_distance = min(self.radar_distance + 0.05, 0.9)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "tags": [t.value for t in self.tags],
            "phenomenon_type": self.phenomenon_type.value,
            "timing": {
                "primary_horizon": self.timing.primary_horizon.value if self.timing else None,
                "acceleration_phase": self.timing.acceleration_phase if self.timing else None,
                "peak_phase": self.timing.peak_phase if self.timing else None,
                "decline_phase": self.timing.decline_phase if self.timing else None,
                "rationale": self.timing.rationale if self.timing else "",
                "uncertainty_acknowledgement": self.timing.uncertainty_acknowledgement if self.timing else "",
            } if self.timing else None,
            "summary": self.summary,
            "background": self.background,
            "sources": [
                {
                    "title": s.title,
                    "url": s.url,
                    "source_type": s.source_type,
                    "publication_date": s.publication_date,
                    "organization": s.organization,
                }
                for s in self.sources
            ],
            "drivers": [
                {
                    "name": d.name,
                    "description": d.description,
                    "category": d.category,
                    "strength": d.strength,
                    "sources": [{"title": s.title, "url": s.url} for s in d.sources],
                }
                for d in self.drivers
            ],
            "scenarios": [
                {
                    "name": s.name,
                    "description": s.description,
                    "probability_assessment": s.probability_assessment,
                    "impact_assessment": {
                        "risks": s.impact_assessment.risks,
                        "opportunities": s.impact_assessment.opportunities,
                        "affected_sectors": s.impact_assessment.affected_sectors,
                        "affected_stakeholders": s.impact_assessment.affected_stakeholders,
                    },
                    "development_path": [
                        {
                            "step_number": dp.step_number,
                            "description": dp.description,
                            "indicative_timeline": dp.indicative_timeline,
                            "indicators_to_monitor": dp.indicators_to_monitor,
                        }
                        for dp in s.development_path
                    ],
                    "key_assumptions": s.key_assumptions,
                }
                for s in self.scenarios
            ],
            "related_phenomena": self.related_phenomena,
            "second_order_effects": self.second_order_effects,
            "areas_for_exploration": self.areas_for_exploration,
            "additional_readings": [
                {"title": r.title, "url": r.url}
                for r in self.additional_readings
            ],
            "confidence_level": self.confidence_level,
            "data_quality": self.data_quality,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "scan_query": self.scan_query,
            "radar_distance": self.radar_distance,
            "radar_angle": self.radar_angle,
        }
