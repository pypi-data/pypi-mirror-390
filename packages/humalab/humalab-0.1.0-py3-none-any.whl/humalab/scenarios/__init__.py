"""Scenario management and configuration.

This module provides the Scenario class and related utilities for managing scenario
configurations with probabilistic distributions, supporting randomized scenario generation
for robotics experiments.
"""

from .scenario import Scenario
from .scenario_operator import list_scenarios, get_scenario

__all__ = ["Scenario", "list_scenarios", "get_scenario"]