"""Base class for config files."""

import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from types import ModuleType
from typing import Any

import tomlkit
import yaml
from dotenv import dotenv_values

import winipedia_utils
from winipedia_utils.dev import configs
from winipedia_utils.dev.projects.poetry.poetry import (
    get_poetry_run_module_script,
)
from winipedia_utils.utils.data.structures.text.string import split_on_uppercase
from winipedia_utils.utils.iterating.iterate import nested_structure_is_subset
from winipedia_utils.utils.modules.class_ import init_all_nonabstract_subclasses
from winipedia_utils.utils.modules.module import import_module_with_default
from winipedia_utils.utils.modules.package import DependencyGraph, get_src_package


class ConfigFile(ABC):
    """Base class for config files."""

    @classmethod
    @abstractmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""

    @classmethod
    @abstractmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the config file."""

    @classmethod
    @abstractmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""

    @classmethod
    @abstractmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""

    @classmethod
    @abstractmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the config."""

    def __init__(self) -> None:
        """Initialize the config file."""
        self.get_path().parent.mkdir(parents=True, exist_ok=True)
        if not self.get_path().exists():
            self.get_path().touch()
            self.dump(self.get_configs())

        if not self.is_correct():
            config = self.add_missing_configs()
            self.dump(config)

        if not self.is_correct():
            msg = f"Config file {self.get_path()} is not correct."
            raise ValueError(msg)

    @classmethod
    def get_path(cls) -> Path:
        """Get the path to the config file."""
        return (
            cls.get_parent_path() / f"{cls.get_filename()}.{cls.get_file_extension()}"
        )

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        name = cls.__name__
        abstract_parents = [
            parent.__name__ for parent in cls.__mro__ if inspect.isabstract(parent)
        ]
        for parent in abstract_parents:
            name = name.removesuffix(parent)
        return "_".join(split_on_uppercase(name)).lower()

    @classmethod
    def add_missing_configs(cls) -> dict[str, Any] | list[Any]:
        """Add any missing configs to the config file."""
        current_config = cls.load()
        expected_config = cls.get_configs()
        nested_structure_is_subset(
            expected_config,
            current_config,
            cls.add_missing_dict_val,
            cls.insert_missing_list_val,
        )
        return current_config

    @staticmethod
    def add_missing_dict_val(
        expected_dict: dict[str, Any], actual_dict: dict[str, Any], key: str
    ) -> None:
        """Add a missing dict value."""
        actual_dict[key] = expected_dict[key]

    @staticmethod
    def insert_missing_list_val(
        expected_list: list[Any], actual_list: list[Any], index: int
    ) -> None:
        """Append a missing list value."""
        actual_list.insert(index, expected_list[index])

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        If the file is empty, it is considered correct.
        This is so bc if a user does not want a specific config file,
        they can just make it empty and the tests will not fail.
        """
        return cls.is_unwanted() or cls.is_correct_recursively(
            cls.get_configs(), cls.load()
        )

    @classmethod
    def is_unwanted(cls) -> bool:
        """Check if the config file is unwanted.

        If the file is empty, it is considered unwanted.
        """
        return cls.get_path().exists() and cls.get_path().read_text() == ""

    @staticmethod
    def is_correct_recursively(
        expected_config: dict[str, Any] | list[Any],
        actual_config: dict[str, Any] | list[Any],
    ) -> bool:
        """Check if the config is correct.

        Checks if expected is a subset recursively of actual.
        If a value is Any, it is considered correct.

        Args:
            expected_config: The expected config
            actual_config: The actual config

        Returns:
            True if the config is correct, False otherwise
        """
        return nested_structure_is_subset(expected_config, actual_config)

    @classmethod
    def init_config_files(cls) -> None:
        """Initialize all subclasses."""
        pkgs_depending_on_winipedia_utils = (
            DependencyGraph().get_all_depending_on_winipedia_utils(
                include_winipedia_utils=True
            )
        )

        pkgs_depending_on_winipedia_utils.add(get_src_package())
        for pkg in pkgs_depending_on_winipedia_utils:
            configs_pkg_name = configs.__name__.replace(
                winipedia_utils.__name__, pkg.__name__, 1
            )
            configs_pkg = import_module_with_default(configs_pkg_name)
            if not isinstance(configs_pkg, ModuleType):
                continue
            init_all_nonabstract_subclasses(cls, load_package_before=configs_pkg)

    @staticmethod
    def get_poetry_run_setup_script() -> str:
        """Get the poetry run setup script."""
        from winipedia_utils.dev import setup  # noqa: PLC0415  # avoid circular import

        return get_poetry_run_module_script(setup)


class YamlConfigFile(ConfigFile):
    """Base class for yaml config files."""

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the config file."""
        return yaml.safe_load(cls.get_path().read_text()) or {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        with cls.get_path().open("w") as f:
            yaml.safe_dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "yaml"


class TomlConfigFile(ConfigFile):
    """Base class for toml config files."""

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load the config file."""
        return tomlkit.parse(cls.get_path().read_text())

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to toml file."
            raise TypeError(msg)
        with cls.get_path().open("w") as f:
            tomlkit.dump(config, f, sort_keys=False)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "toml"


class DotEnvConfigFile(ConfigFile):
    """config class for .env config files."""

    @classmethod
    def load(cls) -> dict[str, str | None]:
        """Load the config file."""
        return dotenv_values(cls.get_path())

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        # is not supposed to be dumped to, so just raise error
        if config:
            msg = f"Cannot dump {config} to .env file."
            raise ValueError(msg)

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "env"

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return ""  # so it builds the path .env and not env.env

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        return {}

    @classmethod
    def is_correct(cls) -> bool:
        """Check if the config is correct."""
        return super().is_correct() or cls.get_path().exists()


class PythonConfigFile(ConfigFile):
    """Base class for python config files."""

    CONTENT_KEY = "content"

    @classmethod
    @abstractmethod
    def get_content_str(cls) -> str:
        """Get the content."""

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
    def is_correct(cls) -> bool:
        """Check if the config is correct.

        Python files are correct if they exist and contain the correct content.
        """
        return (
            super().is_correct()
            or cls.get_content_str().strip() in cls.load()[cls.CONTENT_KEY]
        )
