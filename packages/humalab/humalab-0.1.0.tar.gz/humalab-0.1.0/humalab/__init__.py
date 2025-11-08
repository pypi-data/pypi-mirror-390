"""HumaLab SDK - Python library for robotics and embodied AI experimentation.

The HumaLab SDK provides tools for managing scenarios, runs, episodes, and metrics
for robotics experiments and simulations. It supports probabilistic scenario generation,
metric tracking, and integration with the HumaLab platform.

Main components:
- init: Context manager for creating and managing runs
- Run: Represents a complete experimental run
- Episode: Represents a single episode within a run
- Scenario: Manages scenario configurations with distributions
- Metrics: Base class for tracking various metric types
"""

from humalab.humalab import init, finish, login
from humalab import assets
from humalab import metrics
from humalab import scenarios
from humalab.run import Run
from humalab.constants import MetricDimType, GraphType
# from humalab import evaluators

__all__ = [
    "init",
    "finish",
    "login",
    "assets",
    "metrics",
    "scenarios",
    "Run",
    "MetricDimType",
    "GraphType",
#    "evaluators",
]