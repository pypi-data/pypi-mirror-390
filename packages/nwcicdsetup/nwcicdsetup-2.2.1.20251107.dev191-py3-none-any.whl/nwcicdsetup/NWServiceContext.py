from __future__ import annotations
from nwcicdsetup.Context import Context
from nwcicdsetup.circlecicontext import CircleCIContext

from typing import Any, Dict, List


class NWServiceContext:
    """Giving overall information this generation is running on"""

    def __init__(
            self,
            circleci_context: CircleCIContext,
            services: Dict[str, Any],
            general_config: Dict[str, Any],
            cwd: str,
            global_dependencies: List[str] = [],
            fake_deploy: bool = False,
            force: bool = False,
            resource_class:str = "small",
            checkout_method: str = "full"):

        self.cwd = cwd.replace("\\", "/")
        """current working directory"""
        self.fake_deploy: bool = fake_deploy
        """replace deploy logic with an echo"""
        self.force: bool = force
        """indicating to force run of all tasks"""
        self.global_dependencies = list(global_dependencies)
        """dependencies which cause a global rebuild"""
        self.services: Dict[str, NWService] = services
        """all services mapped via their ids"""
        self.circleci_context = circleci_context
        """we write this ref here on purpose so we see changes from the outside class internally"""
        self.general_config: Dict[str, Dict[str, Any]] = dict(general_config)
        """key/value pairs containing all general and cicd commands, executors that tasks can use to run"""
        self.resource_class: str = resource_class
        """Default resource-class use for all tasks"""
        self.checkout_method: str = checkout_method
        """CircleCi checkout method to use for all tasks [full, blobless]"""


    @property
    def branch(self) -> str:
        """returns the name of the current branch this is running on"""
        return self.circleci_context.branch

    @property
    def job_context(self) -> Context:
        return NWServiceContext.branch_to_context(self.branch)

    @staticmethod
    def branch_to_context(branch: str) -> Context:
        branch = branch.lower()
        if branch.startswith("develop"):
            return Context.DEV
        elif branch.startswith("testing"):
            return Context.TEST
        elif branch.startswith("staging"):
            return Context.STAGE
        elif branch.startswith("master") or branch.startswith("main"):
            return Context.PRODUCTION

        return Context.FEATURE