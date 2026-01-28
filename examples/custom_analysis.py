#!/usr/bin/env python3
"""
Example: Custom analysis with direct component access

This example shows how to use individual components of the
AI Foresight Scanner for more granular control.
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Phenomenon, PhenomenonType, ThematicTag, TimeHorizon, TimingAssessment
from src.scraper import SourceValidator
from src.visualizer import RadarChart, HTMLReportGenerator


def create_sample_phenomena():
    """Create sample phenomena for demonstration."""

    phenomena = [
        Phenomenon(
            id="phenom-001",
            title="Generative AI in Creative Industries",
            tags=[ThematicTag.TECHNOLOGY, ThematicTag.CULTURE, ThematicTag.ECONOMY],
            phenomenon_type=PhenomenonType.STRENGTHENING,
            timing=TimingAssessment(
                primary_horizon=TimeHorizon.NEAR_TERM,
                acceleration_phase="2024-2025",
                peak_phase="2026-2028",
                rationale="Rapid adoption across content creation, design, and media sectors.",
                uncertainty_acknowledgement="Regulatory responses and copyright challenges could slow adoption.",
            ),
            summary="Generative AI tools are rapidly transforming creative industries, enabling new forms of content creation while raising fundamental questions about authorship, originality, and the future of creative work.",
            confidence_level="high",
        ),
        Phenomenon(
            id="phenom-002",
            title="Deglobalization of Supply Chains",
            tags=[ThematicTag.ECONOMY, ThematicTag.GEOPOLITICS],
            phenomenon_type=PhenomenonType.STRENGTHENING,
            timing=TimingAssessment(
                primary_horizon=TimeHorizon.MID_TERM,
                acceleration_phase="2024-2027",
                peak_phase="2028-2032",
                rationale="Geopolitical tensions and pandemic lessons driving reshoring.",
                uncertainty_acknowledgement="Cost pressures may limit extent of restructuring.",
            ),
            summary="Companies and governments are restructuring global supply chains toward regional blocs and domestic production, reversing decades of globalization in response to geopolitical risks and resilience concerns.",
            confidence_level="moderate",
        ),
        Phenomenon(
            id="phenom-003",
            title="Neuromorphic Computing Emergence",
            tags=[ThematicTag.TECHNOLOGY],
            phenomenon_type=PhenomenonType.WEAK_SIGNAL,
            timing=TimingAssessment(
                primary_horizon=TimeHorizon.LONG_TERM,
                rationale="Still in research phase but advancing rapidly.",
                uncertainty_acknowledgement="Commercialization timeline highly uncertain.",
            ),
            summary="Brain-inspired computing architectures that process information more like biological neural networks, potentially enabling dramatic improvements in energy efficiency and learning capabilities.",
            confidence_level="low",
        ),
        Phenomenon(
            id="phenom-004",
            title="Synthetic Biology for Carbon Capture",
            tags=[ThematicTag.TECHNOLOGY, ThematicTag.ENVIRONMENT],
            phenomenon_type=PhenomenonType.WEAK_SIGNAL,
            timing=TimingAssessment(
                primary_horizon=TimeHorizon.MID_TERM,
                rationale="Promising research but scale-up challenges remain.",
            ),
            summary="Engineered microorganisms and plants designed to capture and sequester atmospheric carbon dioxide at enhanced rates, offering potential biological solutions to climate change.",
            confidence_level="low",
        ),
        Phenomenon(
            id="phenom-005",
            title="Decline of Traditional Retail Banking",
            tags=[ThematicTag.ECONOMY, ThematicTag.TECHNOLOGY],
            phenomenon_type=PhenomenonType.WEAKENING,
            timing=TimingAssessment(
                primary_horizon=TimeHorizon.NEAR_TERM,
                decline_phase="2024-2030",
                rationale="Digital-first alternatives and fintech disruption accelerating.",
            ),
            summary="Traditional branch-based retail banking is declining as customers shift to digital channels, neobanks, and embedded financial services, forcing legacy institutions to transform or contract.",
            confidence_level="high",
        ),
    ]

    # Calculate radar positions for all phenomena
    for p in phenomena:
        p.calculate_radar_position()

    return phenomena


def main():
    """Demonstrate custom analysis workflow."""

    print("\n" + "=" * 60)
    print("  Custom Foresight Analysis Example")
    print("=" * 60)

    # Create sample phenomena
    phenomena = create_sample_phenomena()
    print(f"\nCreated {len(phenomena)} sample phenomena")

    # Demonstrate source validation
    print("\n" + "-" * 40)
    print("Source Validation Demo:")
    print("-" * 40)

    validator = SourceValidator()
    test_urls = [
        "https://www.nature.com/articles/example",
        "https://www.weforum.org/reports/future-tech",
        "https://random-blog.example.com/post",
    ]

    for url in test_urls:
        result = validator.validate(url)
        status = "✓" if result.is_acceptable else "✗"
        print(f"  {status} {url}")
        print(f"    Type: {result.source_type.value}, Score: {result.credibility_score}")

    # Generate radar visualization
    print("\n" + "-" * 40)
    print("Generating Radar Visualization:")
    print("-" * 40)

    radar = RadarChart(width=800, height=800)
    os.makedirs("./example_output", exist_ok=True)
    radar.save_html(phenomena, "./example_output/custom_radar.html", title="Custom Foresight Radar")
    print("  Saved: ./example_output/custom_radar.html")

    # Generate reports
    print("\n" + "-" * 40)
    print("Generating Reports:")
    print("-" * 40)

    generator = HTMLReportGenerator()

    # Generate Markdown cards
    for p in phenomena[:2]:  # Just first 2 for demo
        md = generator.generate_markdown_card(p)
        filename = f"./example_output/{p.id}.md"
        with open(filename, "w") as f:
            f.write(md)
        print(f"  Saved: {filename}")

    # Generate HTML report
    html = generator.generate_html_report(phenomena, title="Custom Analysis Report")
    with open("./example_output/custom_report.html", "w") as f:
        f.write(html)
    print("  Saved: ./example_output/custom_report.html")

    # Print summary
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    print(f"\nPhenomena by type:")
    for ptype in PhenomenonType:
        count = sum(1 for p in phenomena if p.phenomenon_type == ptype)
        if count > 0:
            print(f"  - {ptype.value}: {count}")

    print(f"\nPhenomena by time horizon:")
    for horizon in TimeHorizon:
        count = sum(1 for p in phenomena if p.timing and p.timing.primary_horizon == horizon)
        if count > 0:
            print(f"  - {horizon.value}: {count}")

    print("\nOutput files generated in ./example_output/")


if __name__ == "__main__":
    main()
