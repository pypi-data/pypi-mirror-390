"""
Utility Functions for M/M/1 Calculations

Provides theoretical metric calculations and validation utilities.
"""

from .metrics import (
    validate_mm1_config,
    calculate_theoretical_metrics,
    compare_simulation_to_theory
)

__all__ = [
    "validate_mm1_config",
    "calculate_theoretical_metrics",
    "compare_simulation_to_theory"
]
