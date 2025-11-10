"""Middleware for the CopilotAgent."""

from copilotagent.middleware.filesystem import FilesystemMiddleware
from copilotagent.middleware.initial_message import InitialMessageMiddleware
from copilotagent.middleware.planning import PlanningMiddleware
from copilotagent.middleware.server_middleware import ServerMiddleware
from copilotagent.middleware.station_middleware import StationMiddleware
from copilotagent.middleware.subagents import CompiledSubAgent, SubAgent, SubAgentMiddleware

__all__ = [
    "CompiledSubAgent",
    "FilesystemMiddleware",
    "InitialMessageMiddleware",
    "PlanningMiddleware",
    "ServerMiddleware",
    "StationMiddleware",
    "SubAgent",
    "SubAgentMiddleware",
]
