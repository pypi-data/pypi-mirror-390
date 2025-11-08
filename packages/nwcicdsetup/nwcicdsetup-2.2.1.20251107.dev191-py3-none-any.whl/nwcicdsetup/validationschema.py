import re
from typing import Any, Dict, List, Set
from schema import And, Optional, Or, Schema, SchemaError, Use
from nwcicdsetup.NWServiceContext import NWServiceContext

approval_task_name: Any = re.compile("([A-Za-z0-9\\@]+(_|\\-))+approval$")

nw_runner_resource_name: Any = re.compile("nativewaves/.*$")


def is_nw_runner_resource(name: str) -> bool:
    return nw_runner_resource_name.match(name)


def service_validate(data: Dict[str, Any], context: NWServiceContext) -> Dict[str, Any]:
    general_config: Dict[str, Dict[str, Any]] = context.general_config
    commands: Dict[str, Any] = general_config["commands"]

    captured_task: Dict[str, Dict[str, Any]]
    """Task that is currently processed"""

    def capture_task(o: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        nonlocal captured_task
        captured_task = o
        return o

    if not "default" in general_config["executors"]:
        raise Exception(
            "Must provide a 'default' executors in the general configs 'executers' section"
        )

    def is_valid_command(validate_command: Dict[str, Any]) -> bool:

        # check valid referenced commands and parameters
        parameters: Dict[str, Any]
        for name, parameters in validate_command.items():
            if not name in commands:
                raise SchemaError(f"Command '{name}' not found in general config")
            for parameter_name in parameters.keys():
                if not parameter_name in commands[name]["parameters"]:
                    raise SchemaError(
                        f"Parameter '{parameter_name}' not found in command '{name}'"
                    )

            # check that all expected command values have been set if no default is specified
            config_parameters: Dict[str, Any] = commands[name]["parameters"]
            for param_name in config_parameters:
                # check parameter set or default is specified
                if (
                    not param_name in validate_command[name]
                    and "default" not in config_parameters[param_name]
                ):
                    # check parameter specified in the tasks 'parameters' object
                    if "parameters" not in captured_task or any(
                        [param_name not in x for x in captured_task["parameters"]]
                    ):
                        raise SchemaError(
                            f"Command '{name}' expects parameter value for '{param_name}'"
                        )

        return True

    def is_unique_task_id(layers: List[Dict[str, Any]]) -> bool:
        """check all layers for unique task ids"""

        layer_items: Set[str] = set()
        for layer in layers:
            for layer_name, tasks in layer.items():
                for task_name in tasks:
                    if task_name in layer_items:
                        raise SchemaError(
                            f"Found duplicate task-id '{task_name}' in layer '{layer_name}'"
                        )
                    layer_items.add(task_name)
        return True

    requires_id: Any = re.compile("[A-Za-z0-9_\\-\\@]+:([A-Za-z0-9_\\-\\@]+|\\*)$")

    def is_requires_id(value: str) -> bool:
        if requires_id.match(value):
            return True
        raise SchemaError(f"Id {value} doesn't required format {requires_id}")

    def convert_string_command(command_name: str) -> Dict[str, Any]:
        return {command_name: {"working_dir": "", "no_output_timeout": "10m"}}

    def is_approval_step(name: str) -> bool:
        return approval_task_name.match(name)

    def is_an_executor(executor: str) -> bool:
        return executor in general_config["executors"]

    command_schema = {
        # commandname:value pairs:
        str: {  # command name
            # all commands have a default no-output-timer
            Optional("no_output_timeout"): str,
            # the directory the job is run on; relative to service directory
            Optional("working_dir", default=""): str,
            # miscellaneous parameters
            str: Or(str, float, bool, int, list),
        }
    }

    serviceSchema = Schema(
        {
            "name": str,  # Unique name of the service containing all the apps; relevant for references
            "layers": And(
                [  # layers definding an order of job execution
                    {
                        str: Or(  # layer name
                            # Approval task converted to a circleci workflow approval job
                            {
                                Optional(And(str, is_approval_step)): {
                                    Optional("requires", default=[]): [
                                        And(str, is_requires_id)
                                    ]
                                }
                            },
                            {  # Task converted to a Circleci job; can be referenced via "ServiceName:TaskName"
                                str: And(
                                    Use(capture_task),
                                    {
                                        # path to the tasks main folder; set as current working dir if not specifically set;
                                        # path relative to cicd.yml file; by default set to the cicd.yml directory
                                        Optional("path", default="."): str,
                                        # commands to be looked up in the linked general-config.yml
                                        "commands": [
                                            Optional(
                                                And(
                                                    str,
                                                    Use(convert_string_command),
                                                    is_valid_command,
                                                )
                                            ),
                                            And(command_schema, is_valid_command),
                                        ],
                                        Optional(
                                            "resource_class",
                                            default=context.resource_class,
                                        ): And(
                                            str,
                                            Or(
                                                "small",
                                                "windows.small",
                                                "medium",
                                                "windows.medium",
                                                "medium+",
                                                "large",
                                                "windows.large",
                                                "xlarge",
                                                "windows.xlarge",
                                                "2xlarge",
                                                "windows.2xlarge",
                                                "2xlarge+",
                                                "arm.medium",
                                                is_nw_runner_resource,
                                            ),
                                        ),
                                        Optional(
                                            "working_directory", default="/mnt/ramdisk"
                                        ): str,
                                        Optional("executor", default="default"): And(
                                            str, is_an_executor
                                        ),
                                        # triggers the job execution on change; relative path from root dir; for example: services/scheduling/apps/api/*
                                        Optional("dependencies", default=[]): [str],
                                        # list of task references that will be considered when determining the changeset; is used to create job dependencies in workflow jobs
                                        Optional("requires", default=[]): [
                                            And(str, is_requires_id)
                                        ],
                                        Optional(
                                            "not_changed_command", default=None
                                        ): Or(
                                            Optional(
                                                And(
                                                    str,
                                                    Use(convert_string_command),
                                                    is_valid_command,
                                                )
                                            ),
                                            And(command_schema, is_valid_command),
                                        ),
                                        Optional("parameters", default=[]): [
                                            {str: Or(str, bool, float, int, list)}
                                        ],
                                    },
                                )
                            },
                        )
                    }
                ],
                is_unique_task_id,
            ),
        }
    )
    return serviceSchema.validate(data)  # type: ignore

def checkout_method_validate(method: str) -> str:
    checkout_method_schema = Schema(And(str, Or("full", "blobless")))
    return checkout_method_schema.validate(method)

def general_config_validate(data: Dict[str, Any]) -> Dict[str, Any]:
    general_config_schema = Schema(
        {
            "version": Or(str, float),
            "machine": {"python": {"version": Or(str, float)}},
            "executors": {"default": any, str: object},
            Optional("commands"): {
                str: {  # all commands must have a parameters section
                    "parameters": {
                        # workign_dir for commands is mandatory
                        "working_dir": {
                            "type": "string",
                            Optional("default"): Or(str, bool, float, int),
                        },
                        Optional(str): {
                            "type": Or(
                                "string",
                                "boolean",
                                "integer",
                                "enum",
                                "executor",
                                "steps",
                            ),
                            Optional("default"): Or(str, bool, float, int, list),
                        },
                    },
                    str: any,  # all other keys we don't care
                },
                And(
                    "empty_job", error="You have to provide a command for 'empty_job'"
                ): {
                    "parameters": {
                        "job_name": {"type": "string"},
                        "reason": {"type": "string"},
                        Optional(str): any,
                    },
                    "steps": [{"run": any}, {str: any}],
                },
                And(
                    "setup_selfhosted_remote_docker",
                    error="You have to provide a command for 'selfhosted_remote_docker'",
                ): {
                    "parameters": {
                        Optional(str): any,
                    },
                    "steps": [{"run": any}, {str: any}],
                },
                And(
                    "changeset_info",
                    error="You have to provide a command for 'changeset_info'",
                ): {
                    "parameters": {
                        "file_name": {"type": "string"},
                        "data": {"type": "string"},
                        Optional(str): any,
                    },
                    "steps": [{"run": any}, {str: any}],
                },
            },
            Optional("parameters"): any,
            Optional(str): any,
        }
    )
    return general_config_schema.validate(data)  # type: ignore
