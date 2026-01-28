"""
Configuration management for the AI Foresight Scanner.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class SearchConfig:
    """Search engine configuration."""
    backend: str = "auto"  # "brave", "serper", or "auto"
    results_per_query: int = 10
    use_johari_heuristic: bool = True
    preferred_domains: list[str] = field(default_factory=list)


@dataclass
class AnalyzerConfig:
    """AI analyzer configuration."""
    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 4096
    strict_source_validation: bool = False


@dataclass
class OutputConfig:
    """Output configuration."""
    output_dir: str = "./output"
    formats: list[str] = field(default_factory=lambda: ["html", "json", "markdown"])
    generate_radar: bool = True
    radar_width: int = 800
    radar_height: int = 800


@dataclass
class Config:
    """Main configuration for the AI Foresight Scanner."""
    search: SearchConfig = field(default_factory=SearchConfig)
    analyzer: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

    # API Keys (can also be set via environment variables)
    anthropic_api_key: Optional[str] = None
    search_api_key: Optional[str] = None

    def __post_init__(self):
        # Load API keys from environment if not set
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.search_api_key:
            self.search_api_key = (
                os.getenv("SERPER_API_KEY") or os.getenv("BRAVE_API_KEY")
            )


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file or use defaults.

    Args:
        config_path: Optional path to YAML config file

    Returns:
        Config object
    """
    if config_path and Path(config_path).exists():
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)

        search_config = SearchConfig(**data.get("search", {}))
        analyzer_config = AnalyzerConfig(**data.get("analyzer", {}))
        output_config = OutputConfig(**data.get("output", {}))

        return Config(
            search=search_config,
            analyzer=analyzer_config,
            output=output_config,
            anthropic_api_key=data.get("anthropic_api_key"),
            search_api_key=data.get("search_api_key"),
        )

    return Config()


def save_config(config: Config, config_path: str) -> None:
    """
    Save configuration to YAML file.

    Args:
        config: Config object to save
        config_path: Path to save the config
    """
    data = {
        "search": {
            "backend": config.search.backend,
            "results_per_query": config.search.results_per_query,
            "use_johari_heuristic": config.search.use_johari_heuristic,
            "preferred_domains": config.search.preferred_domains,
        },
        "analyzer": {
            "model": config.analyzer.model,
            "temperature": config.analyzer.temperature,
            "max_tokens": config.analyzer.max_tokens,
            "strict_source_validation": config.analyzer.strict_source_validation,
        },
        "output": {
            "output_dir": config.output.output_dir,
            "formats": config.output.formats,
            "generate_radar": config.output.generate_radar,
            "radar_width": config.output.radar_width,
            "radar_height": config.output.radar_height,
        },
    }

    with open(config_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
