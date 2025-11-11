#!/usr/bin/env python3
"""
MCP Models - Data structures for MCP Monitor requests and responses
Aligned with Model Context Protocol specification
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Literal

# Type definitions
Decision = Literal["allow", "block", "need_more_info", "required_explicit_user_confirmation"]
Severity = Literal["low", "medium", "high", "critical"]
Transport = Literal["stdio", "http","streamable-http"]  # MCP spec transport types
CallType = Literal["read", "write", "none"]
ClientOS = Literal["windows", "unix", "macos", "linux"]
@dataclass
class ServerRef:
    """Reference to an MCP server - aligned with MCP specification"""
    name: str                      # Server name (not id) - MCP uses names
    transport: Transport           # stdio or http - from MCP spec
    version: Optional[str] = None  # Server version if available
    context: Optional[str] = None  # additional context, could be "ide", defaults to "mcp"

@dataclass
class ToolRef:
    """Reference to an MCP tool"""
    name: str                    # Tool name from MCP server
    description: Optional[str] = None # Tool description if available
    version: Optional[str] = None # Tool version if available
    full_history: Optional[List['ConfirmationHistoryEntry']] = None  # All tool calls including non-user-input calls

@dataclass
class AgentContext:
    """Agent-provided context for the tool call"""

    # Required fields
    last_user_prompt: str        # Most recent user message that led to this tool call
    context_summary: str         # Agent's summary of the conversation context
    user_prompt_id: str          # Unique ID for the current user prompt

    # Optional fields
    intent: Optional[str] = None                    # What the agent plans to accomplish
    plan: Optional[str] = None                      # Step-by-step execution plan
    expected_outputs: Optional[str] = None          # What the agent expects to receive

    # NOTE: No 'consent' field here - workspace boundaries come from env.workspace
    # We don't trust agent-provided consent as it could be manipulated

@dataclass
class EnvironmentContext:
    """Environment context provided by the Gateway (trusted)"""

    # Required fields
    session_id: str              # Unique session identifier for correlation (multiple tool calls in the same session)
    workspace: Dict[str, Any]    # Workspace boundaries and current file info

    # Optional fields
    app_id: Optional[str] = None                    # App ID (cursor, vscode, etc.)
    client: Optional[str] = None                    # IDE client (cursor, vscode, etc.)
    client_os: Optional[ClientOS] = None             # Client OS (windows, unix, macos, linux)
    client_version: Optional[str] = None            # Client version
    selection_hash: Optional[str] = None            # Hash of current selection/context

@dataclass
class InitRequest:
    """Request structure for MCP server initialization"""

    # Required fields
    environment: EnvironmentContext      # Environment context (session, workspace, client info)
    server: ServerRef                   # MCP server reference
    tools: List[ToolRef]               # Array of tools with name and description

@dataclass
class PolicyRequest:
    """Complete request structure for policy evaluation"""

    # Required fields
    event_id: str                # Unique identifier for this evaluation (client should provide this value upon request and reuse in response)
    timestamp: str               # ISO 8601 timestamp
    direction: Literal["request", "response"]  # Request or response evaluation
    server: ServerRef            # MCP server reference
    tool: ToolRef                # MCP function/tool reference
    arguments_redacted: Dict[str, Any]  # Tool arguments with secrets redacted
    context: Dict[str, Any]      # Combined agent + environment context


@dataclass
class PolicyResponse:
    """Response structure for policy evaluation"""

    # Required fields
    event_id: str                # Links to corresponding request
    timestamp: str               # ISO 8601 timestamp
    direction: Literal["response"]  # Always "response" for responses
    server: ServerRef            # MCP server reference
    tool: ToolRef                # MCP function/tool reference
    result_preview: Dict[str, Any]  # Preview of response content
    context: Dict[str, Any]      # Same context as request

@dataclass
class InspectDecision:
    """Policy decision result"""
    decision: Decision
    severity: Optional[Severity] = None
    reasons: Optional[List[str]] = None
    need_fields: Optional[List[str]] = None        # Specific missing context fields
    ui_hints: Optional[Dict[str, Any]] = None
    matched_rules: Optional[List[str]] = None      # For audit/debug
    llm_analysis: Optional[Dict[str, Any]] = None  # LLM analysis details
    call_type: Optional[CallType] = None          # "read" | "write" | "none" when classified
    thinking_trace: Optional[List[str]] = None     # Optional model reasoning trace


class UserDecision(Enum):
    """User decision for confirmation dialogs"""
    ALLOW = "allow"
    BLOCK = "block"
    ALWAYS_ALLOW = "always_allow"
    ALWAYS_BLOCK = "always_block"


@dataclass
class UserConfirmation:
    """User confirmation data for policy decisions"""
    event_id: str
    direction: Literal["request", "response"]
    user_decision: UserDecision
    call_type: Optional[CallType] = None

PersistDecision = Literal["allow", "block", "ignore", "none"]

@dataclass
class ConfirmationHistoryEntry:
    """Relevant confirmation entry for history lookups"""
    id: int
    event_id: str  # Links to the specific event/transaction
    confirmed_at: str
    server_name: str
    tool_name: str
    user_decision: Literal["allow", "block", "always_allow", "always_block"]
    persist_decision: Optional[PersistDecision]
    call_type: Optional[CallType]
    arguments_redacted: Optional[Dict[str, Any]] = None
    source: Optional[Literal["user_confirmation", "policy"]] = None  # Indicates if user input was required or policy allowed
    direction: Optional[Literal["request", "response"]] = None  # Indicates if this was a request or response transaction

# Factory functions for creating properly structured requests

def create_policy_request(
    event_id: str,
    server: ServerRef,
    tool: ToolRef,
    arguments: Dict[str, Any],
    agent_context: AgentContext,
    env_context: EnvironmentContext,
) -> PolicyRequest:
    """Create a properly structured policy request"""

    return PolicyRequest(
        event_id=event_id,
        timestamp=datetime.now().isoformat() + "Z",
        direction="request",
        server=server,
        tool=tool,
        arguments_redacted=arguments,
        context={
            "agent": {
                "last_user_prompt": agent_context.last_user_prompt,
                "context_summary": agent_context.context_summary,
                "user_prompt_id": agent_context.user_prompt_id,
                "intent": agent_context.intent,
                "plan": agent_context.plan,
                "expected_outputs": agent_context.expected_outputs
            },
            "env": {
                "session_id": env_context.session_id,
                "workspace": env_context.workspace,
                "client": env_context.client,
                "client_version": env_context.client_version,
                "selection_hash": env_context.selection_hash,
                "client_os": env_context.client_os,
                "app_id": env_context.app_id
            }
        }
    )

def create_policy_response(
    event_id: str,
    server: ServerRef,
    tool: ToolRef,
    response_content: str,
    agent_context: AgentContext,
    env_context: EnvironmentContext
) -> PolicyResponse:
    """Create a properly structured policy response"""

    return PolicyResponse(
        event_id=event_id,
        timestamp=datetime.now().isoformat() + "Z",
        direction="response",
        server=server,
        tool=tool,
        result_preview={
            "text_head": response_content,
            "bytes_hash": None,  # Would be hash for binary content
            "meta": {
                "size": len(response_content),
                "content_type": "text"
            }
        },
        context={
            "agent": {
                "last_user_prompt": agent_context.last_user_prompt,
                "context_summary": agent_context.context_summary,
                "user_prompt_id": agent_context.user_prompt_id,
                "intent": agent_context.intent,
                "plan": agent_context.plan,
                "expected_outputs": agent_context.expected_outputs
            },
            "env": {
                "session_id": env_context.session_id,
                "workspace": env_context.workspace,
                "client": env_context.client,
                "client_version": env_context.client_version,
                "selection_hash": env_context.selection_hash,
                "client_os": env_context.client_os,
                "app_id": env_context.app_id
            }
        }
    )

# Example usage
if __name__ == "__main__":
    # Example of creating a proper policy request
    agent_ctx = AgentContext(
        last_user_prompt="Show me the files in the current directory",
        context_summary="User is exploring the project structure to understand the codebase",
        intent="List directory contents for code navigation",
        expected_outputs="List of files and directories"
    )

    env_ctx = EnvironmentContext(
        session_id="session-123",
        workspace={
            "roots": ["file:///home/user/project"],
            "current_file": "/home/user/project/main.py"
        },
        client="cursor",
        client_version="0.42.0"
    )

    request = create_policy_request(
        event_id="demo-001",
        server=ServerRef(name="filesystem-tools", transport="stdio"),
        tool=ToolRef(name="fs.read"),
        arguments={"path": "/home/user/project/README.md"},
        agent_context=agent_ctx,
        env_context=env_ctx
    )

    print("✅ Properly structured policy request created")
    print(f"   Server: {request.server.name} ({request.server.transport})")
    print(f"   Context: {request.context['agent']['last_user_prompt']}")
