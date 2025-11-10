"""
M/M/1 Queue Simulation Model using SimPy

This module implements a basic M/M/1 queuing system with:
- Exponential inter-arrival times (Poisson arrivals)
- Exponential service times
- Single server
- Infinite queue capacity
- FIFO discipline
"""

import simpy
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class MM1Config:
    """Configuration for M/M/1 queue simulation"""
    arrival_rate: float  # λ (customers per unit time)
    service_rate: float  # μ (customers per unit time)
    simulation_time: float = 1000.0
    random_seed: Optional[int] = None

    def __post_init__(self):
        """Validate configuration"""
        if self.arrival_rate <= 0:
            raise ValueError("Arrival rate must be positive")
        if self.service_rate <= 0:
            raise ValueError("Service rate must be positive")
        if self.arrival_rate >= self.service_rate:
            raise ValueError("System is unstable (ρ = λ/μ >= 1)")


@dataclass
class PerformanceMetrics:
    """Performance metrics collected from simulation"""
    average_queue_length: float = 0.0
    average_waiting_time: float = 0.0
    average_system_time: float = 0.0
    server_utilization: float = 0.0
    customers_served: int = 0

    # Time series data
    queue_length_over_time: List[tuple] = field(default_factory=list)
    waiting_times: List[float] = field(default_factory=list)
    system_times: List[float] = field(default_factory=list)

    def calculate_averages(self):
        """Calculate average metrics from collected data"""
        if self.waiting_times:
            self.average_waiting_time = np.mean(self.waiting_times)
        if self.system_times:
            self.average_system_time = np.mean(self.system_times)

    def get_theoretical_values(self, arrival_rate: float, service_rate: float) -> Dict[str, float]:
        """Calculate theoretical M/M/1 performance metrics"""
        rho = arrival_rate / service_rate  # Server utilization

        return {
            'utilization': rho,
            'avg_queue_length': rho**2 / (1 - rho),
            'avg_num_in_system': rho / (1 - rho),
            'avg_waiting_time': rho / (service_rate * (1 - rho)),
            'avg_system_time': 1 / (service_rate * (1 - rho))
        }


class MM1Queue:
    """M/M/1 Queue Simulation Model"""

    def __init__(self, config: MM1Config):
        """
        Initialize M/M/1 queue simulation

        Args:
            config: MM1Config object with simulation parameters
        """
        self.config = config
        self.env = simpy.Environment()
        self.server = simpy.Resource(self.env, capacity=1)
        self.metrics = PerformanceMetrics()

        # Set random seed for reproducibility
        if config.random_seed is not None:
            np.random.seed(config.random_seed)

        # Statistics tracking
        self.queue_length = 0
        self.total_busy_time = 0.0
        self.last_event_time = 0.0

    def customer_arrival(self, customer_id: int):
        """
        Process for a single customer

        Args:
            customer_id: Unique identifier for the customer
        """
        arrival_time = self.env.now

        # Request server
        with self.server.request() as request:
            # Track queue entry (customer joins queue)
            self.queue_length += 1
            self.metrics.queue_length_over_time.append((self.env.now, self.queue_length))

            # Wait for server
            yield request

            # Customer starts service (leaves queue, enters service)
            wait_time = self.env.now - arrival_time
            self.metrics.waiting_times.append(wait_time)

            # Decrement queue length BEFORE service starts
            self.queue_length -= 1
            self.metrics.queue_length_over_time.append((self.env.now, self.queue_length))

            # Service time (exponential distribution)
            service_time = np.random.exponential(1.0 / self.config.service_rate)

            # Track busy time
            service_start = self.env.now
            yield self.env.timeout(service_time)
            self.total_busy_time += service_time

            # Customer departs
            system_time = self.env.now - arrival_time
            self.metrics.system_times.append(system_time)
            self.metrics.customers_served += 1

    def arrival_process(self):
        """
        Generate customer arrivals following Poisson process
        """
        customer_id = 0
        while True:
            # Inter-arrival time (exponential distribution)
            inter_arrival_time = np.random.exponential(1.0 / self.config.arrival_rate)
            yield self.env.timeout(inter_arrival_time)

            # Start customer process
            self.env.process(self.customer_arrival(customer_id))
            customer_id += 1

    def run(self) -> PerformanceMetrics:
        """
        Run the simulation

        Returns:
            PerformanceMetrics object with collected statistics
        """
        # Start arrival process
        self.env.process(self.arrival_process())

        # Run simulation
        self.env.run(until=self.config.simulation_time)

        # Calculate final metrics
        self.metrics.server_utilization = self.total_busy_time / self.config.simulation_time
        self.metrics.calculate_averages()

        # Calculate average queue length from time series
        if self.metrics.queue_length_over_time:
            total_area = 0.0
            for i in range(len(self.metrics.queue_length_over_time) - 1):
                time_i, length_i = self.metrics.queue_length_over_time[i]
                time_next, _ = self.metrics.queue_length_over_time[i + 1]
                total_area += length_i * (time_next - time_i)
            self.metrics.average_queue_length = total_area / self.config.simulation_time

        return self.metrics

    def print_results(self, include_theoretical: bool = True):
        """
        Print simulation results

        Args:
            include_theoretical: Whether to include theoretical values for comparison
        """
        print("\n" + "="*60)
        print("M/M/1 Queue Simulation Results")
        print("="*60)
        print(f"\nConfiguration:")
        print(f"  Arrival rate (λ):  {self.config.arrival_rate:.2f} customers/time unit")
        print(f"  Service rate (μ):  {self.config.service_rate:.2f} customers/time unit")
        print(f"  Utilization (ρ):   {self.config.arrival_rate/self.config.service_rate:.4f}")
        print(f"  Simulation time:   {self.config.simulation_time:.2f} time units")

        print(f"\nSimulation Results:")
        print(f"  Customers served:        {self.metrics.customers_served}")
        print(f"  Server utilization:      {self.metrics.server_utilization:.4f}")
        print(f"  Avg queue length:        {self.metrics.average_queue_length:.4f}")
        print(f"  Avg waiting time:        {self.metrics.average_waiting_time:.4f}")
        print(f"  Avg system time:         {self.metrics.average_system_time:.4f}")

        if include_theoretical:
            theoretical = self.metrics.get_theoretical_values(
                self.config.arrival_rate,
                self.config.service_rate
            )
            print(f"\nTheoretical Values:")
            print(f"  Server utilization:      {theoretical['utilization']:.4f}")
            print(f"  Avg queue length:        {theoretical['avg_queue_length']:.4f}")
            print(f"  Avg waiting time:        {theoretical['avg_waiting_time']:.4f}")
            print(f"  Avg system time:         {theoretical['avg_system_time']:.4f}")

            print(f"\nAccuracy (Simulation vs Theoretical):")
            util_error = abs(self.metrics.server_utilization - theoretical['utilization']) / theoretical['utilization'] * 100
            queue_error = abs(self.metrics.average_queue_length - theoretical['avg_queue_length']) / theoretical['avg_queue_length'] * 100
            wait_error = abs(self.metrics.average_waiting_time - theoretical['avg_waiting_time']) / theoretical['avg_waiting_time'] * 100
            system_error = abs(self.metrics.average_system_time - theoretical['avg_system_time']) / theoretical['avg_system_time'] * 100

            print(f"  Utilization error:       {util_error:.2f}%")
            print(f"  Queue length error:      {queue_error:.2f}%")
            print(f"  Waiting time error:      {wait_error:.2f}%")
            print(f"  System time error:       {system_error:.2f}%")

        print("="*60 + "\n")


def main():
    """Example usage of MM1Queue"""
    # Configure simulation
    config = MM1Config(
        arrival_rate=5.0,    # 5 customers per time unit
        service_rate=8.0,    # 8 customers per time unit
        simulation_time=10000.0,
        random_seed=42
    )

    # Create and run simulation
    print("Running M/M/1 Queue Simulation...")
    queue = MM1Queue(config)
    metrics = queue.run()

    # Print results
    queue.print_results(include_theoretical=True)

    return queue, metrics


if __name__ == "__main__":
    main()
