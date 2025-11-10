"""
MCP Server Prototype v0.1 for Simulation Systems

This server provides structured context about simulation systems to LLMs
following the Model Context Protocol specification.

Note: This is a simplified prototype. In production, use the official MCP SDK.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from .schemas import MM1_SCHEMA


@dataclass
class MCPResource:
    """Represents a resource that can be provided through MCP"""
    uri: str
    name: str
    description: str
    mime_type: str
    content: Any


@dataclass
class MCPTool:
    """Represents a tool that can be invoked through MCP"""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPPrompt:
    """Represents a prompt template available through MCP"""
    name: str
    description: str
    arguments: List[Dict[str, Any]]
    template: str


class SimulationMCPServer:
    """
    MCP Server for providing simulation system context to LLMs

    This prototype server implements core MCP concepts:
    - Resources: Structured schemas describing simulation systems
    - Tools: Operations that can be performed (e.g., validate config)
    - Prompts: Template prompts for common tasks
    """

    def __init__(self):
        """Initialize the MCP server with simulation schemas"""
        self.resources: Dict[str, MCPResource] = {}
        self.tools: Dict[str, MCPTool] = {}
        self.prompts: Dict[str, MCPPrompt] = {}

        # Register M/M/1 schema
        self._register_mm1_resources()
        self._register_mm1_tools()
        self._register_mm1_prompts()

    def _register_mm1_resources(self):
        """Register M/M/1 queue resources"""
        # Complete schema
        self.resources["mm1://schema"] = MCPResource(
            uri="mm1://schema",
            name="M/M/1 Queue Schema",
            description="Complete schema for M/M/1 queuing system",
            mime_type="application/json",
            content=MM1_SCHEMA
        )

        # Parameters only
        self.resources["mm1://parameters"] = MCPResource(
            uri="mm1://parameters",
            name="M/M/1 Parameters",
            description="Input parameters for M/M/1 simulation",
            mime_type="application/json",
            content=MM1_SCHEMA["parameters"]
        )

        # Performance metrics
        self.resources["mm1://metrics"] = MCPResource(
            uri="mm1://metrics",
            name="M/M/1 Performance Metrics",
            description="Performance metrics to calculate",
            mime_type="application/json",
            content=MM1_SCHEMA["performance_metrics"]
        )

        # Implementation guidelines
        self.resources["mm1://guidelines"] = MCPResource(
            uri="mm1://guidelines",
            name="M/M/1 Implementation Guidelines",
            description="Guidelines for implementing M/M/1 simulation",
            mime_type="application/json",
            content=MM1_SCHEMA["implementation_guidelines"]
        )

    def _register_mm1_tools(self):
        """Register tools for M/M/1 operations"""
        self.tools["validate_mm1_config"] = MCPTool(
            name="validate_mm1_config",
            description="Validate M/M/1 configuration parameters",
            input_schema={
                "type": "object",
                "properties": {
                    "arrival_rate": {"type": "number", "minimum": 0, "exclusiveMinimum": True},
                    "service_rate": {"type": "number", "minimum": 0, "exclusiveMinimum": True},
                    "simulation_time": {"type": "number", "minimum": 0, "exclusiveMinimum": True},
                    "random_seed": {"type": "integer", "optional": True}
                },
                "required": ["arrival_rate", "service_rate"]
            }
        )

        self.tools["calculate_theoretical_metrics"] = MCPTool(
            name="calculate_theoretical_metrics",
            description="Calculate theoretical M/M/1 performance metrics",
            input_schema={
                "type": "object",
                "properties": {
                    "arrival_rate": {"type": "number"},
                    "service_rate": {"type": "number"}
                },
                "required": ["arrival_rate", "service_rate"]
            }
        )

    def _register_mm1_prompts(self):
        """Register prompt templates for M/M/1 tasks"""
        self.prompts["generate_mm1_simulation"] = MCPPrompt(
            name="generate_mm1_simulation",
            description="Generate a complete M/M/1 queue simulation in Python using SimPy",
            arguments=[
                {"name": "arrival_rate", "description": "Customer arrival rate", "required": True},
                {"name": "service_rate", "description": "Service rate", "required": True},
                {"name": "simulation_time", "description": "Simulation duration", "required": False},
                {"name": "include_validation", "description": "Include theoretical validation", "required": False}
            ],
            template="""Create a SimPy simulation model for an M/M/1 queuing system with the following requirements:

System Configuration:
- Arrival rate (λ): {arrival_rate} customers per time unit
- Service rate (μ): {service_rate} customers per time unit
- Simulation time: {simulation_time} time units

Requirements:
1. Use the SimPy discrete event simulation framework
2. Implement exponential inter-arrival times (Poisson arrivals)
3. Implement exponential service times
4. Track the following performance metrics:
   - Server utilization (ρ)
   - Average queue length (L_q)
   - Average waiting time in queue (W_q)
   - Average time in system (W)
   - Total customers served

5. Include a configuration dataclass with validation:
   - Validate that arrival_rate > 0
   - Validate that service_rate > 0
   - Validate that arrival_rate < service_rate (stability condition)

6. Include theoretical formulas for comparison:
   - ρ = λ / μ
   - L_q = ρ² / (1 - ρ)
   - W_q = ρ / (μ * (1 - ρ))
   - W = 1 / (μ * (1 - ρ))

7. Print results comparing simulation vs theoretical values

The code should be well-documented, follow Python best practices, and be ready to run."""
        )

        self.prompts["modify_mm1_simulation"] = MCPPrompt(
            name="modify_mm1_simulation",
            description="Modify existing M/M/1 simulation code",
            arguments=[
                {"name": "modification", "description": "Description of modification needed", "required": True}
            ],
            template="""Modify the existing M/M/1 simulation code to implement the following change:

{modification}

Ensure that:
1. The modification maintains the core M/M/1 structure
2. All validation rules are still enforced
3. Performance metrics are still calculated correctly
4. The code remains well-documented
5. Backward compatibility is maintained where possible"""
        )

    def get_resource(self, uri: str) -> Optional[MCPResource]:
        """
        Get a resource by URI

        Args:
            uri: Resource URI

        Returns:
            MCPResource if found, None otherwise
        """
        return self.resources.get(uri)

    def list_resources(self) -> List[Dict[str, str]]:
        """
        List all available resources

        Returns:
            List of resource metadata
        """
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mime_type": resource.mime_type
            }
            for resource in self.resources.values()
        ]

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """
        Get a tool by name

        Args:
            name: Tool name

        Returns:
            MCPTool if found, None otherwise
        """
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools

        Returns:
            List of tool metadata
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema
            }
            for tool in self.tools.values()
        ]

    def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke a tool with given arguments

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if name == "validate_mm1_config":
            return self._validate_mm1_config(arguments)
        elif name == "calculate_theoretical_metrics":
            return self._calculate_theoretical_metrics(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    def _validate_mm1_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate M/M/1 configuration"""
        errors = []

        arrival_rate = config.get("arrival_rate")
        service_rate = config.get("service_rate")
        simulation_time = config.get("simulation_time", 1000.0)

        if arrival_rate is None:
            errors.append("arrival_rate is required")
        elif arrival_rate <= 0:
            errors.append("arrival_rate must be positive")

        if service_rate is None:
            errors.append("service_rate is required")
        elif service_rate <= 0:
            errors.append("service_rate must be positive")

        if arrival_rate and service_rate and arrival_rate >= service_rate:
            errors.append(f"System is unstable: arrival_rate ({arrival_rate}) >= service_rate ({service_rate}). Utilization ρ = {arrival_rate/service_rate:.4f} >= 1")

        if simulation_time <= 0:
            errors.append("simulation_time must be positive")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "utilization": arrival_rate / service_rate if (arrival_rate and service_rate) else None
        }

    def _calculate_theoretical_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate theoretical M/M/1 metrics"""
        arrival_rate = params["arrival_rate"]
        service_rate = params["service_rate"]

        if arrival_rate >= service_rate:
            return {
                "error": "System is unstable (ρ >= 1)",
                "utilization": arrival_rate / service_rate
            }

        rho = arrival_rate / service_rate

        return {
            "utilization": rho,
            "avg_queue_length": rho**2 / (1 - rho),
            "avg_num_in_system": rho / (1 - rho),
            "avg_waiting_time": rho / (service_rate * (1 - rho)),
            "avg_system_time": 1 / (service_rate * (1 - rho))
        }

    def get_prompt(self, name: str, **kwargs) -> Optional[str]:
        """
        Get a filled prompt template

        Args:
            name: Prompt name
            **kwargs: Template arguments

        Returns:
            Filled prompt string if found, None otherwise
        """
        prompt = self.prompts.get(name)
        if not prompt:
            return None

        # Fill in template with provided arguments
        try:
            return prompt.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required argument: {e}")

    def list_prompts(self) -> List[Dict[str, Any]]:
        """
        List all available prompts

        Returns:
            List of prompt metadata
        """
        return [
            {
                "name": prompt.name,
                "description": prompt.description,
                "arguments": prompt.arguments
            }
            for prompt in self.prompts.values()
        ]

    def export_schema_for_llm(self, resource_uri: str = "mm1://schema") -> str:
        """
        Export schema in LLM-friendly format

        Args:
            resource_uri: URI of resource to export

        Returns:
            Formatted string suitable for LLM context
        """
        resource = self.get_resource(resource_uri)
        if not resource:
            raise ValueError(f"Resource not found: {resource_uri}")

        return json.dumps(resource.content, indent=2)


def main():
    """Example usage of MCP Server"""
    # Initialize server
    server = SimulationMCPServer()

    print("=" * 70)
    print("Simulation MCP Server v0.1")
    print("=" * 70)

    # List resources
    print("\nAvailable Resources:")
    for resource in server.list_resources():
        print(f"  - {resource['uri']}: {resource['name']}")

    # List tools
    print("\nAvailable Tools:")
    for tool in server.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")

    # List prompts
    print("\nAvailable Prompts:")
    for prompt in server.list_prompts():
        print(f"  - {prompt['name']}: {prompt['description']}")

    # Example: Validate configuration
    print("\n" + "=" * 70)
    print("Example: Validate M/M/1 Configuration")
    print("=" * 70)

    config = {
        "arrival_rate": 5.0,
        "service_rate": 8.0,
        "simulation_time": 10000.0
    }

    result = server.invoke_tool("validate_mm1_config", config)
    print(f"\nConfiguration: {config}")
    print(f"Valid: {result['valid']}")
    print(f"Utilization: {result['utilization']:.4f}")

    # Example: Calculate theoretical metrics
    print("\n" + "=" * 70)
    print("Example: Calculate Theoretical Metrics")
    print("=" * 70)

    metrics = server.invoke_tool("calculate_theoretical_metrics", {
        "arrival_rate": 5.0,
        "service_rate": 8.0
    })

    print(f"\nTheoretical Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")

    # Example: Get prompt
    print("\n" + "=" * 70)
    print("Example: Generate Prompt for LLM")
    print("=" * 70)

    prompt = server.get_prompt(
        "generate_mm1_simulation",
        arrival_rate=5.0,
        service_rate=8.0,
        simulation_time=10000.0
    )

    print(f"\n{prompt}\n")

    print("=" * 70)


if __name__ == "__main__":
    main()
