from dataclasses import dataclass
from typing import Any, Dict


@ dataclass
class CircleCIWorkflowJob:
    id: str
    started_at: str
    stopped_at: str
    duration: int
    status: str
    credits_used: int

    @ staticmethod
    def from_data(data: Dict[str, Any]) -> "CircleCIWorkflowJob":
        return CircleCIWorkflowJob(
            data["id"],
            data["started_at"],
            data["stopped_at"],
            data["duration"],
            data["status"],
            data["credits_used"])
