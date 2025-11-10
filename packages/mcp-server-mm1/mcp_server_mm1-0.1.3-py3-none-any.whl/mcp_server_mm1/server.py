"""
M/M/1 Queue Simulation MCP Server

A Model Context Protocol server providing resources, tools, and prompts
for M/M/1 queuing system simulation and analysis.

Resources:
    - mm1://schema - Complete M/M/1 schema
    - mm1://parameters - Parameter definitions
    - mm1://metrics - Performance metrics
    - mm1://formulas - Theoretical formulas
    - mm1://guidelines - Implementation guidelines
    - mm1://examples - Example configurations
    - mm1://literature - References and literature

Tools:
    - validate_config - Validate M/M/1 parameters
    - calculate_theoretical_metrics - Compute theoretical values
    - run_simulation - Execute SimPy simulation
    - compare_results - Compare simulation vs theory
    - recommend_parameters - Suggest optimal parameters

Prompts:
    - generate_simulation_code - Create complete SimPy code
    - explain_mm1_theory - Explain M/M/1 theory
    - analyze_results - Analyze simulation results
    - debug_simulation - Debug simulation issues
"""

from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import json

# Import our modules
from .schemas import MM1_SCHEMA
from .utils.metrics import (
    validate_mm1_config,
    calculate_theoretical_metrics,
    compare_simulation_to_theory,
    get_recommended_simulation_time
)
from .simulations.mm1_queue import run_mm1_simulation

# ============================================================================
# Initialize FastMCP Server
# ============================================================================

mcp = FastMCP("MM1 Simulation Server", version="0.1.3")


# ============================================================================
# RESOURCES: Data Providers
# ============================================================================

@mcp.resource("mm1://schema")
def get_full_schema() -> str:
    """
    Complete M/M/1 queue system schema

    Returns the full schema including parameters, metrics, formulas,
    implementation guidelines, and example use cases.
    """
    return json.dumps(MM1_SCHEMA, indent=2)


@mcp.resource("mm1://parameters")
def get_parameters() -> str:
    """
    M/M/1 parameter definitions

    Returns detailed information about input parameters including
    symbols, types, constraints, and examples.
    """
    return json.dumps({
        "parameters": MM1_SCHEMA["parameters"],
        "system_characteristics": MM1_SCHEMA["system_characteristics"]
    }, indent=2)


@mcp.resource("mm1://metrics")
def get_metrics() -> str:
    """
    M/M/1 performance metrics

    Returns definitions of all performance metrics that can be
    calculated, including required and optional metrics.
    """
    return json.dumps({
        "performance_metrics": MM1_SCHEMA["performance_metrics"]
    }, indent=2)


@mcp.resource("mm1://formulas")
def get_formulas() -> str:
    """
    Theoretical formulas for M/M/1 queue

    Returns mathematical formulas for calculating exact
    performance metrics in steady state.
    """
    formulas = {
        "stability_condition": MM1_SCHEMA["theoretical_validation"]["stability_condition"],
        "formulas": MM1_SCHEMA["theoretical_validation"]["formulas"],
        "little_law": MM1_SCHEMA["theoretical_validation"]["little_law"]
    }
    return json.dumps(formulas, indent=2)


@mcp.resource("mm1://guidelines")
def get_implementation_guidelines() -> str:
    """
    Implementation guidelines for M/M/1 simulation

    Returns best practices, required structure, validation rules,
    and error handling guidelines for implementing M/M/1 simulations.
    """
    return json.dumps({
        "implementation_guidelines": MM1_SCHEMA["implementation_guidelines"],
        "output_requirements": MM1_SCHEMA["output_requirements"]
    }, indent=2)


@mcp.resource("mm1://examples")
def get_examples() -> str:
    """
    Example M/M/1 configurations

    Returns pre-configured examples for low, medium, and high
    utilization scenarios.
    """
    return json.dumps({
        "example_use_cases": MM1_SCHEMA["example_use_cases"]
    }, indent=2)


@mcp.resource("mm1://literature")
def get_literature() -> str:
    """
    References and literature for M/M/1 queues

    Returns citations and resources for learning more about
    M/M/1 queuing theory and simulation.
    """
    literature = {
        "foundational_texts": [
            {
                "title": "Introduction to Queueing Theory",
                "author": "Robert B. Cooper",
                "year": 1981,
                "description": "Classic text on queueing theory fundamentals"
            },
            {
                "title": "Fundamentals of Queueing Theory",
                "authors": ["Donald Gross", "John F. Shortie", "James M. Thompson", "Carl M. Harris"],
                "edition": "5th",
                "year": 2018,
                "description": "Comprehensive modern treatment of queueing systems"
            }
        ],
        "simulation_resources": [
            {
                "title": "SimPy Documentation",
                "url": "https://simpy.readthedocs.io/",
                "description": "Official SimPy discrete event simulation framework documentation"
            },
            {
                "title": "Simulation Modeling and Analysis",
                "authors": ["Averill M. Law"],
                "edition": "5th",
                "year": 2015,
                "description": "Standard textbook on simulation methodology"
            }
        ],
        "online_resources": [
            {
                "title": "M/M/1 Queue - Wikipedia",
                "url": "https://en.wikipedia.org/wiki/M/M/1_queue",
                "description": "Overview with formulas and examples"
            }
        ]
    }
    return json.dumps(literature, indent=2)


# ============================================================================
# TOOLS: Executable Functions
# ============================================================================

@mcp.tool()
def validate_config(
    arrival_rate: float,
    service_rate: float,
    simulation_time: float = 10000.0
) -> Dict[str, Any]:
    """
    Validate M/M/1 configuration parameters

    Checks parameter validity and system stability condition.

    Args:
        arrival_rate: Customer arrival rate (λ)
        service_rate: Service rate (μ)
        simulation_time: Simulation duration

    Returns:
        Dictionary with validation result:
            - valid: bool
            - errors: List[str] (if any)
            - warnings: List[str] (if any)
            - utilization: float (if valid)
    """
    return validate_mm1_config(arrival_rate, service_rate, simulation_time)


@mcp.tool()
def calculate_metrics(
    arrival_rate: float,
    service_rate: float
) -> Dict[str, float]:
    """
    Calculate theoretical M/M/1 performance metrics

    Uses exact formulas to compute steady-state performance.

    Args:
        arrival_rate: λ (customers per time unit)
        service_rate: μ (customers per time unit)

    Returns:
        Dictionary of theoretical metrics:
            - utilization: ρ = λ/μ
            - avg_queue_length: L_q = ρ²/(1-ρ)
            - avg_num_in_system: L = ρ/(1-ρ)
            - avg_waiting_time: W_q
            - avg_system_time: W

    Raises:
        ValueError: If system is unstable (λ >= μ)
    """
    try:
        return calculate_theoretical_metrics(arrival_rate, service_rate)
    except ValueError as e:
        return {"error": str(e)}


@mcp.tool()
async def run_simulation(
    arrival_rate: float,
    service_rate: float,
    simulation_time: float = 10000.0,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Run M/M/1 queue simulation using SimPy

    Executes discrete event simulation and returns performance metrics.

    Args:
        arrival_rate: λ (customers per time unit)
        service_rate: μ (customers per time unit)
        simulation_time: Duration of simulation
        random_seed: Random seed for reproducibility

    Returns:
        Dictionary with:
            - simulation_metrics: Dict of simulated values
            - theoretical_metrics: Dict of exact values
            - comparison: Comparison analysis
            - config: Simulation configuration used
    """
    # Validate first
    validation = validate_mm1_config(arrival_rate, service_rate, simulation_time)
    if not validation["valid"]:
        return {
            "error": "Invalid configuration",
            "details": validation
        }

    try:
        # Run simulation
        sim_metrics = run_mm1_simulation(
            arrival_rate=arrival_rate,
            service_rate=service_rate,
            simulation_time=simulation_time,
            random_seed=random_seed
        )

        # Calculate theoretical
        theo_metrics = calculate_theoretical_metrics(arrival_rate, service_rate)

        # Compare
        comparison = compare_simulation_to_theory(sim_metrics, theo_metrics)

        return {
            "simulation_metrics": sim_metrics,
            "theoretical_metrics": theo_metrics,
            "comparison": comparison,
            "config": {
                "arrival_rate": arrival_rate,
                "service_rate": service_rate,
                "simulation_time": simulation_time,
                "random_seed": random_seed
            }
        }

    except Exception as e:
        return {
            "error": f"Simulation failed: {str(e)}",
            "type": type(e).__name__
        }


@mcp.tool()
def compare_results(
    simulation_metrics: Dict[str, float],
    arrival_rate: float,
    service_rate: float
) -> Dict[str, Any]:
    """
    Compare simulation results with theoretical values

    Analyzes accuracy of simulation by comparing against exact formulas.

    Args:
        simulation_metrics: Dictionary of simulated performance metrics
        arrival_rate: λ used in simulation
        service_rate: μ used in simulation

    Returns:
        Comparison analysis with:
            - comparisons: Per-metric comparison
            - mean_abs_error_pct: Average error
            - max_error_pct: Maximum error
            - within_10pct: bool
            - accuracy_grade: Quality assessment
    """
    try:
        theo_metrics = calculate_theoretical_metrics(arrival_rate, service_rate)
        return compare_simulation_to_theory(simulation_metrics, theo_metrics)
    except ValueError as e:
        return {"error": str(e)}


@mcp.tool()
def recommend_parameters(
    target_utilization: float = 0.7,
    service_rate: Optional[float] = None,
    min_customers: int = 1000
) -> Dict[str, Any]:
    """
    Recommend simulation parameters for target utilization

    Suggests appropriate arrival rate, service rate, and simulation time
    for a given target utilization level.

    Args:
        target_utilization: Desired ρ (default: 0.7)
        service_rate: Fixed μ (if None, suggests μ=10)
        min_customers: Minimum customers to simulate

    Returns:
        Recommended parameters and expected metrics
    """
    if not (0 < target_utilization < 1):
        return {
            "error": f"target_utilization must be between 0 and 1 (got {target_utilization})"
        }

    # Set default service rate if not provided
    if service_rate is None:
        service_rate = 10.0

    # Calculate arrival rate for target utilization
    arrival_rate = target_utilization * service_rate

    # Get recommended simulation time
    sim_time = get_recommended_simulation_time(
        arrival_rate, service_rate, min_customers
    )

    # Calculate expected metrics
    metrics = calculate_theoretical_metrics(arrival_rate, service_rate)

    return {
        "recommended_parameters": {
            "arrival_rate": arrival_rate,
            "service_rate": service_rate,
            "simulation_time": sim_time,
            "random_seed": 42
        },
        "expected_metrics": metrics,
        "scenario": {
            "target_utilization": target_utilization,
            "expected_customers": int(arrival_rate * sim_time),
            "difficulty": "High" if target_utilization > 0.9 else "Medium" if target_utilization > 0.7 else "Low"
        }
    }


# ============================================================================
# PROMPTS: Template Generators
# ============================================================================

@mcp.prompt()
def generate_simulation_code(
    arrival_rate: float,
    service_rate: float,
    simulation_time: float = 10000.0,
    include_validation: bool = True,
    include_visualization: bool = False
) -> str:
    """
    Generate complete M/M/1 simulation code prompt

    Creates a detailed prompt for generating production-ready
    SimPy simulation code.

    Args:
        arrival_rate: λ
        service_rate: μ
        simulation_time: Duration
        include_validation: Include theoretical comparison
        include_visualization: Include plotting code

    Returns:
        Formatted prompt for code generation
    """
    rho = arrival_rate / service_rate

    prompt = f"""Create a production-ready M/M/1 queue simulation in Python using SimPy.

## Configuration
- **Arrival rate (λ)**: {arrival_rate} customers/time unit
- **Service rate (μ)**: {service_rate} customers/time unit
- **Simulation time**: {simulation_time} time units
- **System utilization (ρ)**: {rho:.4f}
- **Stability**: {"✓ Stable" if rho < 1 else "✗ UNSTABLE - λ >= μ"}

## Requirements

### 1. Data Classes
```python
from dataclasses import dataclass

@dataclass
class MM1Config:
    arrival_rate: float
    service_rate: float
    simulation_time: float = 10000.0
    random_seed: int = 42

@dataclass
class PerformanceMetrics:
    utilization: float
    avg_queue_length: float
    avg_waiting_time: float
    avg_system_time: float
    customers_served: int
```

### 2. Simulation Class
Implement `MM1Queue` class with:
- `__init__(config: MM1Config)`: Initialize simulation
- `customer_process(customer_id: int)`: Handle single customer
- `arrival_process()`: Generate Poisson arrivals
- `run() -> PerformanceMetrics`: Execute and return results

### 3. Key Features
- Exponential inter-arrival times (Poisson process)
- Exponential service times
- Track queue length, waiting times, system times
- Configuration validation (λ > 0, μ > λ)
- Random seed for reproducibility
"""

    if include_validation:
        prompt += f"""
### 4. Theoretical Validation
Compare simulation results with theoretical formulas:

```python
# Theoretical M/M/1 formulas
rho = arrival_rate / service_rate
theoretical = {{
    'utilization': rho,
    'avg_queue_length': rho**2 / (1 - rho),
    'avg_waiting_time': rho / (service_rate * (1 - rho)),
    'avg_system_time': 1 / (service_rate * (1 - rho))
}}

# Print comparison
print("\\nSimulation vs Theory:")
for metric in ['avg_queue_length', 'avg_waiting_time', 'avg_system_time']:
    sim_val = simulation_metrics[metric]
    theo_val = theoretical[metric]
    error_pct = abs(sim_val - theo_val) / theo_val * 100
    print(f"{{metric}}: Sim={{sim_val:.4f}}, Theory={{theo_val:.4f}}, Error={{error_pct:.2f}}%")
```
"""

    if include_visualization:
        prompt += """
### 5. Visualization
Include plots for:
- Queue length over time
- Waiting time distribution
- System utilization
"""

    prompt += """
### 6. Error Handling
- Raise `ValueError` for invalid parameters
- Check stability condition (ρ < 1)
- Handle edge cases (no customers, etc.)

### 7. Documentation
- Docstrings for all classes and methods
- Type hints throughout
- Comments explaining key logic

Make the code clean, well-structured, and ready to use!
"""

    return prompt


@mcp.prompt()
def explain_mm1_theory() -> str:
    """
    Explain M/M/1 queue theory

    Returns educational prompt explaining M/M/1 concepts,
    formulas, and applications.
    """
    return """Explain M/M/1 Queue Theory comprehensively:

## 1. Notation and Basics
- **M/M/1 Notation**:
  - First M: Markovian (Poisson) arrivals
  - Second M: Markovian (exponential) service times
  - 1: Single server

- **Key Parameters**:
  - λ (lambda): Arrival rate (customers per time unit)
  - μ (mu): Service rate (customers per time unit)
  - ρ (rho): Utilization = λ/μ

## 2. Assumptions
1. Arrivals follow Poisson process (exponential inter-arrival times)
2. Service times are exponentially distributed
3. Single server with FIFO queue
4. Infinite queue capacity
5. Infinite customer population
6. Independence of arrivals and services

## 3. Stability Condition
**Critical requirement**: ρ = λ/μ < 1

If ρ ≥ 1, the queue grows unbounded (system is unstable).

## 4. Performance Metrics (Steady-State)

### Server Utilization
ρ = λ/μ

### Average Number in Queue
L_q = ρ²/(1-ρ)

### Average Number in System
L = ρ/(1-ρ) = L_q + ρ

### Average Waiting Time in Queue
W_q = ρ/(μ(1-ρ)) = λ/(μ(μ-λ))

### Average Time in System
W = 1/(μ(1-ρ)) = 1/(μ-λ)

## 5. Little's Law
Fundamental relationship:
**L = λW**

Average number in system = Arrival rate × Average time in system

Also applies to queue only: L_q = λW_q

## 6. Practical Applications
- Call centers (single agent)
- Single-lane toll booths
- Single-machine service systems
- Network packet queues

## 7. Limitations
- Real systems may not have exponential distributions
- May need multiple servers (M/M/c)
- Finite capacity may be required (M/M/1/K)
- Service may vary by customer type

Provide specific parameter values to calculate metrics for a scenario.
"""


@mcp.prompt()
def analyze_results(
    simulation_metrics: Dict[str, float],
    theoretical_metrics: Dict[str, float],
    config: Dict[str, float]
) -> str:
    """
    Analyze simulation results prompt

    Creates prompt for analyzing simulation accuracy and
    suggesting improvements.

    Args:
        simulation_metrics: Simulation results
        theoretical_metrics: Theoretical values
        config: Simulation configuration

    Returns:
        Analysis prompt
    """
    sim_json = json.dumps(simulation_metrics, indent=2)
    theo_json = json.dumps(theoretical_metrics, indent=2)
    config_json = json.dumps(config, indent=2)

    return f"""Analyze these M/M/1 simulation results:

## Simulation Configuration
```json
{config_json}
```

## Simulation Results
```json
{sim_json}
```

## Theoretical Values
```json
{theo_json}
```

## Analysis Tasks

### 1. Accuracy Assessment
- Calculate relative error for each metric
- Determine if errors are within acceptable range (<10%)
- Identify which metrics have highest/lowest accuracy

### 2. Error Analysis
- Explain possible sources of error
- Assess if simulation time was sufficient
- Check if warm-up period was needed

### 3. Recommendations
- Suggest improvements to reduce error
- Recommend whether to increase simulation time
- Advise on number of replications needed

### 4. Statistical Significance
- Comment on confidence in results
- Suggest confidence interval calculations
- Recommend variance reduction techniques if needed

Provide a comprehensive analysis with specific numerical comparisons and actionable recommendations.
"""


@mcp.prompt()
def debug_simulation() -> str:
    """
    Debug simulation issues prompt

    Returns guidance for troubleshooting common M/M/1
    simulation problems.
    """
    return """Help debug M/M/1 simulation issues:

## Common Problems and Solutions

### 1. Simulation Never Finishes
**Symptoms**: Program hangs, no output
**Possible Causes**:
- Unstable system (λ ≥ μ, ρ ≥ 1)
- Infinite loop in code
- Missing yield statements in SimPy processes

**Debug Steps**:
```python
# Check stability
rho = arrival_rate / service_rate
assert rho < 1, f"Unstable: ρ={rho:.4f} >= 1"

# Add timeout
import signal
signal.alarm(60)  # 60 second timeout
```

### 2. Results Don't Match Theory
**Symptoms**: Large errors (>10%)
**Possible Causes**:
- Too short simulation time
- Not reaching steady state
- Incorrect implementation
- Wrong random distributions

**Debug Steps**:
- Increase simulation_time (try 10x longer)
- Add warm-up period (discard first 10-20%)
- Verify exponential distributions:
  ```python
  import random
  inter_arrival = random.expovariate(arrival_rate)  # Correct
  service_time = random.expovariate(service_rate)    # Correct
  ```
- Print intermediate values to verify logic

### 3. Queue Length Always Zero
**Symptoms**: avg_queue_length ≈ 0 always
**Possible Causes**:
- Very low utilization (ρ << 1)
- Measuring at wrong time
- Not tracking queue correctly

**Debug Steps**:
- Check utilization (should see queues if ρ > 0.5)
- Measure queue length at customer arrival:
  ```python
  self.queue_lengths.append(len(self.server.queue))
  ```
- Log queue lengths to see distribution

### 4. Too Many/Few Customers
**Symptoms**: Unexpected customer count
**Expected**: ~λ × simulation_time customers

**Debug Steps**:
```python
expected = arrival_rate * simulation_time
actual = len(customers_served)
ratio = actual / expected
print(f"Expected ~{expected:.0f}, got {actual} (ratio: {ratio:.3f})")
# Ratio should be close to 1.0
```

### 5. No Arrivals or Services
**Symptoms**: 0 customers served
**Possible Causes**:
- Arrival process not started
- Incorrect expovariate parameter
- simulation_time too short

**Debug Steps**:
```python
# Verify processes are started
env.process(arrival_process())  # Must call this!

# Check rates are positive
assert arrival_rate > 0
assert service_rate > 0

# Print diagnostics
print(f"λ={arrival_rate}, μ={service_rate}, T={simulation_time}")
```

## General Debugging Tips
1. Start with known-good example (λ=3, μ=5, T=10000)
2. Add print statements at key points
3. Verify random number generation
4. Check that SimPy environment is running
5. Compare with reference implementation

Provide your specific error message or unexpected behavior for targeted help.
"""


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point for MCP server"""
    import os

    # Support both STDIO (for local CLI) and HTTP (for Smithery deployment)
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()

    if transport == "http":
        # HTTP transport for containerized deployment (Smithery)
        # Requires uvicorn with CORS support
        import uvicorn
        from starlette.middleware.cors import CORSMiddleware

        # Create Starlette app with MCP endpoint
        app = mcp.http_app()

        # Add CORS middleware for Smithery
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins for Smithery
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=["mcp-session-id", "mcp-protocol-version"],
            max_age=86400,
        )

        # Smithery sets PORT to 8081 by default
        port = int(os.environ.get("PORT", "8000"))
        host = os.environ.get("HOST", "0.0.0.0")

        # Run with uvicorn
        uvicorn.run(app, host=host, port=port)
    else:
        # Default STDIO transport for local CLI usage
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
