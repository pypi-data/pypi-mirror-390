"""
M/M/1 Queue Theoretical Metrics Calculations

Provides functions for:
- Parameter validation
- Theoretical metric calculations
- Simulation result comparisons
"""

from typing import Dict, Any, Optional, List


def validate_mm1_config(
    arrival_rate: float,
    service_rate: float,
    simulation_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    Validate M/M/1 configuration parameters

    Args:
        arrival_rate: Customer arrival rate (λ)
        service_rate: Service rate (μ)
        simulation_time: Simulation duration (optional)

    Returns:
        Dict with:
            - valid: bool
            - errors: List[str]
            - utilization: float (if valid)
            - warnings: List[str] (if any)
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Validate arrival_rate
    if arrival_rate <= 0:
        errors.append(f"arrival_rate must be positive (got {arrival_rate})")

    # Validate service_rate
    if service_rate <= 0:
        errors.append(f"service_rate must be positive (got {service_rate})")

    # Check stability condition
    if arrival_rate > 0 and service_rate > 0:
        rho = arrival_rate / service_rate

        if arrival_rate >= service_rate:
            errors.append(
                f"System is unstable: arrival_rate ({arrival_rate}) >= "
                f"service_rate ({service_rate}). Utilization ρ = {rho:.4f} >= 1"
            )
        elif rho > 0.95:
            warnings.append(
                f"Very high utilization (ρ = {rho:.4f}). "
                "System may take long time to reach steady state."
            )
        elif rho > 0.9:
            warnings.append(
                f"High utilization (ρ = {rho:.4f}). "
                "Consider longer simulation time for accurate results."
            )

    # Validate simulation_time if provided
    if simulation_time is not None:
        if simulation_time <= 0:
            errors.append(f"simulation_time must be positive (got {simulation_time})")
        elif simulation_time < 1000:
            warnings.append(
                f"Short simulation time ({simulation_time}). "
                "May not provide accurate steady-state estimates."
            )

    result = {
        "valid": len(errors) == 0,
        "errors": errors,
    }

    if warnings:
        result["warnings"] = warnings

    if result["valid"]:
        result["utilization"] = arrival_rate / service_rate

    return result


def calculate_theoretical_metrics(
    arrival_rate: float,
    service_rate: float
) -> Dict[str, float]:
    """
    Calculate theoretical M/M/1 performance metrics

    Uses standard M/M/1 formulas to compute exact values.

    Args:
        arrival_rate: λ (customers per time unit)
        service_rate: μ (customers per time unit)

    Returns:
        Dict containing:
            - utilization: ρ = λ/μ
            - avg_queue_length: L_q = ρ²/(1-ρ)
            - avg_num_in_system: L = ρ/(1-ρ)
            - avg_waiting_time: W_q = ρ/(μ(1-ρ))
            - avg_system_time: W = 1/(μ(1-ρ))

    Raises:
        ValueError: If system is unstable (λ >= μ)
    """
    if arrival_rate >= service_rate:
        rho = arrival_rate / service_rate
        raise ValueError(
            f"System is unstable (ρ = {rho:.4f} >= 1). "
            f"arrival_rate ({arrival_rate}) must be less than service_rate ({service_rate})"
        )

    rho = arrival_rate / service_rate

    return {
        "utilization": rho,
        "avg_queue_length": rho**2 / (1 - rho),
        "avg_num_in_system": rho / (1 - rho),
        "avg_waiting_time": rho / (service_rate * (1 - rho)),
        "avg_system_time": 1 / (service_rate * (1 - rho))
    }


def compare_simulation_to_theory(
    simulation_metrics: Dict[str, float],
    theoretical_metrics: Dict[str, float],
    metrics_to_compare: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Compare simulation results with theoretical values

    Args:
        simulation_metrics: Metrics from simulation run
        theoretical_metrics: Theoretical metrics from formulas
        metrics_to_compare: List of metric names to compare (default: all common)

    Returns:
        Dict with:
            - comparisons: List of {metric, sim_value, theo_value, abs_error, rel_error_pct}
            - mean_abs_error_pct: Average absolute percentage error
            - max_error_pct: Maximum percentage error
            - within_10pct: bool (all errors < 10%)
    """
    if metrics_to_compare is None:
        # Compare all common metrics
        metrics_to_compare = list(
            set(simulation_metrics.keys()) & set(theoretical_metrics.keys())
        )

    comparisons = []
    errors_pct = []

    for metric in metrics_to_compare:
        sim_value = simulation_metrics.get(metric)
        theo_value = theoretical_metrics.get(metric)

        if sim_value is None or theo_value is None:
            continue

        abs_error = abs(sim_value - theo_value)

        # Handle zero theoretical values
        if theo_value == 0:
            rel_error_pct = 0.0 if sim_value == 0 else float('inf')
        else:
            rel_error_pct = (abs_error / abs(theo_value)) * 100

        comparisons.append({
            "metric": metric,
            "simulation": sim_value,
            "theoretical": theo_value,
            "absolute_error": abs_error,
            "relative_error_pct": rel_error_pct
        })

        if rel_error_pct != float('inf'):
            errors_pct.append(rel_error_pct)

    if not errors_pct:
        return {
            "comparisons": comparisons,
            "mean_abs_error_pct": None,
            "max_error_pct": None,
            "within_10pct": None
        }

    mean_error = sum(errors_pct) / len(errors_pct)
    max_error = max(errors_pct)

    return {
        "comparisons": comparisons,
        "mean_abs_error_pct": mean_error,
        "max_error_pct": max_error,
        "within_10pct": all(e < 10.0 for e in errors_pct),
        "accuracy_grade": _grade_accuracy(mean_error)
    }


def _grade_accuracy(mean_error_pct: float) -> str:
    """
    Grade accuracy based on mean percentage error

    Args:
        mean_error_pct: Mean absolute percentage error

    Returns:
        Grade string: 'Excellent', 'Good', 'Fair', 'Poor'
    """
    if mean_error_pct < 5.0:
        return "Excellent"
    elif mean_error_pct < 10.0:
        return "Good"
    elif mean_error_pct < 20.0:
        return "Fair"
    else:
        return "Poor"


def get_recommended_simulation_time(
    arrival_rate: float,
    service_rate: float,
    min_customers: int = 1000
) -> float:
    """
    Recommend simulation time based on parameters

    Ensures enough customers to get stable estimates.

    Args:
        arrival_rate: λ
        service_rate: μ
        min_customers: Minimum number of expected customers

    Returns:
        Recommended simulation time
    """
    rho = arrival_rate / service_rate

    # Base time to serve min_customers
    base_time = min_customers / arrival_rate

    # Adjust for high utilization (need more time to reach steady state)
    if rho > 0.9:
        multiplier = 3.0
    elif rho > 0.8:
        multiplier = 2.0
    else:
        multiplier = 1.5

    return base_time * multiplier
