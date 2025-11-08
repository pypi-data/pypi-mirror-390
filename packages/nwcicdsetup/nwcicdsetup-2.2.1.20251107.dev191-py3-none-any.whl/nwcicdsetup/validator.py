import os
import re
import sys
import logging
from pathlib import Path
from typing import Any, Dict

import yaml

from nwcicdsetup.NWServiceContext import NWServiceContext
from nwcicdsetup.circlecicontext import CircleCIContext
from nwcicdsetup.nwservice import NWService, NWTask
from nwcicdsetup.validationschema import general_config_validate

logger = logging.getLogger(__name__)

async def validate(general_config_path: str, pipeline: int):
    cwd = Path(".")
    logger.info(f"Current working dir is: {cwd.resolve()}")
    configs = list(cwd.rglob("cicd.yml"))
    logger.info(f"Found {len(configs)} 'cicd.yml'")

    try:
        if not os.path.exists(general_config_path):
            raise Exception(
                f"No file found for general config at '{general_config_path}'"
            )

        with open(general_config_path, mode="rb") as base_config:
            general_config = general_config_validate(yaml.safe_load(base_config))

        def validate_attr_dependencies(cwd: Path, service: NWService, task: Any):
            for d in task.dependencies:
                path = Path(d.removesuffix("*")).relative_to(cwd)
                path_exists(service, task, str(path))

        def path_exists(service: NWService, task: NWTask, path: str):
            if not os.path.exists(path):
                raise Exception(
                    f"{service.path}/cicd.yml/{task.name}: Could not find '{path}'"
                )

        def validate_attr_requires(
            services: Dict[str, NWService], service: NWService, task: Any
        ):
            for id in task.requires:
                service_id, task_id = id.split(":")
                requires_all = bool(re.search("[\\*]+", task_id))

                # validate the service and the jobs to find
                if not service_id in services or (
                    not requires_all and not task_id in services[service_id].all_jobs
                ):
                    raise Exception(
                        f"{service.path}/cicd.yml: Nothing found for reference '{id}'"
                    )

        services: Dict[str, NWService] = {}
        context = NWServiceContext(
            CircleCIContext.create_dummy_env(pipeline),
            services,
            general_config,
            str(cwd.resolve()),
        )
        services |= {
            s.name: s
            for s in [
                NWService(context, str(configPath.relative_to(cwd)))
                for configPath in configs
            ]
        }

        for service in services.values():
            for task in service.tasks.values():
                validate_attr_requires(services, service, task)
                validate_attr_dependencies(cwd, service, task)
                path_exists(service, task, task.path)

    except Exception as e:
        logger.error("Validation failed", exc_info=True)
        sys.exit(str(e))

    logger.info("Validation successful")
