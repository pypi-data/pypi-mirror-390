"""Config utilities for testing."""

from pathlib import Path

from winipedia_utils.dev.configs.base.base import PythonConfigFile
from winipedia_utils.dev.testing.convention import TESTS_PACKAGE_NAME
from winipedia_utils.utils.modules.module import make_obj_importpath


class PythonTestsConfigFile(PythonConfigFile):
    """Base class for python config files in the tests directory."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path(TESTS_PACKAGE_NAME)


class ConftestConfigFile(PythonTestsConfigFile):
    """Config file for conftest.py."""

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config content."""
        from winipedia_utils.dev.testing.tests import conftest  # noqa: PLC0415

        return f'''"""Pytest configuration for tests.

This module configures pytest plugins for the test suite, setting up the necessary
fixtures and hooks for the different
test scopes (function, class, module, package, session).
It also import custom plugins from tests/base/scopes.
This file should not be modified manually.
"""

pytest_plugins = ["{make_obj_importpath(conftest)}"]
'''


class ZeroTestConfigFile(PythonTestsConfigFile):
    """Config file for test_zero.py."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        filename = super().get_filename()
        return "_".join(reversed(filename.split("_")))

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config."""
        return '''"""Contains an empty test."""


def test_zero() -> None:
    """Empty test.

    Exists so that when no tests are written yet the base fixtures are executed.
    """
'''


class ExperimentConfigFile(PythonConfigFile):
    """Config file for experiment.py.

    Is at root level and in .gitignore for experimentation.
    """

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_content_str(cls) -> str:
        """Get the config."""
        return '''"""This file is for experimentation and is ignored by git."""
'''
