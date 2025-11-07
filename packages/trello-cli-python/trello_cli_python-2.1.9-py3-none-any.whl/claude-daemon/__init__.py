"""
Claude Daemon - AI-Powered Project Intelligence Microservice
Análisis de contexto, detección de fraude, y orquestación de flujos.
"""

__version__ = "1.0.0"
__author__ = "Claude Code"
__description__ = "AI coach that validates projects and detects fraud in Trello workflows"

from .client import ClaudeDaemonClient, get_daemon_client, is_daemon_available

__all__ = [
    "ClaudeDaemonClient",
    "get_daemon_client",
    "is_daemon_available",
]
