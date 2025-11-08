"""Utilities for working with Python projects."""

from winipedia_utils.modules.module import create_module
from winipedia_utils.projects.poetry.config import (
    PyprojectConfigFile,  # avoid circular import
)
from winipedia_utils.text.config import (
    ConfigFile,  # avoid circular import
)


def create_project_root() -> None:
    """Create the project root."""
    src_package_name = PyprojectConfigFile.get_package_name()
    create_module(src_package_name, is_package=True)
    ConfigFile.init_config_files()
