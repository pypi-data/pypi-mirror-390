"""
M/M/1 Queue Simulation using SimPy

Implements discrete event simulation for M/M/1 queuing systems.
"""

import simpy
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any
import numpy as np


@dataclass
class MM1Config:
    """Configuration for M/M/1 simulation"""
    arrival_rate: float
    service_rate: float
    simulation_time: float = 10000.0
    random_seed: int = 42

    def validate(self) -> None:
        """Validate configuration parameters"""
        if self.arrival_rate <= 0:
            raise ValueError(f"arrival_rate must be positive (got {self.arrival_rate})")

        if self.service_rate <= 0:
            raise ValueError(f"service_rate must be positive (got {self.service_rate})")

        if self.arrival_rate >= self.service_rate:
            rho = self.arrival_rate / self.service_rate
            raise ValueError(
                f"System is unstable: arrival_rate ({self.arrival_rate}) >= "
                f"service_rate ({self.service_rate}). Utilization ρ = {rho:.4f} >= 1"
            )

        if self.simulation_time <= 0:
            raise ValueError(f"simulation_time must be positive (got {self.simulation_time})")


@dataclass
class SimulationMetrics:
    """Performance metrics from simulation"""
    utilization: float
    avg_queue_length: float
    avg_waiting_time: float
    avg_system_time: float
    customers_served: int
    avg_num_in_system: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            "utilization": self.utilization,
            "avg_queue_length": self.avg_queue_length,
            "avg_waiting_time": self.avg_waiting_time,
            "avg_system_time": self.avg_system_time,
            "customers_served": self.customers_served,
            "avg_num_in_system": self.avg_num_in_system
        }


class MM1QueueSimulation:
    """
    M/M/1 Queue Simulation

    Simulates a single-server queue with Poisson arrivals
    and exponential service times using SimPy.
    """

    def __init__(self, config: MM1Config):
        """
        Initialize simulation

        Args:
            config: MM1Config with simulation parameters
        """
        config.validate()
        self.config = config

        # Set random seed
        random.seed(config.random_seed)
        np.random.seed(config.random_seed)

        # Metrics storage
        self.waiting_times: List[float] = []
        self.system_times: List[float] = []
        self.queue_lengths: List[int] = []

        # SimPy environment
        self.env = simpy.Environment()
        self.server = simpy.Resource(self.env, capacity=1)

    def customer_process(self, customer_id: int):
        """
        Process a single customer

        Args:
            customer_id: Unique customer identifier
        """
        arrival_time = self.env.now

        # Record queue length on arrival
        self.queue_lengths.append(len(self.server.queue))

        # Request server
        with self.server.request() as request:
            yield request

            # Calculate waiting time
            wait_time = self.env.now - arrival_time
            self.waiting_times.append(wait_time)

            # Service time (exponential distribution)
            service_time = random.expovariate(self.config.service_rate)
            yield self.env.timeout(service_time)

            # Calculate system time
            system_time = self.env.now - arrival_time
            self.system_times.append(system_time)

    def arrival_process(self):
        """
        Generate customer arrivals

        Poisson process = exponential inter-arrival times
        """
        customer_id = 0
        while True:
            # Inter-arrival time (exponential distribution)
            inter_arrival = random.expovariate(self.config.arrival_rate)
            yield self.env.timeout(inter_arrival)

            # Create new customer
            customer_id += 1
            self.env.process(self.customer_process(customer_id))

    def run(self) -> SimulationMetrics:
        """
        Run simulation and calculate metrics

        Returns:
            SimulationMetrics with performance results
        """
        # Start arrival process
        self.env.process(self.arrival_process())

        # Run simulation
        self.env.run(until=self.config.simulation_time)

        # Calculate metrics
        if not self.waiting_times:
            raise RuntimeError("No customers served during simulation")

        avg_wait = np.mean(self.waiting_times)
        avg_system = np.mean(self.system_times)
        avg_queue = np.mean(self.queue_lengths)

        # Server utilization (approximate)
        rho = self.config.arrival_rate / self.config.service_rate

        # Average number in system
        avg_in_system = avg_queue + rho

        return SimulationMetrics(
            utilization=rho,
            avg_queue_length=avg_queue,
            avg_waiting_time=avg_wait,
            avg_system_time=avg_system,
            customers_served=len(self.waiting_times),
            avg_num_in_system=avg_in_system
        )


def run_mm1_simulation(
    arrival_rate: float,
    service_rate: float,
    simulation_time: float = 10000.0,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Run M/M/1 simulation (convenience function)

    Args:
        arrival_rate: λ
        service_rate: μ
        simulation_time: Duration
        random_seed: Random seed

    Returns:
        Dict with simulation metrics
    """
    config = MM1Config(
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        simulation_time=simulation_time,
        random_seed=random_seed
    )

    sim = MM1QueueSimulation(config)
    metrics = sim.run()

    return metrics.to_dict()
