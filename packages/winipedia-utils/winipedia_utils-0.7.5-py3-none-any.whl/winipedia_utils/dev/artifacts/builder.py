"""Build utilities for creating and managing project builds.

This module provides functions for building and managing project artifacts,
including creating build scripts, configuring build environments, and
handling build dependencies. These utilities help with the packaging and
distribution of project code.
"""

import platform
from abc import abstractmethod
from importlib import import_module
from pathlib import Path

from winipedia_utils.dev.configs.builder import BuilderConfigFile
from winipedia_utils.utils.modules.class_ import (
    get_all_nonabstract_subclasses,
)
from winipedia_utils.utils.modules.module import to_module_name, to_path
from winipedia_utils.utils.oop.mixins.mixin import ABCLoggingMixin


class Builder(ABCLoggingMixin):
    """Base class for build scripts.

    Subclass this class and implement the get_artifacts method to create
    a build script for your project. The build method will be called
    automatically when the class is initialized. At the end of the file add
    if __name__ == "__main__":
        YourBuildClass()
    """

    ARTIFACTS_DIR_NAME = "artifacts"
    ARTIFACTS_PATH = Path(ARTIFACTS_DIR_NAME)

    @classmethod
    @abstractmethod
    def create_artifacts(cls) -> None:
        """Build the project.

        This method should create all artifacts in the ARTIFACTS_PATH folder.

        Returns:
            None
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
        cls.create_artifacts()
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

    @classmethod
    def get_artifacts(cls) -> list[Path]:
        """Get the built artifacts."""
        paths = list(cls.ARTIFACTS_PATH.glob("*"))
        if not paths:
            msg = f"Expected {cls.ARTIFACTS_PATH} to contain files"
            raise FileNotFoundError(msg)
        return paths

    @classmethod
    def get_non_abstract_subclasses(cls) -> set[type["Builder"]]:
        """Get all non-abstract subclasses of Builder."""
        path = BuilderConfigFile.get_parent_path()
        module_name = to_module_name(path)
        if not to_path(module_name, is_package=True).exists():
            return set()
        builds_pkg = import_module(module_name)
        return get_all_nonabstract_subclasses(cls, load_package_before=builds_pkg)

    @classmethod
    def init_all_non_abstract_subclasses(cls) -> None:
        """Build all artifacts."""
        for builder in cls.get_non_abstract_subclasses():
            builder()
