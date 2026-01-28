"""
Radar/web chart visualization for foresight phenomena.

Creates an interactive radar chart where:
- Distance from center = time horizon (closer = nearer term)
- Angle = thematic area
- Color = phenomenon type
- Size = confidence level
"""

import json
import math
from dataclasses import dataclass
from typing import Optional

from ..models import Phenomenon, PhenomenonType, ThematicTag, TimeHorizon


@dataclass
class RadarPoint:
    """A point on the radar chart."""
    id: str
    title: str
    x: float
    y: float
    distance: float  # 0-1, where 0 is center
    angle: float     # 0-360 degrees
    color: str
    size: float
    phenomenon_type: str
    time_horizon: str
    tags: list[str]
    summary: str


class RadarChart:
    """
    Generates interactive radar/web chart visualizations
    for foresight phenomena.
    """

    # Colors for phenomenon types
    TYPE_COLORS = {
        PhenomenonType.STRENGTHENING: "#22c55e",   # Green
        PhenomenonType.WEAKENING: "#ef4444",       # Red
        PhenomenonType.WEAK_SIGNAL: "#f59e0b",     # Amber
        PhenomenonType.WILD_CARD: "#8b5cf6",       # Purple
    }

    # Angle assignments for thematic tags (degrees)
    TAG_ANGLES = {
        ThematicTag.TECHNOLOGY: 0,
        ThematicTag.ECONOMY: 36,
        ThematicTag.SOCIETY: 72,
        ThematicTag.DEMOGRAPHICS: 108,
        ThematicTag.CULTURE: 144,
        ThematicTag.ENVIRONMENT: 180,
        ThematicTag.HEALTH: 216,
        ThematicTag.GOVERNANCE: 252,
        ThematicTag.GEOPOLITICS: 288,
        ThematicTag.SECURITY: 324,
    }

    # Time horizon ring distances (0 = center, 1 = edge)
    HORIZON_DISTANCES = {
        TimeHorizon.NEAR_TERM: 0.25,
        TimeHorizon.MID_TERM: 0.55,
        TimeHorizon.LONG_TERM: 0.85,
        TimeHorizon.UNCERTAIN: 0.70,
    }

    def __init__(
        self,
        width: int = 800,
        height: int = 800,
        margin: int = 60,
    ):
        self.width = width
        self.height = height
        self.margin = margin
        self.center_x = width / 2
        self.center_y = height / 2
        self.max_radius = min(width, height) / 2 - margin

    def calculate_position(self, phenomenon: Phenomenon) -> RadarPoint:
        """
        Calculate radar chart position for a phenomenon.

        Args:
            phenomenon: The phenomenon to position

        Returns:
            RadarPoint with calculated coordinates
        """
        # Calculate distance from center based on time horizon
        if phenomenon.timing:
            distance = self.HORIZON_DISTANCES.get(
                phenomenon.timing.primary_horizon, 0.5
            )
        else:
            distance = phenomenon.radar_distance

        # Calculate angle based on primary tag
        if phenomenon.tags:
            primary_tag = phenomenon.tags[0]
            base_angle = self.TAG_ANGLES.get(primary_tag, 0)
            # Add small jitter to prevent overlap
            angle = base_angle + (hash(phenomenon.id) % 30) - 15
        else:
            angle = phenomenon.radar_angle

        # Convert polar to cartesian coordinates
        angle_rad = math.radians(angle)
        radius = distance * self.max_radius
        x = self.center_x + radius * math.cos(angle_rad)
        y = self.center_y + radius * math.sin(angle_rad)

        # Determine color based on type
        color = self.TYPE_COLORS.get(
            phenomenon.phenomenon_type, "#6b7280"
        )

        # Size based on confidence level
        size_map = {"high": 16, "moderate": 12, "low": 8}
        size = size_map.get(phenomenon.confidence_level, 12)

        return RadarPoint(
            id=phenomenon.id,
            title=phenomenon.title,
            x=x,
            y=y,
            distance=distance,
            angle=angle,
            color=color,
            size=size,
            phenomenon_type=phenomenon.phenomenon_type.value,
            time_horizon=(
                phenomenon.timing.primary_horizon.value
                if phenomenon.timing else "uncertain"
            ),
            tags=[t.value for t in phenomenon.tags],
            summary=phenomenon.summary[:200] + "..." if len(phenomenon.summary) > 200 else phenomenon.summary,
        )

    def generate_chart_data(
        self, phenomena: list[Phenomenon]
    ) -> dict:
        """
        Generate data structure for the radar chart.

        Args:
            phenomena: List of phenomena to visualize

        Returns:
            Dictionary with chart configuration and data
        """
        points = [self.calculate_position(p) for p in phenomena]

        return {
            "config": {
                "width": self.width,
                "height": self.height,
                "centerX": self.center_x,
                "centerY": self.center_y,
                "maxRadius": self.max_radius,
            },
            "rings": [
                {
                    "name": "Near-term (0-5 years)",
                    "distance": self.HORIZON_DISTANCES[TimeHorizon.NEAR_TERM],
                    "radius": self.HORIZON_DISTANCES[TimeHorizon.NEAR_TERM] * self.max_radius,
                },
                {
                    "name": "Mid-term (5-10 years)",
                    "distance": self.HORIZON_DISTANCES[TimeHorizon.MID_TERM],
                    "radius": self.HORIZON_DISTANCES[TimeHorizon.MID_TERM] * self.max_radius,
                },
                {
                    "name": "Long-term (10-20 years)",
                    "distance": self.HORIZON_DISTANCES[TimeHorizon.LONG_TERM],
                    "radius": self.HORIZON_DISTANCES[TimeHorizon.LONG_TERM] * self.max_radius,
                },
            ],
            "sectors": [
                {"name": tag.value.title(), "angle": angle}
                for tag, angle in self.TAG_ANGLES.items()
            ],
            "legend": [
                {"type": ptype.value, "color": color, "label": ptype.value.replace("_", " ").title()}
                for ptype, color in self.TYPE_COLORS.items()
            ],
            "points": [
                {
                    "id": p.id,
                    "title": p.title,
                    "x": p.x,
                    "y": p.y,
                    "distance": p.distance,
                    "angle": p.angle,
                    "color": p.color,
                    "size": p.size,
                    "phenomenonType": p.phenomenon_type,
                    "timeHorizon": p.time_horizon,
                    "tags": p.tags,
                    "summary": p.summary,
                }
                for p in points
            ],
        }

    def generate_html(
        self,
        phenomena: list[Phenomenon],
        title: str = "Foresight Radar",
        include_details: bool = True,
    ) -> str:
        """
        Generate a complete HTML page with the radar chart.

        Args:
            phenomena: List of phenomena to visualize
            title: Chart title
            include_details: Whether to include phenomenon details panel

        Returns:
            Complete HTML string
        """
        chart_data = self.generate_chart_data(phenomena)

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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        header {{
            text-align: center;
            margin-bottom: 2rem;
        }}

        header h1 {{
            font-size: 2.5rem;
            color: #fff;
            margin-bottom: 0.5rem;
        }}

        header p {{
            color: #9ca3af;
            font-size: 1.1rem;
        }}

        .main-content {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            justify-content: center;
        }}

        .radar-container {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        }}

        #radar-chart {{
            display: block;
        }}

        .legend {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }}

        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}

        .details-panel {{
            flex: 1;
            min-width: 350px;
            max-width: 500px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 1rem;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
        }}

        .details-panel h2 {{
            color: #fff;
            margin-bottom: 1rem;
            font-size: 1.3rem;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 0.5rem;
        }}

        .detail-section {{
            margin-bottom: 1rem;
        }}

        .detail-section h3 {{
            font-size: 0.85rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.3rem;
        }}

        .detail-section p {{
            font-size: 0.95rem;
            line-height: 1.5;
        }}

        .tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .tag {{
            background: rgba(255, 255, 255, 0.1);
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.8rem;
        }}

        .type-badge {{
            display: inline-block;
            padding: 0.3rem 0.8rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        .instructions {{
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 1rem;
        }}

        .phenomenon-list {{
            margin-top: 1rem;
        }}

        .phenomenon-item {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: background 0.2s;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .phenomenon-item:hover {{
            background: rgba(255, 255, 255, 0.1);
        }}

        .phenomenon-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .phenomenon-title {{
            font-size: 0.9rem;
            flex: 1;
        }}

        .phenomenon-horizon {{
            font-size: 0.75rem;
            color: #6b7280;
        }}

        /* Tooltip */
        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: #fff;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            font-size: 0.85rem;
            max-width: 250px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            z-index: 100;
        }}

        .tooltip.visible {{
            opacity: 1;
        }}

        .tooltip h4 {{
            margin-bottom: 0.25rem;
        }}

        .tooltip p {{
            color: #9ca3af;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p>Interactive visualization of emerging trends, signals, and disruptions</p>
        </header>

        <div class="main-content">
            <div class="radar-container">
                <svg id="radar-chart" width="{self.width}" height="{self.height}"></svg>
                <div class="legend" id="legend"></div>
                <p class="instructions">Hover over points for details. Click to select.</p>
            </div>

            <div class="details-panel" id="details-panel">
                <h2>Phenomenon Details</h2>
                <div id="details-content">
                    <p style="color: #6b7280;">Select a phenomenon from the radar to view details.</p>
                </div>
                <div class="phenomenon-list" id="phenomenon-list"></div>
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip"></div>

    <script>
        const chartData = {json.dumps(chart_data)};

        // Initialize the radar chart
        function initRadar() {{
            const svg = document.getElementById('radar-chart');
            const config = chartData.config;

            // Draw background rings
            chartData.rings.forEach((ring, i) => {{
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', config.centerX);
                circle.setAttribute('cy', config.centerY);
                circle.setAttribute('r', ring.radius);
                circle.setAttribute('fill', 'none');
                circle.setAttribute('stroke', 'rgba(255, 255, 255, 0.1)');
                circle.setAttribute('stroke-width', '1');
                circle.setAttribute('stroke-dasharray', '4 4');
                svg.appendChild(circle);

                // Ring label
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', config.centerX);
                text.setAttribute('y', config.centerY - ring.radius - 5);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('fill', 'rgba(255, 255, 255, 0.4)');
                text.setAttribute('font-size', '10');
                text.textContent = ring.name;
                svg.appendChild(text);
            }});

            // Draw sector lines and labels
            chartData.sectors.forEach(sector => {{
                const angleRad = sector.angle * Math.PI / 180;
                const x2 = config.centerX + config.maxRadius * Math.cos(angleRad);
                const y2 = config.centerY + config.maxRadius * Math.sin(angleRad);

                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', config.centerX);
                line.setAttribute('y1', config.centerY);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                line.setAttribute('stroke', 'rgba(255, 255, 255, 0.05)');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);

                // Sector label
                const labelRadius = config.maxRadius + 20;
                const labelX = config.centerX + labelRadius * Math.cos(angleRad);
                const labelY = config.centerY + labelRadius * Math.sin(angleRad);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', labelX);
                text.setAttribute('y', labelY);
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('dominant-baseline', 'middle');
                text.setAttribute('fill', 'rgba(255, 255, 255, 0.5)');
                text.setAttribute('font-size', '11');
                text.textContent = sector.name;
                svg.appendChild(text);
            }});

            // Draw center point
            const center = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            center.setAttribute('cx', config.centerX);
            center.setAttribute('cy', config.centerY);
            center.setAttribute('r', 5);
            center.setAttribute('fill', '#fff');
            center.setAttribute('opacity', '0.3');
            svg.appendChild(center);

            // Draw phenomenon points
            chartData.points.forEach(point => {{
                const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                group.setAttribute('class', 'phenomenon-point');
                group.setAttribute('data-id', point.id);
                group.style.cursor = 'pointer';

                // Outer glow
                const glow = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                glow.setAttribute('cx', point.x);
                glow.setAttribute('cy', point.y);
                glow.setAttribute('r', point.size + 4);
                glow.setAttribute('fill', point.color);
                glow.setAttribute('opacity', '0.2');
                group.appendChild(glow);

                // Main point
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', point.x);
                circle.setAttribute('cy', point.y);
                circle.setAttribute('r', point.size);
                circle.setAttribute('fill', point.color);
                circle.setAttribute('stroke', '#fff');
                circle.setAttribute('stroke-width', '2');
                group.appendChild(circle);

                // Event handlers
                group.addEventListener('mouseenter', (e) => showTooltip(e, point));
                group.addEventListener('mouseleave', hideTooltip);
                group.addEventListener('click', () => selectPhenomenon(point));

                svg.appendChild(group);
            }});

            // Build legend
            const legend = document.getElementById('legend');
            chartData.legend.forEach(item => {{
                const div = document.createElement('div');
                div.className = 'legend-item';
                div.innerHTML = `<span class="legend-dot" style="background: ${{item.color}}"></span>${{item.label}}`;
                legend.appendChild(div);
            }});

            // Build phenomenon list
            const list = document.getElementById('phenomenon-list');
            chartData.points.forEach(point => {{
                const div = document.createElement('div');
                div.className = 'phenomenon-item';
                div.innerHTML = `
                    <span class="phenomenon-dot" style="background: ${{point.color}}"></span>
                    <span class="phenomenon-title">${{point.title}}</span>
                    <span class="phenomenon-horizon">${{point.timeHorizon.replace('_', '-')}}</span>
                `;
                div.addEventListener('click', () => {{
                    selectPhenomenon(point);
                    highlightPoint(point.id);
                }});
                list.appendChild(div);
            }});
        }}

        function showTooltip(e, point) {{
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = `
                <h4>${{point.title}}</h4>
                <p>${{point.phenomenonType.replace('_', ' ')}} | ${{point.timeHorizon.replace('_', '-')}}</p>
            `;
            tooltip.style.left = (e.pageX + 15) + 'px';
            tooltip.style.top = (e.pageY + 15) + 'px';
            tooltip.classList.add('visible');
        }}

        function hideTooltip() {{
            document.getElementById('tooltip').classList.remove('visible');
        }}

        function selectPhenomenon(point) {{
            const content = document.getElementById('details-content');
            content.innerHTML = `
                <div class="detail-section">
                    <span class="type-badge" style="background: ${{point.color}}; color: #fff;">
                        ${{point.phenomenonType.replace('_', ' ').toUpperCase()}}
                    </span>
                </div>
                <div class="detail-section">
                    <h3>Time Horizon</h3>
                    <p>${{point.timeHorizon.replace('_', ' ').replace('term', '-term')}}</p>
                </div>
                <div class="detail-section">
                    <h3>Tags</h3>
                    <div class="tags">
                        ${{point.tags.map(t => `<span class="tag">${{t}}</span>`).join('')}}
                    </div>
                </div>
                <div class="detail-section">
                    <h3>Summary</h3>
                    <p>${{point.summary}}</p>
                </div>
            `;

            // Update panel title
            document.querySelector('.details-panel h2').textContent = point.title;
        }}

        function highlightPoint(id) {{
            // Reset all points
            document.querySelectorAll('.phenomenon-point').forEach(g => {{
                g.querySelector('circle:last-child').setAttribute('stroke-width', '2');
            }});
            // Highlight selected
            const selected = document.querySelector(`.phenomenon-point[data-id="${{id}}"]`);
            if (selected) {{
                selected.querySelector('circle:last-child').setAttribute('stroke-width', '4');
            }}
        }}

        // Initialize on load
        document.addEventListener('DOMContentLoaded', initRadar);
    </script>
</body>
</html>"""

        return html

    def save_html(
        self,
        phenomena: list[Phenomenon],
        output_path: str,
        title: str = "Foresight Radar",
    ) -> None:
        """
        Save the radar chart as an HTML file.

        Args:
            phenomena: List of phenomena to visualize
            output_path: Path to save the HTML file
            title: Chart title
        """
        html = self.generate_html(phenomena, title)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
