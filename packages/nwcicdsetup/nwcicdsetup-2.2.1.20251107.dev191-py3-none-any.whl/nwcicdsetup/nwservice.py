import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Coroutine, Dict, List, Optional, Set, Tuple, Union

import yaml
from schema import SchemaError

from nwcicdsetup.Context import Context
from nwcicdsetup.NWServiceContext import NWServiceContext
from nwcicdsetup.circleci import check_change_async, check_dotnet_change_async
from nwcicdsetup.validationschema import approval_task_name, service_validate, is_nw_runner_resource

logger = logging.getLogger(__name__)

class NWApproval:
    """Encapsulation resulting in an Circleci approval workflow step"""

    def __init__(self, service: "NWService", id: str, members: Dict[str, Any]):
        self.id = id
        self.service = service
        self.name = f"{service.name}-{id}-approve-job"
        self.requires: List[str] = list(members["requires"])
        """wait for completion on this approval job"""

    def to_yaml(self) -> Dict[str, Any]:
        return {
            self.name: {
                "type": "approval",
                "requires": self.service.job_names_for_requires_references(
                    self.requires
                ),
            }
        }


class NWService:
    """Encapsulation of the cicd.yml files which is processing task data"""

    def __init__(self, context: "NWServiceContext", config_path: str):
        self.approvals: Dict[str, NWApproval] = {}
        """all parsed approval jobs resulting in Circleci workflow approvals"""
        self.context: NWServiceContext = context
        """context information"""
        self.name: str = ""
        """name of the parsed cicd.yml - assigned from its 'name' atttribute"""
        self.layers: List[Set[str]] = []
        """tasks names per layer"""
        self.tasks: Dict[str, NWTask] = {}
        """parsed 'tasks' section of the cicd.yml mainly controlling the building part"""
        self.path = os.path.dirname(config_path).replace("\\\\", "/").replace("\\", "/")
        """path to the cicd.yml file relative from the root"""

        logger.debug(f"Parsing service config from: {config_path}")

        try:
            logger.info(f"process config '{config_path}'")

            with open(config_path, mode="rb") as config_stream:
                loaded_config = (
                    yaml.safe_load(json.dumps(json.loads(config_stream.read())))
                    if ".json" in config_path
                    else yaml.safe_load(config_stream)
                )
            nodes = service_validate(loaded_config, context)

            self.name = nodes["name"]
            # build up build layers containing task ids which can be used to resolve
            # tasks of self.tasks dictionary
            for layer in nodes["layers"]:
                logger.debug(f"Processing layer with tasks: {list(layer.keys())}")
                tasks: Set[str] = set()
                self.layers.append(tasks)
                for layer_tasks in layer.values():
                    for task_name, task in layer_tasks.items():
                        tasks.add(task_name)
                        if approval_task_name.match(task_name):
                            self.approvals |= {
                                task_name: NWApproval(
                                    service=self, id=task_name, members=task
                                )
                            }
                            logger.debug(f"Added approval task: {task_name}")
                        else:
                            self.tasks |= {
                                task_name: NWTask(
                                    name=task_name, service=self, members=task
                                )
                            }
                            logger.debug(f"Added build task: {task_name}")

            # setup requires depending on layers
            for task in [*self.tasks.values(), *self.approvals.values()]:
                task.requires += self.get_preceding_layers_references_for(task.id)
                task.requires = list(set(task.requires))
                task.requires.sort()
                
            logger.info(f"Resolved {len(self.tasks)} tasks and {len(self.approvals)} approvals for service '{self.name}'")

        except SchemaError as e:
            logger.exception(f"Schema validation failed for config: {config_path}")
            raise e

    @property
    def context_name(self) -> str:
        c = self.context.job_context
        context_prefix = os.environ.get("CIRCLE_CONTEXT_PREFIX")
        context_prefix = context_prefix if context_prefix else ""

        if c == Context.FEATURE:
            return f"{context_prefix}feature"
        if c == Context.DEV:
            return f"{context_prefix}dev"
        if c == Context.TEST:
            return f"{context_prefix}test"
        if c == Context.STAGE:
            return f"{context_prefix}stage"
        if c == Context.PRODUCTION:
            return f"{context_prefix}prod"

        raise Exception(f"Cant find context for {self.name}")

    @property
    def all_jobs(self) -> Dict[str, Union["NWTask", "NWApproval"]]:
        """returns a dictionary containing all jobs or this service"""
        return self.tasks | self.approvals

    def get_preceding_layers_references_for(self, id: str) -> List[str]:
        """returns all task ids of preceding layers for the given task or approval id"""
        depending: List[str] = []

        # collect tasks until we find the containing layer
        for layer_tasks in self.layers:
            if id in layer_tasks:
                break
            for task_id in layer_tasks:
                if task_id in self.tasks:
                    depending.append(f"{self.name}:{self.tasks[task_id].id}")
                else:
                    depending.append(f"{self.name}:{self.approvals[task_id].id}")

        return depending

    def job_names_for_requires_references(self, requires: List[str]) -> List[str]:
        """List of job names for all given requires references"""
        required: List[str] = []
        for id in requires:
            service_id, job_id = id.split(":")

            # link all jobs from the service?
            requires_all = bool(re.search("[\\*]+", job_id))
            # validate the service and the tasks to find
            if not service_id in self.context.services:
                raise Exception(f"Nothing found for {service_id} in '{id}'")
            required_service = self.context.services[service_id]

            all_jobs = required_service.all_jobs
            if not job_id in all_jobs and not requires_all:
                raise Exception(f"Nothing found for {job_id} in '{id}'")

            if requires_all:
                required += [j.name for j in all_jobs.values()]
            else:
                required.append(all_jobs[job_id].name)
        return required

    async def check_changes_for_required(
        self, requires: List[str]
    ) -> Tuple[bool, Dict[str, Any]]:
        """retrieves change status of tasks via dependency_ids"""

        services = self.context.services

        def tasks_for(reference: str) -> List[Coroutine[Any, Any, bool]]:
            service_id, job_id = reference.split(":")

            # link all jobs from the service?
            requires_all = bool(re.search("[\\*]+", job_id))

            # validate the service and the tasks to find
            if not service_id in services:
                raise Exception(f"No service found for {service_id} in '{reference}'")

            service = services[service_id]
            if not job_id in service.tasks and not requires_all:
                raise Exception(
                    f"No task-reference found for {job_id} in '{reference}'"
                )

            tasks = (
                [t.is_changed_async for t in service.tasks.values()]
                if requires_all
                else [service.tasks[job_id].is_changed_async]
            )
            return tasks

        async def to_result(
            t: Coroutine[Any, Any, bool], reference: str
        ) -> Tuple[bool, Dict[str, Any]]:
            return (await t, {"required task": reference})

        def is_approval(reference: str) -> bool:
            service_id, id = reference.split(":")
            if not service_id in services:
                raise Exception(f"No service found for {service_id} in '{reference}'")
            return id in services[service_id].approvals

        logger.debug(f"Checking changes for required references: {requires}")
        requires = list(filter(lambda x: not is_approval(x), requires))

        tasks = [
            to_result(t, reference)
            for reference in requires
            for t in tasks_for(reference)
        ]
        results = list(await asyncio.gather(*tasks))
        def true_result(x: Tuple[bool, Dict[str, Any]]) -> bool:
            return x[0]
        
        logger.info(f"Change check result: changed={any(filter(true_result, results))}, info={results}")

        # combine results if any
        if any(filter(true_result, results)):
            info: Dict[str, Any] = {}
            for result in results:
                info |= result[1]
            return (True, info)
        return (False, {})

    async def job_yaml_async(self) -> Dict[str, Any]:
        """returns all task in form of a yml compliant dictionary"""
        logger.info(f"Generate jobs for service '{self.name}'")

        tasks = [task.to_yaml_async() for task in self.tasks.values()]
        jobs: Dict[str, Any] = {}
        for a in await asyncio.gather(*tasks):
            jobs |= a

        logger.debug(f"Generated {len(jobs)} job(s) for workflow in service '{self.name}'")
        return jobs

    async def workflow_jobs_async(self) -> List[Dict[str, Any]]:
        # enable yml dumper caching via aliases
        if not "yml_branch_filter" in globals():
            g = globals() # dictionary of the current global symbol table
            g["yml_branch_filter"] = {
                "branches": {"only": [self.context.branch]},
                "tags": {"ignore": "/.^/"} # i am not sure, but to get tags working, we have to add a wildcard here
                # the tag logic identifies the correct branch of the tag commit, so the context should just fall in line
            }
        yml_branch_filter = (globals())["yml_branch_filter"]

        def workflow_job(
            dependency_ids: List[str], name: str, custom_dependencies: List[str] = []
        ) -> Dict[str, Any]:
            yml_obj = {"context": self.context_name, "filters": yml_branch_filter}
            required = self.job_names_for_requires_references(dependency_ids)
            if len(required) > 0:
                yml_obj["requires"] = required + custom_dependencies
            return {name: yml_obj}

        # workflow jobs for tasks:
        jobs: List[Dict[str, Any]] = []
        for task in self.tasks.values():
            jobs.append(workflow_job(task.requires, task.name))

        # workflow jobs for approvals:
        for approval in self.approvals.values():
            jobs.append(approval.to_yaml())

        return jobs


class NWTask:

    def __init__(self, name: str, service: "NWService", members: Dict[str, Any]):
        self._is_changed: Optional[bool] = None
        """private flag caching a previous call to is_changed_async()"""
        self._lock = asyncio.Lock()
        """the lock used for is_changed_async()"""
        self.change_info: Dict[str, Any] = {}
        """changeset information available after first call to is_changed_async()"""
        self.commands: List[Dict[str, Any]] = list(members["commands"])
        """command and parameters this task will be linked to"""
        self.dependencies: List[str] = list(members["dependencies"])
        """dependencies that will considered to determine changeset and trigger the job"""
        self.executor: str = members["executor"]
        """executor to be used for the generated job"""
        self.path: str = os.path.normpath(
            os.path.join(service.path, members["path"])
        ).replace("\\", "/")
        """path of this task relative from cicd.yml"""
        self.resource_class: str = members["resource_class"]
        """the resource class used for job generation"""

        self.working_directory: str = members["working_directory"]
        """working directory used for speed up builds"""

        self.requires: List[str] = list(members["requires"])
        """tasks we consider when determining a changeset; also used to wait for completion in circleci workflow jobs"""
        self.service: NWService = service
        """parent cicd.yml/nwservice that generated this task"""
        self.id: str = name
        """the unprocessed task name as ID"""
        self.not_changed_command: Optional[Dict[str, Dict[str, Any]]] = members[
            "not_changed_command"
        ]
        self.parameters: List[Dict[str, Any]] = list(members["parameters"])

        if isinstance(self.commands[0], str):
            raise Exception(
                f"Found a string only command named '{self.commands[0]}'! This should have been converted in the schema validation!!!"
            )

        first_command_name = next(iter(self.commands[0]))

        self.name = f"{self.service.name}-{name}-{first_command_name}-job"
        """name of the task including the service name"""

        config_commands = self.service.context.general_config["commands"]
        # set working dir default values
        for command in self.commands:
            for command_name, parameters in command.items():
                if (
                    "working_dir" not in parameters
                    or len(str(parameters["working_dir"])) == 0
                ):
                    parameters["working_dir"] = self.path
                else:
                    # prepend service path
                    parameters["working_dir"] = (
                        os.path.normpath(
                            os.path.join(self.path, str(parameters["working_dir"]))
                        )
                        .replace("\\", "/")
                        .replace("//", "/")
                    )

                # set unittest-dir if existent in the command defined in 'general-config.yml'
                if "unittest_dir" in config_commands[command_name]["parameters"]:
                    test_path = self.test_path
                    if (
                        "unittest_dir" not in parameters
                        or len(str(parameters["unittest_dir"])) < 0
                    ):
                        if len(test_path) > 0:  # prevent override
                            parameters["unittest_dir"] = test_path
                    else:
                        # prepend service path
                        parameters["unittest_dir"] = (
                            os.path.normpath(
                                os.path.join(self.path, str(parameters["unittest_dir"]))
                            )
                            .replace("\\", "/")
                            .replace("//", "/")
                        )

        # always add the tasks directory as dependency
        self.dependencies.append(self.path + "/*")

    @property
    def command_steps(self) -> List[Union[str, Dict[str, Any]]]:
        steps: List[Union[str, Dict[str, Any]]] = []

        # command dictionaries with parameters
        for command_entry in self.commands:
            for command, parameters in command_entry.items():
                step = self.command_to_step(command, parameters)
                steps.append(step)

        return steps

    def command_to_step(
        self, command: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        config_commands = self.service.context.general_config["commands"]
        config_params = config_commands[command]["parameters"]

        # extend with eventual parameters given by the cicd.yaml
        # that fit parameters found in the command definition in general-config.yaml
        for param_kvp in self.parameters:
            for param_name, param_value in param_kvp.items():
                if param_name in config_params:
                    parameters[param_name] = param_value
        return {command: {name: value for name, value in parameters.items()}}

    @property
    def is_feature_branch(self) -> bool:
        return self.service.context.job_context == Context.FEATURE

    @property
    def is_deployment(self) -> bool:
        return "deploy" in [
            name.lower() for command in self.commands for name in command.keys()
        ]

    @property
    async def should_execute_async(self) -> bool:
        """Returns true if dependencies changed"""
        logger.debug(f"Should execute '{self.name}'? Feature: {self.is_feature_branch}, Deploy: {self.is_deployment}, Force: {self.service.context.force}")
        return (
            not (
                self.is_deployment
                and (self.is_feature_branch or self.service.context.fake_deploy)
            )
            and await self.is_changed_async
        )

    async def check_task_changed_async(
        self, tasks: List["NWTask"]
    ) -> Tuple[bool, Dict[str, Any]]:
        """get information about task change; returns a Tuple(True, reasons of change)"""

        if self.service.context.force:
            return (True, {"Forced": "All apps changed"})

        async def to_result(
            routine: Coroutine[Any, Any, bool], name: str
        ) -> Tuple[bool, str]:
            return (await routine, name)

        app_changed_info: Dict[str, Any] = {}
        result = await asyncio.gather(
            *[to_result(t.is_changed_async, t.name) for t in tasks]
        )
        # filter results indicating a change only
        changed_result = list(filter(lambda x: x[0], result))

        is_changed = any(changed_result)
        if is_changed:
            app_changed_info |= {
                "Tasks changed": list(map(lambda x: x[1], changed_result))
            }

        return (is_changed, app_changed_info)

    @property
    async def is_changed_async(self) -> bool:
        if self.service.context.force:
            self.change_info = {"Forced": ""}
            return True

        # we need this critical section to wait for complete resolution of this if block
        # otherwise the first dependency check could set self._is_changed to a result,
        # which is not the final end result...
        async with self._lock:
            if self._is_changed is None:
                # handle dotnet related tasks:
                logger.debug(f"Checking dotnet changes for {self.name} in path {self.path}")
                dotnet_result = await check_dotnet_change_async(
                    self.service.context.circleci_context, self.path
                )
                self.change_info |= dotnet_result[1]
                self._is_changed = self._is_changed or dotnet_result[0]

                # handle dependencies given via configuration:
                logger.debug(f"Checking dependency changes for {self.name}")
                dependency_result = await check_change_async(
                    self.service.context.circleci_context,
                    self.name,
                    self.dependencies,
                    name="dependencies",
                )
                self.change_info |= dependency_result[1]
                self._is_changed = self._is_changed or dependency_result[0]

                # only check global dependencies if in layer 0
                logger.debug(f"Checking global changes for {self.name}")
                if len(self.service.get_preceding_layers_references_for(self.id)) == 0:
                    global_result = await check_change_async(
                        self.service.context.circleci_context,
                        self.name,
                        self.service.context.global_dependencies,
                        name="global",
                    )
                    self._is_changed = self._is_changed or global_result[0]
                    self.change_info |= global_result[1]

                # check depending internal and external tasks by the requires attribute:
                logger.debug(f"Checking required changes for {self.name}")
                required_dependencies_result = (
                    await self.service.check_changes_for_required(self.requires)
                )
                self.change_info |= required_dependencies_result[1]
                self._is_changed = self._is_changed or required_dependencies_result[0]

                if self._is_changed:
                    logger.info(
                        f"Detected relevant changes for {self.name}:\n{json.dumps(self.change_info, indent=2)}"
                    )
                else:
                    logger.warning(f"Detected no relevant changes for {self.name}")
            else:
                logger.debug(f"Change status for {self.name} already determined: {self._is_changed}")

        return self._is_changed

    @property
    def test_path(self) -> str:
        """Returns the path to a test project from self.path or self.service.path else ''"""

        def find_test_path_by_id(name: str, path: Path) -> str:
            name = re.sub("[\\.\\-_]", "", name)
            test_projects = list(
                map(lambda x: str(x), path.rglob(f"*.Test.csproj"))
            )  # case sensitive names
            service_result = list(
                filter(
                    lambda a_path: re.match(
                        f".*{name}\\.test.*", str(a_path), flags=re.IGNORECASE
                    ),
                    test_projects,
                )
            )
            csproj_path = (
                str(service_result.pop()).replace("\\", "/")
                if len(service_result)
                else ""
            )
            return os.path.dirname(csproj_path)

        result = find_test_path_by_id(self.id, Path(self.path))
        if not len(result) > 0:
            result = find_test_path_by_id(self.id, Path(self.service.path))
        # result = result if len(result) else self.path
        logger.info(
            f'Test path for {self.name}: {result if len(result) else f"Fallback to {self.path}"}'
        )
        return result

    async def to_yaml_async(self) -> Dict[str, Any]:
        def job(commands: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
            steps: List[Union[str, Dict[str, Any]]] = [
                {
                    "checkout": 
                    {
                        "method": self.service.context.checkout_method
                    }
                },
                {
                    "changeset_info": {
                        "file_name": "change-set.json",
                        "data": json.dumps(self.change_info),
                    }
                },
            ]
            steps += commands

            # this is supposed to be configurable.. let's do this in the .net version
            if self.working_directory == "/mnt/ramdisk":
                # step that allows ramdisk to be safe for git
                # to be executed before checkout step
                steps.insert(
                    0,
                    {
                        "run": {
                            "name": "Git Preconfiguration",
                            "command": "git config --global --add safe.directory /mnt/ramdisk",
                        }
                    },
                )

            yml_obj = {
                "executor": self.executor,
                "resource_class": self.resource_class,
                "working_directory": self.working_directory,  # optimization to speed up builds
                "steps": steps,
            }
            # self.add_docker_push(task, steps)
            return {self.name: yml_obj}

        if await self.should_execute_async:
            return job(self.command_steps)

        reason = "# No changes to code, infrastructure or dependencies detected"
        if self.is_feature_branch:
            reason = "# you are working on a feature branch"
        elif self.is_deployment and self.service.context.fake_deploy:
            reason = f"\necho -e '{FAKE_DEPLOY_MSG}'"

        empty_job = (
            [
                self.command_to_step(name, params)
                for name, params in self.not_changed_command.items()
            ]
            if self.not_changed_command
            else [
                self.command_to_step(
                    "empty_job", {"job_name": self.name, "reason": reason}
                )
            ]
        )

        yaml_obj = {
            "resource_class": self.resource_class,
            "steps": empty_job,
        }
        if is_nw_runner_resource(self.resource_class):
            yaml_obj["executor"] = self.executor
        else:
            yaml_obj["docker"] = [{"image": "cimg/base:current-20.04"}]
        return { self.name: yaml_obj }


FAKE_DEPLOY_MSG: str = """
~~~~           FAKE DEPLOY          ~~~~


░░░░░░░░░░░░░░▄▄▄▄▄▄▄▄▄▄▄▄░░░░░░░░░░░░░░
░░░░░░░░░░░░▄████████████████▄░░░░░░░░░░
░░░░░░░░░░▄██▀░░░░░░░▀▀████████▄░░░░░░░░
░░░░░░░░░▄█▀░░░░░░░░░░░░░▀▀██████▄░░░░░░
░░░░░░░░░███▄░░░░░░░░░░░░░░░▀██████░░░░░
░░░░░░░░▄░░▀▀█░░░░░░░░░░░░░░░░██████░░░░
░░░░░░░█▄██▀▄░░░░░▄███▄▄░░░░░░███████░░░
░░░░░░▄▀▀▀██▀░░░░░▄▄▄░░▀█░░░░█████████░░
░░░░░▄▀░░░░▄▀░▄░░█▄██▀▄░░░░░██████████░░
░░░░░█░░░░▀░░░█░░░▀▀▀▀▀░░░░░██████████▄░
░░░░░░░▄█▄░░░░░▄░░░░░░░░░░░░██████████▀░
░░░░░░█▀░░░░▀▀░░░░░░░░░░░░░███▀███████░░
░░░▄▄░▀░▄░░░░░░░░░░░░░░░░░░▀░░░██████░░░
██████░░█▄█▀░▄░░██░░░░░░░░░░░█▄█████▀░░░
██████░░░▀████▀░▀░░░░░░░░░░░▄▀█████████▄
██████░░░░░░░░░░░░░░░░░░░░▀▄████████████
██████░░▄░░░░░░░░░░░░░▄░░░██████████████
██████░░░░░░░░░░░░░▄█▀░░▄███████████████
███████▄▄░░░░░░░░░▀░░░▄▀▄███████████████

~~~~           FAKE DEPLOY          ~~~~
"""
