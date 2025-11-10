"""
MCP Schema for M/M/1 Queue Simulation System

This schema defines the structured context that will be provided to LLMs
for generating M/M/1 queue simulation code.
"""

MM1_SCHEMA = {
    "schema_version": "1.0",
    "system_type": "M/M/1 Queue",
    "description": "Single-server queuing system with Poisson arrivals and exponential service times",

    "parameters": {
        "arrival_rate": {
            "symbol": "λ",
            "description": "Customer arrival rate (customers per unit time)",
            "type": "float",
            "constraints": {
                "min": 0.0,
                "exclusive_min": True
            },
            "example": 5.0
        },
        "service_rate": {
            "symbol": "μ",
            "description": "Service rate (customers per unit time)",
            "type": "float",
            "constraints": {
                "min": 0.0,
                "exclusive_min": True
            },
            "example": 8.0
        },
        "simulation_time": {
            "description": "Duration of simulation run (in time units)",
            "type": "float",
            "default": 1000.0,
            "constraints": {
                "min": 0.0,
                "exclusive_min": True
            }
        },
        "random_seed": {
            "description": "Random seed for reproducibility",
            "type": "integer",
            "optional": True,
            "example": 42
        }
    },

    "system_characteristics": {
        "queue_capacity": "infinite",
        "num_servers": 1,
        "service_discipline": "FIFO",
        "arrival_process": {
            "type": "Poisson",
            "distribution": "Exponential inter-arrival times"
        },
        "service_process": {
            "type": "Exponential",
            "distribution": "Exponential service times"
        }
    },

    "performance_metrics": {
        "required": [
            {
                "name": "server_utilization",
                "symbol": "ρ",
                "description": "Fraction of time server is busy",
                "formula": "λ / μ",
                "type": "float",
                "range": [0.0, 1.0]
            },
            {
                "name": "average_queue_length",
                "symbol": "L_q",
                "description": "Average number of customers in queue (not including service)",
                "formula": "ρ² / (1 - ρ)",
                "type": "float"
            },
            {
                "name": "average_waiting_time",
                "symbol": "W_q",
                "description": "Average time customer spends waiting in queue",
                "formula": "ρ / (μ * (1 - ρ))",
                "type": "float"
            },
            {
                "name": "average_system_time",
                "symbol": "W",
                "description": "Average total time customer spends in system",
                "formula": "1 / (μ * (1 - ρ))",
                "type": "float"
            }
        ],
        "optional": [
            {
                "name": "customers_served",
                "description": "Total number of customers served during simulation",
                "type": "integer"
            },
            {
                "name": "queue_length_over_time",
                "description": "Time series of queue length",
                "type": "list[tuple[float, int]]"
            }
        ]
    },

    "output_requirements": {
        "code_language": "Python",
        "framework": "SimPy",
        "version": ">=4.0",
        "include_visualization": False,
        "include_validation": True,
        "include_theoretical_comparison": True
    },

    "implementation_guidelines": {
        "required_imports": [
            "simpy",
            "numpy"
        ],
        "class_structure": {
            "config_class": {
                "name": "MM1Config",
                "type": "dataclass",
                "fields": ["arrival_rate", "service_rate", "simulation_time", "random_seed"]
            },
            "metrics_class": {
                "name": "PerformanceMetrics",
                "type": "dataclass",
                "fields": ["average_queue_length", "average_waiting_time", "average_system_time", "server_utilization"]
            },
            "simulation_class": {
                "name": "MM1Queue",
                "methods": [
                    {
                        "name": "__init__",
                        "parameters": ["config: MM1Config"]
                    },
                    {
                        "name": "customer_arrival",
                        "parameters": ["customer_id: int"],
                        "description": "Process for handling a single customer"
                    },
                    {
                        "name": "arrival_process",
                        "description": "Generate arrivals following Poisson process"
                    },
                    {
                        "name": "run",
                        "returns": "PerformanceMetrics",
                        "description": "Execute simulation and return results"
                    }
                ]
            }
        },
        "validation_rules": [
            "arrival_rate must be positive",
            "service_rate must be positive",
            "arrival_rate must be less than service_rate (stability condition: ρ < 1)",
            "simulation_time must be positive"
        ],
        "error_handling": [
            "Raise ValueError for invalid parameters",
            "Check stability condition before running simulation"
        ]
    },

    "theoretical_validation": {
        "stability_condition": {
            "formula": "ρ = λ / μ < 1",
            "description": "System must be stable (arrival rate < service rate)"
        },
        "little_law": {
            "formula": "L = λ * W",
            "description": "Average number in system equals arrival rate times average time in system"
        },
        "formulas": {
            "utilization": "λ / μ",
            "avg_queue_length": "ρ² / (1 - ρ)",
            "avg_num_in_system": "ρ / (1 - ρ)",
            "avg_waiting_time": "ρ / (μ * (1 - ρ))",
            "avg_system_time": "1 / (μ * (1 - ρ))"
        }
    },

    "example_use_cases": [
        {
            "scenario": "Low utilization system",
            "parameters": {
                "arrival_rate": 3.0,
                "service_rate": 8.0,
                "simulation_time": 5000.0
            },
            "expected_utilization": 0.375
        },
        {
            "scenario": "Medium utilization system",
            "parameters": {
                "arrival_rate": 5.0,
                "service_rate": 8.0,
                "simulation_time": 10000.0
            },
            "expected_utilization": 0.625
        },
        {
            "scenario": "High utilization system",
            "parameters": {
                "arrival_rate": 7.0,
                "service_rate": 8.0,
                "simulation_time": 20000.0
            },
            "expected_utilization": 0.875
        }
    ]
}
