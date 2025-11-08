from dataclasses import dataclass
from typing import Any, Dict, Optional


@ dataclass
class CircleCIBuild:
    url: str
    num: int
    workflow_name: str
    job_name: str
    retry_of: Optional[int]
    vcs_revision: str

    @ staticmethod
    def from_data(data: Dict[str, Any]) -> "CircleCIBuild":
        return CircleCIBuild(
            data["build_url"],
            data["build_num"],
            data.get("workflows", {}).get("workflow_name", "default"),
            data.get("workflows", {}).get("job_name", "default"),
            data.get("retry_of"),
            data["vcs_revision"])
