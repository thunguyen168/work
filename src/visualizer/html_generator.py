"""
HTML and Markdown report generator for foresight phenomena.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models import Phenomenon


class HTMLReportGenerator:
    """
    Generates formatted reports and cards for foresight phenomena.
    """

    def generate_markdown_card(self, phenomenon: Phenomenon) -> str:
        """
        Generate a Markdown-formatted foresight card.

        Args:
            phenomenon: The phenomenon to format

        Returns:
            Markdown string
        """
        # Header
        md = f"# {phenomenon.title}\n\n"

        # Tags
        tags = " | ".join([f"`{t.value}`" for t in phenomenon.tags])
        md += f"**Tags:** {tags}\n\n"

        # Type and Timing
        md += "## Classification\n\n"
        type_emoji = {
            "strengthening": "📈",
            "weakening": "📉",
            "weak_signal": "🔍",
            "wild_card": "⚡",
        }
        emoji = type_emoji.get(phenomenon.phenomenon_type.value, "")
        md += f"**Type:** {emoji} {phenomenon.phenomenon_type.value.replace('_', ' ').title()}\n\n"

        if phenomenon.timing:
            horizon = phenomenon.timing.primary_horizon.value.replace("_", "-")
            md += f"**Time Horizon:** {horizon.title()}\n\n"
            if phenomenon.timing.rationale:
                md += f"*{phenomenon.timing.rationale}*\n\n"
            if phenomenon.timing.uncertainty_acknowledgement:
                md += f"> ⚠️ **Uncertainty:** {phenomenon.timing.uncertainty_acknowledgement}\n\n"

        # Summary
        md += "## Summary\n\n"
        md += f"{phenomenon.summary}\n\n"

        # Sources
        if phenomenon.sources:
            md += "### Sources\n\n"
            for source in phenomenon.sources[:5]:  # Limit to top 5
                md += f"- [{source.title}]({source.url})"
                if source.organization:
                    md += f" ({source.organization})"
                md += "\n"
            md += "\n"

        # Drivers
        if phenomenon.drivers:
            md += "## Key Drivers\n\n"
            for driver in phenomenon.drivers:
                strength_indicator = {"strong": "●●●", "moderate": "●●○", "emerging": "●○○"}
                indicator = strength_indicator.get(driver.strength, "●○○")
                md += f"### {driver.name}\n\n"
                md += f"**Category:** {driver.category.title()} | **Strength:** {indicator} {driver.strength}\n\n"
                md += f"{driver.description}\n\n"

        # Scenarios
        if phenomenon.scenarios:
            md += "## Future Scenarios\n\n"
            for i, scenario in enumerate(phenomenon.scenarios, 1):
                md += f"### Scenario {i}: {scenario.name}\n\n"
                md += f"*Probability: {scenario.probability_assessment}*\n\n"
                md += f"{scenario.description}\n\n"

                if scenario.key_assumptions:
                    md += "**Key Assumptions:**\n"
                    for assumption in scenario.key_assumptions:
                        md += f"- {assumption}\n"
                    md += "\n"

                # Impact Assessment
                md += "#### Impact Assessment\n\n"
                if scenario.impact_assessment.risks:
                    md += "**Risks:**\n"
                    for risk in scenario.impact_assessment.risks:
                        md += f"- ⚠️ {risk}\n"
                    md += "\n"

                if scenario.impact_assessment.opportunities:
                    md += "**Opportunities:**\n"
                    for opp in scenario.impact_assessment.opportunities:
                        md += f"- ✅ {opp}\n"
                    md += "\n"

                if scenario.impact_assessment.affected_sectors:
                    sectors = ", ".join(scenario.impact_assessment.affected_sectors)
                    md += f"**Affected Sectors:** {sectors}\n\n"

                # Development Path
                if scenario.development_path:
                    md += "#### Development Path\n\n"
                    for step in scenario.development_path:
                        md += f"**Step {step.step_number}** ({step.indicative_timeline})\n"
                        md += f"{step.description}\n"
                        if step.indicators_to_monitor:
                            md += "- *Monitor:* " + ", ".join(step.indicators_to_monitor) + "\n"
                        md += "\n"

        # Connections
        md += "## Connections & Implications\n\n"

        if phenomenon.related_phenomena:
            md += "### Related Phenomena\n\n"
            for related in phenomenon.related_phenomena:
                md += f"- {related}\n"
            md += "\n"

        if phenomenon.second_order_effects:
            md += "### Second-Order Effects\n\n"
            for effect in phenomenon.second_order_effects:
                md += f"- {effect}\n"
            md += "\n"

        if phenomenon.areas_for_exploration:
            md += "### Areas for Exploration\n\n"
            for area in phenomenon.areas_for_exploration:
                md += f"- {area}\n"
            md += "\n"

        # Additional Readings
        if phenomenon.additional_readings:
            md += "### Additional Readings\n\n"
            for reading in phenomenon.additional_readings:
                md += f"- [{reading.title}]({reading.url})\n"
            md += "\n"

        # Metadata footer
        md += "---\n\n"
        md += f"*Generated: {phenomenon.created_at.strftime('%Y-%m-%d %H:%M')} | "
        md += f"Confidence: {phenomenon.confidence_level} | "
        md += f"Data Quality: {phenomenon.data_quality}*\n"

        return md

    def generate_summary_table(self, phenomena: list[Phenomenon]) -> str:
        """
        Generate a Markdown summary table of multiple phenomena.

        Args:
            phenomena: List of phenomena

        Returns:
            Markdown table string
        """
        md = "# Foresight Scan Summary\n\n"
        md += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        md += f"Total Phenomena: {len(phenomena)}*\n\n"

        md += "| Title | Type | Time Horizon | Tags | Confidence |\n"
        md += "|-------|------|--------------|------|------------|\n"

        for p in phenomena:
            title = p.title[:40] + "..." if len(p.title) > 40 else p.title
            ptype = p.phenomenon_type.value.replace("_", " ").title()
            horizon = p.timing.primary_horizon.value.replace("_", "-") if p.timing else "N/A"
            tags = ", ".join([t.value for t in p.tags[:2]])
            md += f"| {title} | {ptype} | {horizon} | {tags} | {p.confidence_level} |\n"

        return md

    def generate_html_report(
        self,
        phenomena: list[Phenomenon],
        title: str = "Foresight Scan Report",
    ) -> str:
        """
        Generate a full HTML report with all phenomena.

        Args:
            phenomena: List of phenomena
            title: Report title

        Returns:
            HTML string
        """
        cards_html = ""
        for p in phenomena:
            cards_html += self._generate_html_card(p)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
            color: white;
            border-radius: 1rem;
        }}
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        header p {{
            opacity: 0.8;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1.5rem;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.7;
        }}
        .cards {{
            display: grid;
            gap: 2rem;
        }}
        .card {{
            background: white;
            border-radius: 1rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .card-header {{
            padding: 1.5rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .card-header h2 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        .card-meta {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .badge-strengthening {{ background: #dcfce7; color: #166534; }}
        .badge-weakening {{ background: #fee2e2; color: #991b1b; }}
        .badge-weak_signal {{ background: #fef3c7; color: #92400e; }}
        .badge-wild_card {{ background: #ede9fe; color: #5b21b6; }}
        .tag {{
            background: #f1f5f9;
            color: #475569;
            padding: 0.2rem 0.6rem;
            border-radius: 0.25rem;
            font-size: 0.75rem;
        }}
        .card-body {{
            padding: 1.5rem;
        }}
        .section {{
            margin-bottom: 1.5rem;
        }}
        .section h3 {{
            font-size: 1rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }}
        .section p {{
            color: #334155;
        }}
        .driver {{
            background: #f8fafc;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.75rem;
        }}
        .driver h4 {{
            color: #1e293b;
            margin-bottom: 0.25rem;
        }}
        .driver-meta {{
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 0.5rem;
        }}
        .scenario {{
            border-left: 3px solid #3b82f6;
            padding-left: 1rem;
            margin-bottom: 1.5rem;
        }}
        .scenario h4 {{
            color: #1e293b;
            margin-bottom: 0.5rem;
        }}
        .scenario-prob {{
            font-size: 0.85rem;
            color: #64748b;
            font-style: italic;
        }}
        .impact-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        .impact-box {{
            background: #f8fafc;
            padding: 1rem;
            border-radius: 0.5rem;
        }}
        .impact-box h5 {{
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 0.5rem;
        }}
        .impact-box ul {{
            font-size: 0.9rem;
            padding-left: 1.2rem;
        }}
        .source-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .source-link {{
            background: #eff6ff;
            color: #1d4ed8;
            padding: 0.3rem 0.75rem;
            border-radius: 0.25rem;
            font-size: 0.85rem;
            text-decoration: none;
        }}
        .source-link:hover {{
            background: #dbeafe;
        }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.9rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p>AI-powered foresight analysis of emerging trends and signals</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(phenomena)}</div>
                    <div class="stat-label">Phenomena</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{sum(1 for p in phenomena if p.phenomenon_type.value == 'strengthening')}</div>
                    <div class="stat-label">Strengthening</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{sum(1 for p in phenomena if p.phenomenon_type.value == 'weak_signal')}</div>
                    <div class="stat-label">Weak Signals</div>
                </div>
            </div>
        </header>

        <div class="cards">
            {cards_html}
        </div>

        <footer>
            <p>Generated by AI Foresight Scanner on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </footer>
    </div>
</body>
</html>"""

        return html

    def _generate_html_card(self, p: Phenomenon) -> str:
        """Generate HTML for a single phenomenon card."""
        tags_html = "".join([f'<span class="tag">{t.value}</span>' for t in p.tags])

        sources_html = ""
        for s in p.sources[:4]:
            sources_html += f'<a href="{s.url}" class="source-link" target="_blank">{s.title[:30]}...</a>'

        drivers_html = ""
        for d in p.drivers[:3]:
            drivers_html += f"""
            <div class="driver">
                <h4>{d.name}</h4>
                <div class="driver-meta">{d.category.title()} | Strength: {d.strength}</div>
                <p>{d.description}</p>
            </div>
            """

        scenarios_html = ""
        for s in p.scenarios[:2]:
            risks_html = "".join([f"<li>{r}</li>" for r in s.impact_assessment.risks[:3]])
            opps_html = "".join([f"<li>{o}</li>" for o in s.impact_assessment.opportunities[:3]])

            scenarios_html += f"""
            <div class="scenario">
                <h4>{s.name}</h4>
                <p class="scenario-prob">Probability: {s.probability_assessment}</p>
                <p>{s.description}</p>
                <div class="impact-grid">
                    <div class="impact-box">
                        <h5>Risks</h5>
                        <ul>{risks_html}</ul>
                    </div>
                    <div class="impact-box">
                        <h5>Opportunities</h5>
                        <ul>{opps_html}</ul>
                    </div>
                </div>
            </div>
            """

        horizon = p.timing.primary_horizon.value.replace("_", "-") if p.timing else "uncertain"

        return f"""
        <div class="card">
            <div class="card-header">
                <h2>{p.title}</h2>
                <div class="card-meta">
                    <span class="badge badge-{p.phenomenon_type.value}">{p.phenomenon_type.value.replace('_', ' ').title()}</span>
                    <span class="badge" style="background: #e0e7ff; color: #3730a3;">{horizon}</span>
                    {tags_html}
                </div>
            </div>
            <div class="card-body">
                <div class="section">
                    <h3>Summary</h3>
                    <p>{p.summary}</p>
                </div>

                <div class="section">
                    <h3>Key Drivers</h3>
                    {drivers_html}
                </div>

                <div class="section">
                    <h3>Future Scenarios</h3>
                    {scenarios_html}
                </div>

                <div class="section">
                    <h3>Sources</h3>
                    <div class="source-list">
                        {sources_html}
                    </div>
                </div>
            </div>
        </div>
        """

    def save_report(
        self,
        phenomena: list[Phenomenon],
        output_dir: str,
        format: str = "all",
    ) -> dict[str, str]:
        """
        Save reports in specified formats.

        Args:
            phenomena: List of phenomena
            output_dir: Directory to save reports
            format: "markdown", "html", "json", or "all"

        Returns:
            Dictionary of output file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        outputs = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format in ("markdown", "all"):
            # Individual cards
            cards_dir = output_path / "cards"
            cards_dir.mkdir(exist_ok=True)
            for p in phenomena:
                card_path = cards_dir / f"{p.id[:8]}_{self._slugify(p.title)}.md"
                with open(card_path, "w", encoding="utf-8") as f:
                    f.write(self.generate_markdown_card(p))

            # Summary
            summary_path = output_path / f"summary_{timestamp}.md"
            with open(summary_path, "w", encoding="utf-8") as f:
                f.write(self.generate_summary_table(phenomena))
            outputs["markdown_summary"] = str(summary_path)
            outputs["markdown_cards"] = str(cards_dir)

        if format in ("html", "all"):
            html_path = output_path / f"report_{timestamp}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.generate_html_report(phenomena))
            outputs["html_report"] = str(html_path)

        if format in ("json", "all"):
            json_path = output_path / f"phenomena_{timestamp}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(
                    [p.to_dict() for p in phenomena],
                    f,
                    indent=2,
                    default=str,
                )
            outputs["json_data"] = str(json_path)

        return outputs

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug."""
        import re
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text[:50]
