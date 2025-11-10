"""
MCP (Model Context Protocol) Integration Module

Enhanced MCP server integration for AWS API access with enterprise-grade
error handling, Rich CLI formatting, and ≥99.5% accuracy validation.

Key Components:
- MCPIntegrationManager: Main integration orchestrator
- CrossValidationEngine: Data accuracy validation
- MCPAWSClient: AWS API access via MCP
- Enhanced decimal conversion with error handling
"""

from .integration import (
    MCPIntegrationManager,
    CrossValidationEngine,
    MCPAWSClient,
    MCPValidationError,
    MCPServerEndpoints,
    create_mcp_manager_for_single_account,
    create_mcp_manager_for_multi_account,
    create_mcp_server_for_claude_code,
    _safe_decimal_conversion,
)

__all__ = [
    "MCPIntegrationManager",
    "CrossValidationEngine",
    "MCPAWSClient",
    "MCPValidationError",
    "MCPServerEndpoints",
    "create_mcp_manager_for_single_account",
    "create_mcp_manager_for_multi_account",
    "create_mcp_server_for_claude_code",
    "_safe_decimal_conversion",
]
