"""Build utilities for creating and managing project builds.

This module provides functions for building and managing project artifacts,
including creating build scripts, configuring build environments, and
handling build dependencies. These utilities help with the packaging and
distribution of project code.
"""

import platform
from abc import abstractmethod
from pathlib import Path

from winipedia_utils.dev.configs.workflows.base.base import Workflow
from winipedia_utils.utils.oop.mixins.mixin import ABCLoggingMixin


class Build(ABCLoggingMixin):
    """Base class for build scripts.

    Subclass this class and implement the get_artifacts method to create
    a build script for your project. The build method will be called
    automatically when the class is initialized. At the end of the file add
    if __name__ == "__main__":
        YourBuildClass()
    """

    ARTIFACTS_PATH = Workflow.ARTIFACTS_PATH

    @classmethod
    @abstractmethod
    def get_artifacts(cls) -> list[Path]:
        """Build the project.

        Returns:
            list[Path]: List of paths to the built artifacts
        """

    @classmethod
    def __init__(cls) -> None:
        """Initialize the build script."""
        cls.build()

    @classmethod
    def build(cls) -> None:
        """Build the project.

        This method is called by the __init__ method.
        It takes all the files and renames them with -platform.system()
        and puts them in the artifacts folder.
        """
        cls.ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
        artifacts = cls.get_artifacts()
        for artifact in artifacts:
            parent = artifact.parent
            if parent != cls.ARTIFACTS_PATH:
                msg = f"You must create {artifact} in {cls.ARTIFACTS_PATH}"
                raise FileNotFoundError(msg)

            # rename the files with -platform.system()
            new_name = f"{artifact.stem}-{platform.system()}{artifact.suffix}"
            new_path = cls.ARTIFACTS_PATH / new_name
            artifact.rename(new_path)
