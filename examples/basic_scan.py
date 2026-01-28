#!/usr/bin/env python3
"""
Example: Basic foresight scan

This example demonstrates how to use the AI Foresight Scanner
programmatically to analyze a topic and generate outputs.

Prerequisites:
- Set ANTHROPIC_API_KEY environment variable
- Set SERPER_API_KEY or BRAVE_API_KEY environment variable
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cli import ForesightScanner
from src.utils import Config


async def main():
    """Run a basic foresight scan."""

    # Check for required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    if not (os.getenv("SERPER_API_KEY") or os.getenv("BRAVE_API_KEY")):
        print("Error: SERPER_API_KEY or BRAVE_API_KEY environment variable not set")
        sys.exit(1)

    # Create configuration
    config = Config()
    config.output.output_dir = "./example_output"
    config.output.generate_radar = True

    # Initialize scanner
    scanner = ForesightScanner(config=config)

    # Define topic to scan
    topic = "quantum computing applications in cryptography"

    print(f"\n{'='*60}")
    print(f"  Scanning topic: {topic}")
    print(f"{'='*60}\n")

    # Run the scan
    phenomena = await scanner.scan_topic(topic)

    if phenomena:
        print(f"\nIdentified {len(phenomena)} phenomenon/phenomena")

        # Print summary of each phenomenon
        for p in phenomena:
            print(f"\n{'─'*40}")
            print(f"Title: {p.title}")
            print(f"Type: {p.phenomenon_type.value}")
            if p.timing:
                print(f"Time Horizon: {p.timing.primary_horizon.value}")
            print(f"Tags: {', '.join(t.value for t in p.tags)}")
            print(f"Confidence: {p.confidence_level}")
            print(f"\nSummary: {p.summary[:200]}...")

            if p.drivers:
                print(f"\nKey Drivers:")
                for d in p.drivers[:3]:
                    print(f"  - {d.name} ({d.category})")

            if p.scenarios:
                print(f"\nScenarios:")
                for s in p.scenarios:
                    print(f"  - {s.name}: {s.description[:100]}...")

        # Generate outputs
        print(f"\n{'='*60}")
        print("  Generating outputs...")
        print(f"{'='*60}")

        outputs = scanner.generate_outputs(phenomena, title="Quantum Computing Foresight")

        print("\nGenerated files:")
        for output_type, path in outputs.items():
            print(f"  - {output_type}: {path}")

    else:
        print("No phenomena identified. Try a different topic.")


if __name__ == "__main__":
    asyncio.run(main())
