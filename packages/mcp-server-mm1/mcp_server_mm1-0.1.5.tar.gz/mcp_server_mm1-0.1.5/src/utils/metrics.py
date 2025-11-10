"""
Metrics calculation and comparison utilities
"""

from typing import Dict, Tuple
import numpy as np


def calculate_error(simulated: float, theoretical: float) -> Tuple[float, float]:
    """
    Calculate absolute and relative error between simulated and theoretical values

    Args:
        simulated: Simulated value
        theoretical: Theoretical value

    Returns:
        Tuple of (absolute_error, relative_error_percentage)
    """
    absolute_error = abs(simulated - theoretical)
    relative_error = (absolute_error / abs(theoretical)) * 100 if theoretical != 0 else float('inf')

    return absolute_error, relative_error


def compare_metrics(simulated_metrics: Dict[str, float],
                   theoretical_metrics: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    """
    Compare simulated metrics with theoretical values

    Args:
        simulated_metrics: Dictionary of simulated metric values
        theoretical_metrics: Dictionary of theoretical metric values

    Returns:
        Dictionary with comparison results for each metric
    """
    comparison = {}

    for key in simulated_metrics:
        if key in theoretical_metrics:
            sim_value = simulated_metrics[key]
            theo_value = theoretical_metrics[key]
            abs_err, rel_err = calculate_error(sim_value, theo_value)

            comparison[key] = {
                'simulated': sim_value,
                'theoretical': theo_value,
                'absolute_error': abs_err,
                'relative_error_pct': rel_err,
                'acceptable': rel_err < 10.0  # 10% threshold
            }

    return comparison


def calculate_confidence_interval(data: list, confidence: float = 0.95) -> Tuple[float, float, float]:
    """
    Calculate confidence interval for a dataset

    Args:
        data: List of values
        confidence: Confidence level (default 0.95 for 95%)

    Returns:
        Tuple of (mean, lower_bound, upper_bound)
    """
    if not data:
        return 0.0, 0.0, 0.0

    mean = np.mean(data)
    std = np.std(data, ddof=1)
    n = len(data)

    # Calculate standard error
    se = std / np.sqrt(n)

    # Z-score for confidence level
    from scipy import stats
    z = stats.norm.ppf((1 + confidence) / 2)

    margin = z * se
    return mean, mean - margin, mean + margin
