# MCP Server for M/M/1 Queue Simulation

A [Model Context Protocol](https://modelcontextprotocol.io/) server that provides comprehensive resources, tools, and prompts for M/M/1 queuing system simulation and analysis.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

## What is M/M/1?

M/M/1 is a fundamental queuing model in operations research:
- **First M**: Markovian (Poisson) arrivals
- **Second M**: Markovian (exponential) service times
- **1**: Single server

This MCP server enables LLMs like Claude to:
- Access structured M/M/1 theory and formulas
- Validate simulation parameters
- Calculate theoretical performance metrics
- Generate and execute SimPy simulations
- Compare simulation results with theory

## Features

### 📚 Resources (7)
- `mm1://schema` - Complete M/M/1 system schema
- `mm1://parameters` - Parameter definitions with constraints
- `mm1://metrics` - Performance metrics catalog
- `mm1://formulas` - Theoretical formulas
- `mm1://guidelines` - Implementation best practices
- `mm1://examples` - Pre-configured scenarios
- `mm1://literature` - References and citations

### 🔧 Tools (5)
- `validate_config` - Validate M/M/1 parameters and check stability
- `calculate_metrics` - Compute theoretical performance metrics
- `run_simulation` - Execute SimPy discrete event simulation
- `compare_results` - Analyze simulation accuracy
- `recommend_parameters` - Suggest optimal configuration

### 💬 Prompts (4)
- `generate_simulation_code` - Create production-ready SimPy code
- `explain_mm1_theory` - Educational content on M/M/1 theory
- `analyze_results` - Interpret simulation outcomes
- `debug_simulation` - Troubleshoot common issues

## Installation

### Option 1: Using `uvx` (Recommended)

```bash
uvx mcp-server-mm1
```

### Option 2: Using `pip`

```bash
pip install mcp-server-mm1
mcp-server-mm1
```

### Option 3: From Source

```bash
git clone https://github.com/yourusername/mcp-server-mm1.git
cd mcp-server-mm1
uv pip install -e .
mcp-server-mm1
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration

```json
{
  "mcpServers": {
    "mm1-simulation": {
      "command": "uvx",
      "args": ["mcp-server-mm1"]
    }
  }
}
```

Restart Claude Desktop and the server will be available!

## Example Usage in Claude

### 1. Get M/M/1 Schema
```
User: Show me the M/M/1 queue schema

Claude uses: mm1://schema resource
```

### 2. Validate Configuration
```
User: Is λ=5, μ=8 a valid M/M/1 configuration?

Claude uses: validate_config tool
Result: ✓ Valid, ρ=0.625
```

### 3. Calculate Theoretical Metrics
```
User: Calculate theoretical metrics for λ=5, μ=8

Claude uses: calculate_metrics tool
Result:
- Utilization: 0.625
- Avg queue length: 1.0417
- Avg waiting time: 0.2083
- Avg system time: 0.3333
```

### 4. Run Simulation
```
User: Run a simulation with λ=5, μ=8 for 10,000 time units

Claude uses: run_simulation tool
Result: Simulation metrics + theoretical comparison + accuracy analysis
```

### 5. Generate Code
```
User: Generate SimPy code for λ=3, μ=10

Claude uses: generate_simulation_code prompt
Result: Complete, production-ready Python code
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/mcp-server-mm1.git
cd mcp-server-mm1

# Install dependencies
uv pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Local Testing

Use the MCP Inspector to test the server locally:

```bash
# Install MCP inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Run server with inspector
mcp dev src/mcp_server_mm1/server.py
```

This opens a web interface where you can:
- Browse available resources
- Test tool invocations
- Try prompt templates
- Inspect JSON-RPC communication

## Architecture

```
src/mcp_server_mm1/
├── server.py          # FastMCP server with resources/tools/prompts
├── schemas/
│   └── mm1_schema.py  # M/M/1 system schema definition
├── simulations/
│   └── mm1_queue.py   # SimPy simulation implementation
└── utils/
    └── metrics.py     # Theoretical calculations
```

## M/M/1 Theory Quick Reference

### Key Formulas

Given arrival rate λ and service rate μ:

- **Utilization**: ρ = λ/μ
- **Avg Queue Length**: L_q = ρ²/(1-ρ)
- **Avg Time in Queue**: W_q = ρ/(μ(1-ρ))
- **Avg Time in System**: W = 1/(μ(1-ρ))

### Stability Condition
System must satisfy **ρ < 1** (λ < μ)

If ρ ≥ 1, the queue grows unbounded!

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Related Work

This MCP server was developed as part of research on LLM-assisted simulation code generation for the Winter Simulation Conference (WSC) 2025.

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [SimPy Documentation](https://simpy.readthedocs.io/)
- [M/M/1 Queue - Wikipedia](https://en.wikipedia.org/wiki/M/M/1_queue)

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/mcp-server-mm1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mcp-server-mm1/discussions)

---

**Made with ❤️ for the simulation and LLM communities**
