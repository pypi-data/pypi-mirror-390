import asyncio
import json
import os
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List

import yaml

from nwcicdsetup import circleci
from nwcicdsetup.NWServiceContext import NWServiceContext
from nwcicdsetup.nwservice import NWService
from nwcicdsetup.validationschema import general_config_validate, is_nw_runner_resource, checkout_method_validate

logger = logging.getLogger(__name__)


def str_presenter(dumper: Any, data: Any):
    if "\n" in data:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


async def generate(
    outfile: str,
    general_config_path: str,
    global_dependencies: List[str],
    pipeline: int,
    fake_deploy: bool,
    force: bool,
    resource_class: str,
    dummy_env: bool,
    checkout_method: str = "full",
) -> None:
    logger.info(f"<<< Pipeline: {pipeline} >>>")
    logger.info(f"Global dependencies: {json.dumps(global_dependencies, indent=4)}")
    if force:
        logger.info("<<< Forcing job execution >>>")
    if fake_deploy:
        logger.info("<<< Using fake deploy >>>")
    if dummy_env:
        logger.info("<<< Using dummy environment >>>")

    logger.info(f"<<< Use default resource-class: {resource_class} >>>")
    logger.info(f"Writing config to '{outfile}'")
    logger.info(f"Loading general config from '{general_config_path}'")

    try:
        checkout_method_validate(checkout_method)
    except ValueError as e:
        logger.error(f"Invalid checkout method '{checkout_method}': {e}. Falling back to 'full'.")
        checkout_method = "full"

    logger.info(f"Using checkout method: {checkout_method}")
    try:
        yaml.add_representer(str, str_presenter)
        yaml.representer.SafeRepresenter.add_representer(str, str_presenter)  # type: ignore

        circleci_context = await circleci.init_async(pipeline, dummy_env, force)
        cwd = Path(".")
        configs = (
            list(cwd.rglob("cicd.yml"))
            + list(cwd.rglob("cicd.yaml"))
            + list(cwd.rglob("cicd.json"))
            + list(cwd.rglob("*.cicd.yml"))
            + list(cwd.rglob("*.cicd.yaml"))
            + list(cwd.rglob("*.cicd.json"))
        )
        logger.info(f"Found {len(configs)} 'cicd' configs in {cwd.resolve()}")

        if not os.path.exists(general_config_path):
            raise FileNotFoundError(f"No file found for general config at '{general_config_path}'")

        logger.info(f"Processing general config '{general_config_path}'")
        with open(general_config_path, mode="rb") as general_config_stream:
            general_config = general_config_validate(yaml.safe_load(general_config_stream))

        services: Dict[str, NWService] = {}
        context = NWServiceContext(
            circleci_context,
            services,
            general_config,
            str(cwd.resolve()),
            global_dependencies,
            fake_deploy,
            force,
            resource_class,
            checkout_method=checkout_method,
        )
        services |= {
            s.name: s
            for s in [
                NWService(context, str(configPath.relative_to(cwd)))
                for configPath in configs
            ]
        }
        # preserve entries from loaded base config
        workflow_name = "{}-build-deploy".format(
            NWServiceContext.branch_to_context(circleci_context.branch).name.lower()
        )
        workflow_jobs: List[Dict[str, Any]] = []
        jobs: Dict[str, Any] = {}

        if "workflows" not in general_config:
            general_config["workflows"] = {workflow_name: {"jobs": workflow_jobs}}
        if workflow_name not in general_config["workflows"]:
            general_config["workflows"][workflow_name] = {"jobs": workflow_jobs}

        general_config["workflows"]["version"] = 2.1  # type: ignore

        if "jobs" not in general_config:
            general_config["jobs"] = jobs

        logger.info("Generating job sections...")
        yml_tasks = [asyncio.create_task(s.job_yaml_async()) for s in services.values()]
        for t_jobs in await asyncio.gather(*yml_tasks):
            jobs |= t_jobs

        if services:
            logger.info(f"Using context '{list(services.values())[0].context_name}' for all generated jobs.")

        logger.info("Generating workflow sections...")
        yml_tasks = [s.workflow_jobs_async() for s in services.values()]
        for w_jobs in await asyncio.gather(*yml_tasks):
            workflow_jobs += w_jobs

        # output
        yaml_str: str = yaml.safe_dump(general_config, width=1000)  # type: ignore

        if is_nw_runner_resource(resource_class):
            logger.info(
                f"Replacing 'setup_remote_docker' with 'setup_selfhosted_remote_docker' for resource '{resource_class}'"
            )
            yaml_str = yaml_str.replace("setup_remote_docker", "setup_selfhosted_remote_docker")

        with open(os.path.join(cwd.resolve(), f"{outfile}"), mode="w") as config_file:
            config_file.write(yaml_str)
            logger.info(f"Wrote configuration to {outfile}")

    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        sys.exit(1)
