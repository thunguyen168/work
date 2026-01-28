"""
Command-line interface for the AI Foresight Scanner.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

from .analyzer import ForesightAnalyzer
from .models import Phenomenon
from .scraper import SearchEngine, SourceValidator, WebScraper
from .utils import Config, load_config, setup_logging
from .visualizer import HTMLReportGenerator, RadarChart


class ForesightScanner:
    """
    Main orchestrator for the AI Foresight Scanner.

    Coordinates web scraping, AI analysis, and output generation.
    """

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the scanner.

        Args:
            config: Optional configuration object
        """
        self.config = config or Config()
        self.logger = setup_logging(log_dir=self.config.output.output_dir)

        # Initialize components
        self.source_validator = SourceValidator(
            strict_mode=self.config.analyzer.strict_source_validation
        )
        self.web_scraper = WebScraper()
        self.analyzer = ForesightAnalyzer(
            model=self.config.analyzer.model,
            source_validator=self.source_validator,
        )
        self.radar_chart = RadarChart(
            width=self.config.output.radar_width,
            height=self.config.output.radar_height,
        )
        self.report_generator = HTMLReportGenerator()

    async def scan_topic(self, topic: str) -> list[Phenomenon]:
        """
        Perform a foresight scan on a topic.

        Args:
            topic: The topic to scan

        Returns:
            List of identified phenomena
        """
        self.logger.info(f"Starting foresight scan for: {topic}")
        phenomena = []

        try:
            # Initialize search engine
            search_engine = SearchEngine(
                preferred_domains=self.config.search.preferred_domains
                or SearchEngine.CREDIBLE_DOMAINS
            )

            # Perform comprehensive search using Johari Window heuristic
            if self.config.search.use_johari_heuristic:
                self.logger.info("Executing comprehensive search with Johari Window heuristic...")
                search_results = await search_engine.comprehensive_search(
                    topic,
                    results_per_quadrant=self.config.search.results_per_query,
                )

                # Flatten results
                all_results = []
                for quadrant, responses in search_results.items():
                    for response in responses:
                        all_results.extend(response.results)

                self.logger.info(f"Found {len(all_results)} total search results")
            else:
                # Simple targeted search
                self.logger.info("Executing targeted search...")
                response = await search_engine.search_credible_sources(
                    topic,
                    num_results=self.config.search.results_per_query * 4,
                )
                all_results = response.results

            # Deduplicate and filter by credibility
            all_results = search_engine.deduplicate_results(all_results)
            credible_results = search_engine.filter_by_credibility(
                all_results, min_score=0.5
            )
            self.logger.info(f"Filtered to {len(credible_results)} credible results")

            # Scrape top results
            urls_to_scrape = [r.url for r in credible_results[:15]]
            self.logger.info(f"Scraping {len(urls_to_scrape)} URLs...")
            scraped_contents = self.web_scraper.fetch_sync(urls_to_scrape)
            successful_scrapes = [s for s in scraped_contents if s.success]
            self.logger.info(f"Successfully scraped {len(successful_scrapes)} pages")

            # Analyze and structure as phenomenon
            self.logger.info("Analyzing content with AI...")
            phenomenon = await self.analyzer.analyze_phenomenon(
                query=topic,
                scraped_contents=successful_scrapes,
                search_results=credible_results[:20],
            )
            phenomena.append(phenomenon)

            # Quality check
            self.logger.info("Running quality check...")
            quality = self.analyzer.quality_check(phenomenon)
            self.logger.info(
                f"Quality score: {quality.get('quality_score', 'N/A')}/10"
            )

            if quality.get("issues"):
                for issue in quality["issues"][:3]:
                    self.logger.warning(f"Quality issue: {issue}")

        except Exception as e:
            self.logger.error(f"Error during scan: {e}")
            raise

        return phenomena

    async def scan_multiple_topics(self, topics: list[str]) -> list[Phenomenon]:
        """
        Scan multiple topics.

        Args:
            topics: List of topics to scan

        Returns:
            List of all identified phenomena
        """
        all_phenomena = []
        for topic in topics:
            phenomena = await self.scan_topic(topic)
            all_phenomena.extend(phenomena)
        return all_phenomena

    def generate_outputs(
        self,
        phenomena: list[Phenomenon],
        title: str = "Foresight Scan",
    ) -> dict[str, str]:
        """
        Generate all output formats.

        Args:
            phenomena: List of phenomena to output
            title: Title for reports

        Returns:
            Dictionary of output file paths
        """
        self.logger.info("Generating outputs...")
        outputs = {}

        output_dir = Path(self.config.output.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate reports in configured formats
        format_str = "all" if len(self.config.output.formats) >= 3 else ",".join(
            self.config.output.formats
        )
        report_outputs = self.report_generator.save_report(
            phenomena,
            str(output_dir),
            format=format_str,
        )
        outputs.update(report_outputs)

        # Generate radar chart
        if self.config.output.generate_radar:
            radar_path = output_dir / "radar.html"
            self.radar_chart.save_html(
                phenomena,
                str(radar_path),
                title=f"{title} - Radar View",
            )
            outputs["radar"] = str(radar_path)
            self.logger.info(f"Radar chart saved to: {radar_path}")

        self.logger.info("Output generation complete!")
        for output_type, path in outputs.items():
            self.logger.info(f"  {output_type}: {path}")

        return outputs


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="AI Foresight Scanner - Identify and structure emerging trends and signals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a single topic
  foresight-scan "artificial intelligence in healthcare"

  # Scan multiple topics
  foresight-scan "quantum computing" "synthetic biology" "space economy"

  # Use custom config
  foresight-scan --config my_config.yaml "climate adaptation technologies"

  # Output to specific directory
  foresight-scan --output ./my_scans "future of work"
        """,
    )

    parser.add_argument(
        "topics",
        nargs="+",
        help="Topics to scan for foresight phenomena",
    )

    parser.add_argument(
        "-c", "--config",
        type=str,
        help="Path to YAML configuration file",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Output directory (default: ./output)",
    )

    parser.add_argument(
        "--title",
        type=str,
        default="Foresight Scan",
        help="Title for generated reports",
    )

    parser.add_argument(
        "--no-radar",
        action="store_true",
        help="Skip radar chart generation",
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["html", "json", "markdown", "all"],
        default="all",
        help="Output format (default: all)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="claude-sonnet-4-20250514",
        help="Claude model to use for analysis",
    )

    parser.add_argument(
        "--strict-sources",
        action="store_true",
        help="Use strict source validation (only top-tier sources)",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args()

    # Load or create config
    if args.config:
        config = load_config(args.config)
    else:
        config = Config()

    # Apply CLI overrides
    config.output.output_dir = args.output
    config.output.generate_radar = not args.no_radar
    config.analyzer.model = args.model
    config.analyzer.strict_source_validation = args.strict_sources

    if args.format != "all":
        config.output.formats = [args.format]

    # Run the scanner
    try:
        scanner = ForesightScanner(config=config)

        print("\n" + "=" * 60)
        print("  AI FORESIGHT SCANNER")
        print("=" * 60)
        print(f"\nTopics to scan: {', '.join(args.topics)}")
        print(f"Output directory: {args.output}")
        print(f"Model: {config.analyzer.model}")
        print("\n" + "-" * 60 + "\n")

        # Run async scan
        phenomena = asyncio.run(scanner.scan_multiple_topics(args.topics))

        if phenomena:
            # Generate outputs
            outputs = scanner.generate_outputs(phenomena, title=args.title)

            print("\n" + "=" * 60)
            print("  SCAN COMPLETE")
            print("=" * 60)
            print(f"\nIdentified {len(phenomena)} phenomena")
            print("\nOutputs generated:")
            for output_type, path in outputs.items():
                print(f"  - {output_type}: {path}")
            print()
        else:
            print("\nNo phenomena identified. Try different search terms.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
