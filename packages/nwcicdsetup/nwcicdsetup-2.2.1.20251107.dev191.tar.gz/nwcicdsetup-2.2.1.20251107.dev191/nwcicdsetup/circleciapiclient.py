import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote

import aiohttp

from nwcicdsetup.circlecicontext import CircleCIContext

logger = logging.getLogger(__name__)


class CircleCIAPIClient:
    def __init__(
        self, session: aiohttp.ClientSession, context: CircleCIContext
    ) -> None:
        self._base_url_v2 = "https://circleci.com/api/v2"
        self._base_url_v1_1 = "https://circleci.com/api/v1.1"
        self._session = session
        self._context = context
        self._validate_context()

    def _validate_context(self) -> None:
        required_attrs = [
            "circle_token",
            "vcs_type",
            "project_username",
            "project_reponame",
            "branch",
            "pipeline_number",
        ]
        missing = [attr for attr in required_attrs if not hasattr(self._context, attr)]
        if missing:
            raise ValueError(
                f"Missing required context attributes: {', '.join(missing)}"
            )

    @property
    def headers(self) -> Dict[str, Any]:
        return {"Circle-Token": self._context.circle_token}

    @property
    def project_slug(self) -> str:
        return f"{quote(self._context.vcs_type)}/{quote(self._context.project_username)}/{quote(self._context.project_reponame)}"

    async def _get(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Reusable GET request with error handling."""
        headers = headers or self.headers
        try:
            async with self._session.get(url, headers=headers, timeout=10) as response:
                raw_text = await response.text()
                try:
                    # Attempt to parse the response as JSON, even if Content-Type is incorrect
                    return json.loads(raw_text)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON from response. Raw response: {raw_text}")
                    return {}
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error {e.status} while accessing {url}: {e.message}")
        except aiohttp.ClientConnectionError as e:
            logger.error(f"Connection error while accessing {url}: {str(e)}")
        except aiohttp.ClientError as e:
            logger.error(f"Unexpected client error: {str(e)}")
        except asyncio.TimeoutError:
            logger.error(f"Request to {url} timed out.")
        return {}

    async def load_current_vcs_async(self, pipeline: int) -> str:
        pipeline_url = (
            f"{self._base_url_v2}/project/{self.project_slug}/pipeline/{pipeline}"
        )
        logger.info(f"Requesting pipeline data from: {pipeline_url}")

        for attempt in range(5):
            data = await self._get(pipeline_url, headers=self.headers)
            if data:
                try:
                    vcs = data["vcs"]
                    revision = vcs["revision"]
                    logger.info(f"Found current VCS revision: {revision}")
                    logger.debug(f"VCS details: {json.dumps(vcs, indent=3)}")
                    return revision
                except KeyError as e:
                    logger.error(f"KeyError while processing pipeline data: {e}")
                    logger.debug(f"Full pipeline data: {json.dumps(data, indent=3)}")
            else:
                logger.warning(
                    f"Attempt {attempt + 1}/5 failed. Retrying in 5 seconds..."
                )
                await asyncio.sleep(5)
        return "Not Found"

    async def load_previous_successful_vcs_async(self) -> str:
        logger.info("Searching for previous successful build...")

        async def search() -> Optional[Dict[str, Any]]:
            page_token: Optional[str] = ""
            max_attempts = 3
            attempt = 0

            while page_token is not None:
                page_suffix = f"?page-token={page_token}&" if page_token else "?"
                url = f"{self._base_url_v2}/project/{self.project_slug}/pipeline{page_suffix}branch={quote(self._context.branch)}"
                logger.info(f"Requesting pipelines: {url}")

                data = await self._get(url, headers=self.headers)
                if not data or not data.get("items"):
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.warning(
                            f"No results after {max_attempts} attempts for {url}"
                        )
                        break
                    logger.warning(
                        f"Empty response. Retrying {attempt}/{max_attempts}..."
                    )
                    await asyncio.sleep(0.5)
                    continue

                page_token = data.get("next_page_token")

                def filter_func(pipeline: Dict[str, Any]) -> bool:
                    try:
                        return (
                            pipeline["number"] < self._context.pipeline_number
                            and len(pipeline["errors"]) == 0
                            and pipeline["state"] == "created"
                            and pipeline["vcs"]["branch"] == self._context.branch
                        )
                    except KeyError as e:
                        logger.warning(f"Skip pipeline {pipeline.get('number')}. Missing key in pipeline data: {e}")
                        return False
                    except TypeError as e:
                        logger.warning(f"Skip pipeline {pipeline.get('number')}. Type error in pipeline data: {e}")
                        return False
                    except Exception as e:
                        logger.warning(f"Skip pipeline {pipeline.get('number')}. Unexpected error in pipeline filtering: {e}")
                        return False

                filtered_pipelines: List[Dict[str, Any]] = list(filter(filter_func, data["items"]))
                logger.info(
                    f"Found {len(filtered_pipelines)} pipelines matching criteria"
                )

                # pipelines ordered by their number. highest pipeline number first
                for pipeline in filtered_pipelines:
                    try:
                        workflow_url = (
                            f"{self._base_url_v2}/pipeline/{pipeline['id']}/workflow"
                        )
                        workflow_data = await self._get(workflow_url, headers=self.headers)
                        if not workflow_data:
                            continue

                        workflow_names = {item["name"] for item in workflow_data["items"]}
                        success_per_workflow = [
                            any(
                                item["status"] == "success"
                                for item in workflow_data["items"]
                                if item["name"] == name
                            )
                            for name in workflow_names
                        ]

                        if all(success_per_workflow):
                            logger.info(
                                f"Found successful pipeline: {json.dumps(pipeline, indent=3)}"
                            )
                            return pipeline
                    except KeyError as e:
                        logger.error(f"Missing key in pipeline or workflow data: {e}")
                        logger.debug(f"Pipeline data: {json.dumps(pipeline, indent=3)}")
                    except TypeError as e:
                        logger.error(
                            f"Type error when processing pipeline or workflow data: {e}"
                        )
                        logger.debug(f"Pipeline data: {json.dumps(pipeline, indent=3)}")
                    except Exception as e:
                        logger.error(
                            f"Unexpected error during workflow processing: {e}"
                        )
                        logger.debug(f"Pipeline data: {json.dumps(pipeline, indent=3)}")
            return None

        result = await search()
        return result["vcs"]["revision"] if result else ""
