"""
Tests for source validation functionality.
"""

import pytest

from src.scraper.source_validator import SourceValidator, SourceType


class TestSourceValidator:
    """Tests for SourceValidator."""

    @pytest.fixture
    def validator(self):
        return SourceValidator()

    @pytest.fixture
    def strict_validator(self):
        return SourceValidator(strict_mode=True)

    def test_peer_reviewed_detection(self, validator):
        result = validator.validate("https://www.nature.com/articles/s41586-024-1234")
        assert result.source_type == SourceType.PEER_REVIEWED
        assert result.credibility_score >= 0.9
        assert result.is_acceptable

    def test_intergovernmental_detection(self, validator):
        result = validator.validate("https://www.un.org/reports/climate-2024")
        assert result.source_type == SourceType.INTERGOVERNMENTAL
        assert result.credibility_score >= 0.85
        assert result.is_acceptable

    def test_think_tank_detection(self, validator):
        result = validator.validate("https://www.brookings.edu/research/ai-policy")
        assert result.source_type == SourceType.THINK_TANK
        assert result.credibility_score >= 0.75
        assert result.is_acceptable

    def test_industry_research_detection(self, validator):
        result = validator.validate("https://www.mckinsey.com/insights/technology")
        assert result.source_type == SourceType.INDUSTRY_RESEARCH
        assert result.is_acceptable

    def test_established_media_detection(self, validator):
        result = validator.validate("https://www.reuters.com/world/tech-trends")
        assert result.source_type == SourceType.ESTABLISHED_MEDIA
        assert result.is_acceptable

    def test_government_detection(self, validator):
        result = validator.validate("https://www.state.gov/policy-reports")
        assert result.source_type == SourceType.GOVERNMENT
        assert result.is_acceptable

    def test_general_web_detection(self, validator):
        result = validator.validate("https://random-blog.com/my-thoughts")
        assert result.source_type == SourceType.GENERAL_WEB
        assert result.credibility_score < 0.5

    def test_strict_mode_rejects_general_web(self, strict_validator):
        result = strict_validator.validate("https://random-blog.com/article")
        assert not result.is_acceptable

    def test_strict_mode_accepts_peer_reviewed(self, strict_validator):
        result = strict_validator.validate("https://www.nature.com/article")
        assert result.is_acceptable

    def test_batch_validation(self, validator):
        urls = [
            "https://www.nature.com/article1",
            "https://www.un.org/report1",
            "https://random-site.com/page",
        ]
        results = validator.validate_batch(urls)
        assert len(results) == 3
        assert results[0].source_type == SourceType.PEER_REVIEWED
        assert results[1].source_type == SourceType.INTERGOVERNMENTAL

    def test_filter_acceptable(self, validator):
        urls = [
            "https://www.nature.com/article",
            "https://random-blog.com/post",
            "https://www.brookings.edu/research",
        ]
        acceptable = validator.filter_acceptable(urls)
        assert len(acceptable) == 2
        # Should be sorted by credibility
        assert acceptable[0][1].source_type == SourceType.PEER_REVIEWED

    def test_organization_extraction(self, validator):
        result = validator.validate("https://www.worldbank.org/report")
        assert result.organization == "World Bank"

        result = validator.validate("https://www.economist.com/article")
        assert result.organization == "The Economist"

    def test_warning_detection(self, validator):
        result = validator.validate("https://blog.wordpress.com/my-predictions")
        assert len(result.warnings) > 0
        assert any("user-generated" in w.lower() for w in result.warnings)

    def test_credibility_boost_for_research_urls(self, validator):
        base_result = validator.validate("https://www.example-org.org/page")
        research_result = validator.validate("https://www.example-org.org/research/study")

        # Research URL should get slight boost
        assert research_result.credibility_score >= base_result.credibility_score

    def test_academic_domain_detection(self, validator):
        result = validator.validate("https://www.stanford.edu/research")
        assert result.source_type == SourceType.PEER_REVIEWED

        result = validator.validate("https://www.ox.ac.uk/publications")
        assert result.source_type == SourceType.PEER_REVIEWED
