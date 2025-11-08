from dataclasses import dataclass
from typing import Any, Dict


@ dataclass
class CircleCIJob:
    number: int
    name: str
    started_at: str
    status: str
    web_url: str
    workflow_name: str
    pipeline_id: str
    trigger_type: str = ""
    vcs_revision: str = ""

    @ staticmethod
    def from_data(data: Dict[str, Any]) -> "CircleCIJob":
        return CircleCIJob(
            data["number"],
            data["name"],
            data["started_at"],
            data["status"],
            data["web_url"],
            data["latest_workflow"]["name"],
            data["pipeline"]["id"])
