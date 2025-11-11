"""Utilities for working with Python projects."""

from winipedia_utils.dev.configs.base.base import ConfigFile
from winipedia_utils.dev.configs.pyproject import PyprojectConfigFile
from winipedia_utils.dev.testing.convention import TESTS_PACKAGE_NAME
from winipedia_utils.utils.modules.module import create_module
from winipedia_utils.utils.modules.package import (
    create_init_files_for_package_and_subpackages,
)


def create_project_root() -> None:
    """Create the project root."""
    src_package_name = PyprojectConfigFile.get_package_name()
    src_package = create_module(src_package_name, is_package=True)
    ConfigFile.init_config_files()
    create_init_files_for_package_and_subpackages(src_package)
    create_init_files_for_package_and_subpackages(TESTS_PACKAGE_NAME)
