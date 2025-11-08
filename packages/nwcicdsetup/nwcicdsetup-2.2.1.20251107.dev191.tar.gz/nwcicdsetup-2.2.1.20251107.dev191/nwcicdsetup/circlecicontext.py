import os
from dataclasses import dataclass, field
from nwcicdsetup.githubapiclient import GitHubAPIClient
import logging

logger = logging.getLogger(__name__)

@dataclass
class CircleCIContext:
    branch: str
    pipeline_number: int
    project_reponame: str
    project_username: str
    working_directory: str
    circle_token: str
    github_token: str
    vcs_type: str = "gh"
    current_vcs_revision: str = field(default="", init=False)
    last_successful_vcs_revision: str = field(default="", init=False)

    @staticmethod
    async def create_dummy_env(pipeline: int) -> "CircleCIContext":
        if len(os.environ["CIRCLE_PROJECT_USERNAME"]) < 0:
            raise Exception("project username is null")

        circle_token = os.environ.get("CIRCLE_TOKEN", "")
        github_token = os.environ.get("GITHUB_TOKEN", "")
        return CircleCIContext(
            branch="develop",
            pipeline_number=pipeline,
            project_reponame="nw-platform",
            project_username="nativewaves",
            working_directory=".",
            circle_token=circle_token,
            github_token=github_token
        )

    @classmethod
    async def create_from_environ_async(
        cls,
        pipeline: int,
        github_client: GitHubAPIClient
    ) -> "CircleCIContext":
        if len(os.environ["CIRCLE_PROJECT_USERNAME"]) < 0:
            raise Exception("project username is null")

        branch = os.environ.get("CIRCLE_BRANCH", "").strip()
        tag = os.environ.get("CIRCLE_TAG", "").strip()
        sha = os.environ.get("CIRCLE_SHA1", "").strip()
        project_username = os.environ["CIRCLE_PROJECT_USERNAME"]
        project_reponame = os.environ.get("CIRCLE_PROJECT_REPONAME", "")
        working_directory = os.environ["CIRCLE_WORKING_DIRECTORY"]
        circle_token = os.environ["CIRCLE_TOKEN"]
        github_token = os.environ["GITHUB_TOKEN"]

        if tag and sha:
            logger.info(f"Push for a tag detected: {tag}, commit: {sha}")
            branch = await github_client.resolve_branch_from_tag_commit_async(
                repoUsername=project_username,
                repository=project_reponame,
                sha=sha
            )
            
        logger.info(
            f"Created CircleCIContext from environment: branch={branch}, pipeline={pipeline}, repo={project_username}/{project_reponame}, sha={sha}"
        )

        return cls(
            branch=branch,
            pipeline_number=pipeline,
            project_reponame=project_reponame,
            project_username=project_username,
            working_directory=working_directory,
            circle_token=circle_token,
            github_token=github_token
        )

