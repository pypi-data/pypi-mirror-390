import asyncio
import logging
import json
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import aiohttp
from nwcicdsetup.githubchangeset import GitHubChangeset

logger = logging.getLogger(__name__)


class GitHubAPIClient:

    def __init__(self, session: aiohttp.ClientSession, auth_token: str) -> None:
        self._base_url = "https://api.github.com"
        self._auth_token = auth_token
        self._session = session

    @property
    def headers(self) -> Dict[str, Any]:
        return {
            "Authorization": f"token {self._auth_token}"
        }

    async def check_dependencies_async(self, username: str, repository: str, branch: str, dependencies: List[str]) -> bool:
        logger.info(f"Checking {len(dependencies)} dependencies for branch '{branch}'")
        tasks = [self.check_dependency_async(username, repository, branch, d) for d in dependencies]
        return all(await asyncio.gather(*tasks))

    async def check_dependency_async(self, username: str, repository: str, branch: str, dependency: str) -> bool:
        """Use GitHub to verify that a dependency is valid"""
        if dependency.endswith("/*"):
            dependency = dependency[:-2]

        url = f"{self._base_url}/repos/{quote(username)}/{quote(repository)}/contents/{quote(dependency)}?ref={quote(branch)}"

        for attempt in range(1, 6):
            try:
                async with self._session.get(url, headers=self.headers) as response:
                    response.raise_for_status()
                    logger.debug(f"Dependency check passed for: {dependency} on branch {branch}")
                    return True
            except aiohttp.ClientResponseError as e:
                logger.warning(f"[Attempt {attempt}/5] GitHub responded {e.status} for dependency '{dependency}' on branch '{branch}': {e.message}")
                await asyncio.sleep(5)
            except (aiohttp.ServerConnectionError, aiohttp.ClientConnectionError) as e:
                logger.warning(f"[Attempt {attempt}/5] Connection error for '{dependency}': {str(e)}")
                await asyncio.sleep(5)

        logger.error(f"❌ Dependency invalid or unreachable: '{dependency}'")
        return False

    async def get_changeset(
        self,
        commit_id: str,
        previous_commit_id: str,
        repository: str,
        username: str
    ) -> GitHubChangeset:
        """Use GitHub to get all changes between two commit ids"""
        cache: Dict[Any, Any]
        lock: asyncio.Lock

        _globals = globals()
        cache = _globals.setdefault("__changeset_cache", {})
        lock = cache.setdefault("__changeset_lock", asyncio.Lock())

        async with lock:
            cache_key = (commit_id, previous_commit_id, repository, username)
            if cache_key in cache:
                logger.debug(f"Using cached changeset for {cache_key}")
                return cache[cache_key]

            logger.info(f"Fetching changeset for {commit_id} ↔ {previous_commit_id}")

            changeset1 = GitHubChangeset(
                f"{self._base_url}/repos/{quote(username)}/{quote(repository)}/compare/{quote(previous_commit_id)}...{quote(commit_id)}",
                self.headers,
                self._session,
            )
            changeset2 = GitHubChangeset(
                f"{self._base_url}/repos/{quote(username)}/{quote(repository)}/compare/{quote(commit_id)}...{quote(previous_commit_id)}",
                self.headers,
                self._session,
            )

            await asyncio.gather(*[changeset1.fetch_async(), changeset2.fetch_async()])
            result = changeset1.join(changeset2)
            cache[cache_key] = result
            logger.info(f"Found changeset between '{previous_commit_id}' and '{commit_id}': {json.dumps(result.filenames, indent=4)}")
            return result

    async def resolve_branch_from_tag_commit_async(
        self,
        repoUsername: str,
        repository: str,
        sha: str,
        preferred_branches: Optional[List[str]] = None
    ) -> str:
        """
        Resolves the source branch for a tag by checking where the commit is HEAD.
        Returns 'develop' as a fallback.
        """
        preferred_branches = preferred_branches or ["master", "main", "develop", "testing", "staging"]

        url = f"{self._base_url}/repos/{quote(repoUsername)}/{quote(repository)}/commits/{quote(sha)}/branches-where-head"
        logger.info(f"Resolving source branch for commit {sha} using: {url}")
        try:
            async with self._session.get(url, headers=self.headers, timeout=10) as response:
                raw_text = await response.text()
                try:
                    parsed: Any = json.loads(raw_text)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode GitHub JSON from: {raw_text}")
                    return "develop"

                branches: List[str] = []
                for item in parsed:
                    if not isinstance(item, dict):
                        continue
                    name = item.get("name")
                    if isinstance(name, str):
                        branches.append(name)

                for candidate in preferred_branches:
                    if candidate in branches:
                        logger.info(f"Resolved branch '{candidate}' for commit {sha}")
                        return candidate

                logger.warning(f"No known branch found for commit {sha}, defaulting to 'develop'")

        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error {e.status} while accessing {url}: {e.message}")
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Connection error while accessing {url}: {str(e)}")
        except aiohttp.ClientError as e:
            logger.error(f"Unexpected client error: {str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"GitHub request to {url} timed out.")

        return "develop"
