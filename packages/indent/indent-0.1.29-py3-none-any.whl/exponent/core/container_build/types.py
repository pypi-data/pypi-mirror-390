"""Types for container build log streaming."""

from typing import Literal

import msgspec


class BuildLogOutput(msgspec.Struct, tag="container_build_log_output"):
    """A single log line from a container build."""

    container_image_uuid: str
    data: str
    timestamp: float
    level: Literal["info", "error", "warning"] = "info"
    phase: Literal["build", "verification"] = "build"
    command: str | None = None


class BuildLogStatus(msgspec.Struct, tag="container_build_log_status"):
    """Status update for a container build."""

    container_image_uuid: str
    status: Literal["started", "completed", "failed"]
    message: str | None = None


BuildLogMessage = BuildLogOutput | BuildLogStatus
