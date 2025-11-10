"""
MCP Server for M/M/1 Queue Simulation

A Model Context Protocol server providing resources, tools, and prompts
for M/M/1 queuing system simulation and analysis.

Usage:
    uvx mcp-server-mm1
    # or
    uv run mcp-server-mm1
"""

__version__ = "0.1.0"
__author__ = "WSC 2025 Research Project"

from .server import main

__all__ = ["main"]
