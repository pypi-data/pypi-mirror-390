"""Config utilities for testing."""

from abc import abstractmethod
from pathlib import Path
from typing import Any

from winipedia_utils.dev.configs.base.config import ConfigFile
from winipedia_utils.dev.testing.convention import TESTS_PACKAGE_NAME
from winipedia_utils.utils.modules.module import make_obj_importpath


class PythonConfigFile(ConfigFile):
    """Base class for python config files."""

    CONTENT_KEY = "content"

    @classmethod
    def load(cls) -> dict[str, str]:
        """Load the config file."""
        return {cls.CONTENT_KEY: cls.get_path().read_text()}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to python file."
            raise TypeError(msg)
        cls.get_path().write_text(config[cls.CONTENT_KEY])

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "py"

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        return {cls.CONTENT_KEY: cls.get_content_str()}

    @classmethod
    def get_file_content(cls) -> str:
        """Get the file content."""
        return cls.load()[cls.CONTENT_KEY]

    @classmethod
    @abstractmethod
    def get_content_str(cls) -> str:
        """Get the content."""

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        Python files are correct if they exist and contain the correct content.
        """
        return (
            super().is_correct()
            or cls.get_content_str().strip() in cls.load()[cls.CONTENT_KEY]
        )


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
