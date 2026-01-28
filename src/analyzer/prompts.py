"""
LLM prompts for foresight analysis.

These prompts are designed to structure information into the
card-based foresight format.
"""


class ForesightPrompts:
    """
    Collection of prompts for AI-powered foresight analysis.

    All prompts are designed to:
    - Maintain analytical neutrality
    - Distinguish evidence from assumptions
    - Avoid hype and deterministic language
    - Acknowledge uncertainty appropriately
    """

    SYSTEM_PROMPT = """You are a professional foresight analyst with expertise in futures research, strategic foresight, and horizon scanning. Your role is to analyze information about emerging trends, weak signals, and potential disruptions in a rigorous, analytical manner.

Key principles:
1. ANALYTICAL NEUTRALITY: Operate at a neutral, analytical level. Do not assume a specific organization or sector unless provided.

2. EVIDENCE-BASED: Distinguish clearly between evidence, assumptions, signals, and uncertainties. All factual claims must be supported by cited sources.

3. NO HYPE: Avoid deterministic language, sensationalism, or claims of privileged information. Be transparent about confidence levels.

4. UNCERTAINTY ACKNOWLEDGEMENT: Clearly acknowledge what is known, what is uncertain, and what is genuinely unknown.

5. EXPLORATORY SCENARIOS: Frame future scenarios as exploratory alternatives, not predictions. Present contrasting but plausible directions.

6. SOURCE QUALITY: Prefer credible, publicly available sources: peer-reviewed research, intergovernmental organizations, reputable policy institutes, established academic publishers, and well-regarded industry reports.

When user prompts lack detail, make reasonable high-level assumptions and state them explicitly. Only ask clarifying questions when they materially affect relevance."""

    PHENOMENON_CLASSIFICATION = """Analyze the following information about a phenomenon and classify it:

CONTENT TO ANALYZE:
{content}

SOURCES:
{sources}

Classify this phenomenon using the following framework:

1. PHENOMENON TYPE (choose one):
   - STRENGTHENING: A growing trend with increasing momentum and evidence
   - WEAKENING: A declining trend that is losing momentum
   - WEAK_SIGNAL: An early indicator with uncertain trajectory and limited evidence
   - WILD_CARD: A low probability but high impact potential event

2. TIME HORIZON (choose primary):
   - NEAR_TERM (0-5 years): Evidence of imminent or current acceleration
   - MID_TERM (5-10 years): Likely to mature or peak in this period
   - LONG_TERM (10-20 years): Structural change with extended timeline
   - UNCERTAIN: For weak signals where timing cannot be assessed

3. THEMATIC TAGS (select all applicable):
   - TECHNOLOGY, SOCIETY, ECONOMY, ENVIRONMENT, GEOPOLITICS, HEALTH, GOVERNANCE, SECURITY, DEMOGRAPHICS, CULTURE

Provide your classification with a brief rationale for each choice. Be explicit about uncertainty.

OUTPUT FORMAT (JSON):
{{
  "phenomenon_type": "...",
  "type_rationale": "...",
  "time_horizon": "...",
  "timing_rationale": "...",
  "uncertainty_note": "...",
  "tags": ["...", "..."],
  "confidence_level": "low|moderate|high"
}}"""

    SUMMARY_GENERATION = """Generate a professional foresight summary for the following phenomenon:

TITLE: {title}
TYPE: {phenomenon_type}
CONTENT: {content}
SOURCES: {sources}

Create a single, well-crafted paragraph (150-250 words) that:
1. Explains WHAT the phenomenon is in clear, accessible terms
2. Describes WHY it matters now (current relevance and urgency)
3. Outlines the CURRENT STATE of play (where things stand today)
4. Sketches the most PLAUSIBLE FUTURE paths and impacts

Requirements:
- Write in third person, analytical voice
- Integrate source citations naturally using [Source Name](URL) markdown format
- Distinguish between established facts and emerging signals
- Avoid superlatives, hype, or deterministic language
- Acknowledge key uncertainties

OUTPUT: The summary paragraph with embedded hyperlinks."""

    DRIVER_ANALYSIS = """Analyze the key drivers shaping this phenomenon:

PHENOMENON: {title}
SUMMARY: {summary}
CONTENT: {content}

Identify 4-6 key drivers using the STEEP+G framework:
- Social: Demographic shifts, lifestyle changes, cultural values
- Technological: Innovation, R&D trends, digital transformation
- Economic: Market forces, financial flows, business models
- Environmental: Climate, resources, sustainability pressures
- Political: Regulation, governance, geopolitical dynamics
- Governance: Institutional capacity, international cooperation

For each driver:
1. Name it concisely (3-7 words)
2. Describe its influence (2-3 sentences)
3. Assess its strength: "strong" (clear evidence), "moderate" (mixed signals), "emerging" (early indicators)
4. Note key sources if available

OUTPUT FORMAT (JSON):
{{
  "drivers": [
    {{
      "name": "...",
      "category": "social|technological|economic|environmental|political|governance",
      "description": "...",
      "strength": "strong|moderate|emerging",
      "source_references": ["..."]
    }}
  ]
}}"""

    SCENARIO_GENERATION = """Generate two contrasting but plausible future scenarios for this phenomenon:

PHENOMENON: {title}
SUMMARY: {summary}
DRIVERS: {drivers}
TIME HORIZON: {time_horizon}

Create two scenarios representing different plausible directions:

SCENARIO A: A scenario where enabling drivers strengthen and barriers diminish
SCENARIO B: A scenario where barriers strengthen or countervailing forces emerge

For each scenario provide:

1. NAME: A memorable, descriptive title (3-6 words)

2. DESCRIPTION: A vivid but analytical paragraph (100-150 words) describing this future state

3. KEY ASSUMPTIONS: 3-4 critical assumptions that must hold for this scenario

4. PROBABILITY ASSESSMENT: "plausible" (could reasonably happen), "possible" (requires specific conditions), or "emerging" (early signals only)

5. IMPACT ASSESSMENT:
   - Risks: 3-4 key risks for organizations/systems
   - Opportunities: 3-4 potential opportunities
   - Affected sectors: Which sectors most impacted
   - Key stakeholders: Who needs to pay attention

6. DEVELOPMENT PATH: 3-4 concrete steps/milestones toward this scenario, with:
   - Step description
   - Indicative timeline (e.g., "2025-2027", "Within 3 years")
   - Indicators to monitor

IMPORTANT: Scenarios are exploratory, not predictive. Frame them as alternatives to consider, not forecasts.

OUTPUT FORMAT (JSON):
{{
  "scenarios": [
    {{
      "name": "...",
      "description": "...",
      "probability_assessment": "...",
      "key_assumptions": ["...", "..."],
      "impact_assessment": {{
        "risks": ["..."],
        "opportunities": ["..."],
        "affected_sectors": ["..."],
        "affected_stakeholders": ["..."]
      }},
      "development_path": [
        {{
          "step_number": 1,
          "description": "...",
          "indicative_timeline": "...",
          "indicators_to_monitor": ["..."]
        }}
      ]
    }}
  ]
}}"""

    CONNECTIONS_ANALYSIS = """Analyze connections and implications for this phenomenon:

PHENOMENON: {title}
SUMMARY: {summary}
SCENARIOS: {scenarios}

Identify:

1. RELATED PHENOMENA (3-5):
   Other trends, signals, or disruptions that interact with this one.
   For each, briefly note the nature of the connection.

2. SECOND-ORDER EFFECTS (3-5):
   Downstream consequences that might emerge as this phenomenon develops.
   Think beyond direct impacts to systemic effects.

3. AREAS FOR EXPLORATION (2-4):
   Questions or domains that warrant deeper investigation.
   What gaps in understanding should be addressed?

4. ADDITIONAL READINGS (3-5):
   Suggest types of sources or specific topics for further research.
   These should complement (not duplicate) the core sources.

OUTPUT FORMAT (JSON):
{{
  "related_phenomena": [
    {{"phenomenon": "...", "connection": "..."}}
  ],
  "second_order_effects": ["...", "..."],
  "areas_for_exploration": ["...", "..."],
  "suggested_readings": [
    {{"topic": "...", "rationale": "..."}}
  ]
}}"""

    TIMING_ASSESSMENT = """Provide an expert timing assessment for this phenomenon:

PHENOMENON: {title}
TYPE: {phenomenon_type}
SUMMARY: {summary}
DRIVERS: {drivers}

Assess when this phenomenon is most likely to:
- ACCELERATE: When momentum is likely to build significantly
- PEAK: When at maximum influence or prevalence
- DECLINE: When waning (if applicable)

Use these time bands:
- Near-term: 2025-2030 (0-5 years)
- Mid-term: 2030-2035 (5-10 years)
- Long-term: 2035-2045 (10-20 years)

Provide:
1. A primary time horizon classification
2. Specific phase estimates (where assessable)
3. A rationale for your assessment (3-4 sentences)
4. An explicit uncertainty acknowledgement

Note: For WEAK_SIGNAL types, timing is inherently uncertain. Acknowledge this clearly.

OUTPUT FORMAT (JSON):
{{
  "primary_horizon": "near_term|mid_term|long_term|uncertain",
  "acceleration_phase": "...",
  "peak_phase": "...",
  "decline_phase": "...",
  "rationale": "...",
  "uncertainty_acknowledgement": "..."
}}"""

    TITLE_GENERATION = """Generate a concise, descriptive title for this phenomenon:

CONTENT SUMMARY: {content}

Requirements:
- 4-8 words maximum
- Captures the core phenomenon clearly
- Avoids jargon unless widely understood
- Neutral, analytical tone (no hype words)
- Should be distinctive enough to differentiate from similar phenomena

OUTPUT: Just the title, nothing else."""

    QUALITY_CHECK = """Review this foresight analysis for quality and completeness:

ANALYSIS:
{analysis}

Check for:

1. EVIDENCE QUALITY:
   - Are claims supported by cited sources?
   - Are sources credible and appropriate?
   - Is evidence distinguished from speculation?

2. ANALYTICAL BALANCE:
   - Is the tone neutral and professional?
   - Are multiple perspectives considered?
   - Are uncertainties acknowledged?

3. COMPLETENESS:
   - Are all required sections present?
   - Is sufficient detail provided?
   - Are connections and implications explored?

4. CLARITY:
   - Is language accessible and clear?
   - Are technical terms explained?
   - Is the structure logical?

Provide:
- Overall quality score (1-10)
- Specific issues found
- Suggestions for improvement

OUTPUT FORMAT (JSON):
{{
  "quality_score": 1-10,
  "issues": ["..."],
  "suggestions": ["..."],
  "passes_quality_threshold": true|false
}}"""

    JOHARI_WINDOW_GUIDANCE = """When researching and scanning for phenomena, use the Johari Window as a sense-checking heuristic:

OPEN AREA (Known to self, known to others):
- Well-documented dynamics
- Established trends with extensive coverage
- Search for: reports, statistics, market research, academic studies

BLIND AREA (Unknown to self, known to others):
- Widely discussed but under-recognized implications
- Perspectives from different domains or regions
- Search for: cross-sector impacts, international perspectives, contrarian views

HIDDEN AREA (Known to self, unknown to others):
- Emerging or sensitive signals with limited disclosure
- Early-stage developments not yet mainstream
- Search for: patents, startup activity, research preprints, specialist forums

UNKNOWN AREA (Unknown to self, unknown to others):
- Genuine unknowns and contested uncertainties
- Edge cases and wild cards
- Search for: scenario exercises, risk assessments, speculative research

NOTE: This heuristic informs what to search for and stress-tests completeness.
Outputs are NOT labeled or categorized using the Johari Window.
Results are presented only in the standard foresight structure."""
