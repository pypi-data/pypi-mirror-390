"""
ACP (Agent Client Protocol) client for Augment CLI.

This module provides a synchronous Python client for communicating with
the Augment CLI agent via the Agent Client Protocol.
"""

from augment.acp.client import ACPClient, AuggieACPClient, AgentEventListener
from augment.acp.claude_code_client import ClaudeCodeACPClient

__all__ = ["ACPClient", "AuggieACPClient", "ClaudeCodeACPClient", "AgentEventListener"]
