"""
Tests for foresight phenomenon models.
"""

import pytest
from datetime import datetime

from src.models import (
    Phenomenon,
    PhenomenonType,
    TimeHorizon,
    ThematicTag,
    Source,
    Driver,
    Scenario,
    ImpactAssessment,
    DevelopmentPath,
    TimingAssessment,
)


class TestSource:
    """Tests for Source model."""

    def test_source_creation(self):
        source = Source(
            title="Test Report",
            url="https://example.com/report",
            source_type="peer_reviewed",
            organization="Example Org",
        )
        assert source.title == "Test Report"
        assert source.url == "https://example.com/report"

    def test_source_markdown_link(self):
        source = Source(
            title="Test Report",
            url="https://example.com/report",
            source_type="peer_reviewed",
        )
        assert source.to_markdown_link() == "[Test Report](https://example.com/report)"


class TestDriver:
    """Tests for Driver model."""

    def test_driver_creation(self):
        driver = Driver(
            name="AI Advancement",
            description="Rapid progress in machine learning",
            category="technological",
            strength="strong",
        )
        assert driver.name == "AI Advancement"
        assert driver.category == "technological"
        assert driver.strength == "strong"


class TestScenario:
    """Tests for Scenario model."""

    def test_scenario_creation(self):
        impact = ImpactAssessment(
            risks=["Risk 1", "Risk 2"],
            opportunities=["Opportunity 1"],
            affected_sectors=["Healthcare", "Finance"],
        )

        path = [
            DevelopmentPath(
                step_number=1,
                description="Initial adoption",
                indicative_timeline="2025-2027",
                indicators_to_monitor=["Market share", "Investment levels"],
            )
        ]

        scenario = Scenario(
            name="Accelerated Adoption",
            description="Rapid mainstream adoption of the technology",
            probability_assessment="plausible",
            impact_assessment=impact,
            development_path=path,
            key_assumptions=["Regulatory support", "Cost reduction"],
        )

        assert scenario.name == "Accelerated Adoption"
        assert len(scenario.development_path) == 1
        assert len(scenario.impact_assessment.risks) == 2


class TestPhenomenon:
    """Tests for Phenomenon model."""

    def test_phenomenon_creation(self):
        phenomenon = Phenomenon(
            id="test-123",
            title="Test Phenomenon",
            tags=[ThematicTag.TECHNOLOGY, ThematicTag.ECONOMY],
            phenomenon_type=PhenomenonType.STRENGTHENING,
            summary="This is a test phenomenon.",
        )
        assert phenomenon.id == "test-123"
        assert phenomenon.title == "Test Phenomenon"
        assert len(phenomenon.tags) == 2
        assert phenomenon.phenomenon_type == PhenomenonType.STRENGTHENING

    def test_phenomenon_with_timing(self):
        timing = TimingAssessment(
            primary_horizon=TimeHorizon.NEAR_TERM,
            acceleration_phase="2025-2026",
            peak_phase="2027-2028",
            rationale="Strong current momentum",
            uncertainty_acknowledgement="Regulatory factors could delay",
        )

        phenomenon = Phenomenon(
            id="test-456",
            title="Near-term Trend",
            tags=[ThematicTag.TECHNOLOGY],
            phenomenon_type=PhenomenonType.STRENGTHENING,
            timing=timing,
        )

        assert phenomenon.timing.primary_horizon == TimeHorizon.NEAR_TERM
        assert "2025" in phenomenon.timing.acceleration_phase

    def test_phenomenon_radar_position(self):
        timing = TimingAssessment(
            primary_horizon=TimeHorizon.NEAR_TERM,
            rationale="Test",
        )

        phenomenon = Phenomenon(
            id="test-789",
            title="Test",
            tags=[ThematicTag.TECHNOLOGY],
            phenomenon_type=PhenomenonType.STRENGTHENING,
            timing=timing,
        )

        phenomenon.calculate_radar_position()
        assert phenomenon.radar_distance == 0.25  # Near-term distance

    def test_phenomenon_to_dict(self):
        phenomenon = Phenomenon(
            id="test-dict",
            title="Dict Test",
            tags=[ThematicTag.SOCIETY],
            phenomenon_type=PhenomenonType.WEAK_SIGNAL,
            summary="Testing serialization",
            confidence_level="moderate",
        )

        data = phenomenon.to_dict()
        assert data["id"] == "test-dict"
        assert data["phenomenon_type"] == "weak_signal"
        assert "society" in data["tags"]
        assert data["confidence_level"] == "moderate"

    def test_get_horizon_years(self):
        timing = TimingAssessment(
            primary_horizon=TimeHorizon.MID_TERM,
            rationale="Test",
        )

        phenomenon = Phenomenon(
            id="test-years",
            title="Years Test",
            tags=[ThematicTag.ECONOMY],
            phenomenon_type=PhenomenonType.STRENGTHENING,
            timing=timing,
        )

        start, end = phenomenon.get_horizon_years()
        current_year = datetime.now().year
        assert start == current_year + 5
        assert end == current_year + 10


class TestEnums:
    """Tests for enum types."""

    def test_phenomenon_types(self):
        assert PhenomenonType.STRENGTHENING.value == "strengthening"
        assert PhenomenonType.WEAKENING.value == "weakening"
        assert PhenomenonType.WEAK_SIGNAL.value == "weak_signal"
        assert PhenomenonType.WILD_CARD.value == "wild_card"

    def test_time_horizons(self):
        assert TimeHorizon.NEAR_TERM.value == "near_term"
        assert TimeHorizon.MID_TERM.value == "mid_term"
        assert TimeHorizon.LONG_TERM.value == "long_term"

    def test_thematic_tags(self):
        assert ThematicTag.TECHNOLOGY.value == "technology"
        assert ThematicTag.ENVIRONMENT.value == "environment"
        assert len(ThematicTag) == 10
