import os
import logging
from typing import Any, Dict, List, Tuple

import aiohttp

from nwcicdsetup.circleciapiclient import CircleCIAPIClient
from nwcicdsetup.circlecicontext import CircleCIContext
from nwcicdsetup.dotnetdependencyresolver import fetch_dependencies
from nwcicdsetup.githubapiclient import GitHubAPIClient

logger = logging.getLogger(__name__)

async def init_async(pipeline: int, dummy_env: bool, forced: bool) -> CircleCIContext:
    async with aiohttp.ClientSession() as session:
        if dummy_env:
            context = await CircleCIContext.create_dummy_env(pipeline)
            logger.info("Created dummy circleci context")
        else:
            github_client = GitHubAPIClient(session, os.environ["GITHUB_TOKEN"])
            context: CircleCIContext = await CircleCIContext.create_from_environ_async(
                pipeline=pipeline,
                github_client=github_client
            )

        if forced:
            return context

        circleci_client = CircleCIAPIClient(session, context)
        current_vcs_revision = await circleci_client.load_current_vcs_async(context.pipeline_number)
        last_successful_vcs = await circleci_client.load_previous_successful_vcs_async()

        context.current_vcs_revision = current_vcs_revision
        context.last_successful_vcs_revision = last_successful_vcs

        logger.info(f"Current vcs '{current_vcs_revision}'")
        logger.info(f"Last successful vcs '{last_successful_vcs}'")

        return context


async def check_dotnet_change_async(circleci_context: CircleCIContext, project_dir: str) -> Tuple[bool, Dict[str, Any]]:
    if not circleci_context.last_successful_vcs_revision:
        logger.warning(f"No previous successful build found - Assume {project_dir} changed!!!")
        return (True, {"Check change": "No previous successful build found"})

    try:
        dotnet_dependencies = fetch_dependencies(
            root_dir=circleci_context.working_directory,
            project_dir=project_dir)
    except Exception as e:
        logger.error(f"Failed to fetch .NET dependencies: {e}")
        return (False, {})

    dotnet_dependencies = list(set(dotnet_dependencies))  # cut duplicates
    if len(dotnet_dependencies) <= 0:
        return (False, {})

    dotnet_dependencies.sort()

    async with aiohttp.ClientSession() as session:
        github_client = GitHubAPIClient(session, circleci_context.github_token)

        changeset = await github_client.get_changeset(
            circleci_context.current_vcs_revision,
            circleci_context.last_successful_vcs_revision,
            circleci_context.project_reponame,
            circleci_context.project_username)

        relevant_changes: List[str] = changeset.find_relevant_changes(dotnet_dependencies)

        await session.close()

        if len(relevant_changes):
            return (True, {"dotnet dependencies": relevant_changes})
        return (False, {})


async def check_change_async(circleci_context: CircleCIContext, project_name: str, dependencies: List[str], name: str) -> Tuple[bool, Dict[str, Any]]:
    if not circleci_context.last_successful_vcs_revision:
        logger.warning(f"No previous successful build found - Assume {project_name} changed!!!")
        return (True, {"Check change": "No previous successful build found"})

    if len(dependencies) <= 0:
        return (False, {})

    dependencies.sort()

    async with aiohttp.ClientSession() as session:
        github_client = GitHubAPIClient(session, circleci_context.github_token)

        changeset = await github_client.get_changeset(
            circleci_context.current_vcs_revision,
            circleci_context.last_successful_vcs_revision,
            circleci_context.project_reponame,
            circleci_context.project_username)

        relevant_changes: List[str] = changeset.find_relevant_changes(dependencies)

        await session.close()

        if len(relevant_changes):
            return (True, {name: relevant_changes})

        return (False, {})
