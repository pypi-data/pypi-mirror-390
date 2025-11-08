"""Constants and enumerations used throughout the HumaLab SDK."""

from enum import Enum


RESERVED_NAMES = {
    "sceanario",
    "seed",
}
"""Set of reserved names that cannot be used for metric or artifact keys."""

DEFAULT_PROJECT = "default"
"""Default project name used when no project is specified."""


class ArtifactType(Enum):
    """Types of artifacts that can be stored"""
    METRICS = "metrics" # Run & Episode
    SCENARIO_STATS = "scenario_stats" # Run only
    PYTHON = "python" # Run & Episode
    CODE = "code" # Run & Episode (YAML)


class MetricType(Enum):
    """Enumeration of metric types.

    Maps to corresponding artifact types for metrics and scenario statistics.
    """
    METRICS = ArtifactType.METRICS.value
    SCENARIO_STATS = ArtifactType.SCENARIO_STATS.value


class GraphType(Enum):
    """Types of graphs supported by Humalab."""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    GAUSSIAN = "gaussian"
    THREE_D_MAP = "3d_map"


class MetricDimType(Enum):
    """Types of metric dimensions"""
    ZERO_D = "0d"
    ONE_D = "1d"
    TWO_D = "2d"
    THREE_D = "3d"