"""
mcpower_shared - Shared types and utilities for MCPower projects
"""

from mcpower_shared.mcp_types import (
    # Type definitions
    Decision,
    Severity,
    Transport,
    CallType,
    ClientOS,
    PersistDecision,
    
    # Data classes
    ServerRef,
    ToolRef,
    AgentContext,
    EnvironmentContext,
    InitRequest,
    PolicyRequest,
    PolicyResponse,
    InspectDecision,
    UserDecision,
    UserConfirmation,
    ConfirmationHistoryEntry,
    
    # Factory functions
    create_policy_request,
    create_policy_response,
)

__version__ = "0.1.0"

__all__ = [
    # Type definitions
    "Decision",
    "Severity",
    "Transport",
    "CallType",
    "ClientOS",
    "PersistDecision",
    
    # Data classes
    "ServerRef",
    "ToolRef",
    "AgentContext",
    "EnvironmentContext",
    "InitRequest",
    "PolicyRequest",
    "PolicyResponse",
    "InspectDecision",
    "UserDecision",
    "UserConfirmation",
    "ConfirmationHistoryEntry",
    
    # Factory functions
    "create_policy_request",
    "create_policy_response",
]

