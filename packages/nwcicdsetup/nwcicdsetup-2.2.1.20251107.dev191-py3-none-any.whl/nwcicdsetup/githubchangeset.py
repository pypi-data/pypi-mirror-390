import asyncio
import fnmatch
import logging
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class GitHubChangeset:
    def __init__(self, url: str, headers: Dict[str, Any], session: Optional[aiohttp.ClientSession] = None) -> None:
        self.url = url
        self.headers = headers
        self.session = session or aiohttp.ClientSession()  # Not ideal; session should be passed in
        self.filenames: List[str] = []

    async def fetch_async(self) -> None:
        """Queries the changeset and populates the list of changed files"""
        logger.info(f"Fetching change-set from: '{self.url}'")

        for attempt in range(1, 4):
            try:
                async with self.session.get(self.url, headers=self.headers) as response:
                    response.raise_for_status()
                    data = await response.json()

                    files = data.get("files", [])
                    self.filenames.extend(item["filename"] for item in files)
                    logger.info(f"Retrieved {len(self.filenames)} changed files from GitHub")
                    return
            except aiohttp.ServerConnectionError as e:
                logger.warning(f"[Attempt {attempt}] Server connection error: {e}")
            except aiohttp.ClientConnectionError as e:
                logger.warning(f"[Attempt {attempt}] Client connection error: {e}")
            except Exception as e:
                logger.error(f"[Attempt {attempt}] Unexpected error: {e}")

            await asyncio.sleep(5)

        raise Exception(f"❌ Could not load changeset from GitHub: '{self.url}'")

    def join(self, other: "GitHubChangeset") -> "GitHubChangeset":
        self.filenames.extend(other.filenames)
        return self

    def find_relevant_changes(self, dependencies: List[str]) -> List[str]:
        logger.debug("Filtering relevant changes against dependency patterns")
        dependencies = list(filter(None, dependencies))

        matches: List[str] = []
        for pattern in [x for x in dependencies if not x.startswith("!")]:
            matches.extend(fnmatch.filter(self.filenames, pattern))

        unmatch: List[str] = []
        for pattern in [x[1:] for x in dependencies if x.startswith("!")]:
            unmatch.extend(fnmatch.filter(matches, pattern))

        relevant_changes = sorted(set(matches) - set(unmatch))
        logger.debug(f"Found {len(relevant_changes)} relevant changes")
        return relevant_changes
