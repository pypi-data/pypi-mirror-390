"""Config utilities for poetry and pyproject.toml."""

from functools import cache
from pathlib import Path
from typing import Any, cast

import requests
from packaging.version import Version

from winipedia_utils.dev.configs.base.base import ConfigFile, TomlConfigFile
from winipedia_utils.dev.configs.testing import ExperimentConfigFile
from winipedia_utils.dev.projects.poetry.dev_deps import DEV_DEPENDENCIES
from winipedia_utils.dev.projects.poetry.poetry import POETRY_ARG, VersionConstraint
from winipedia_utils.dev.testing.convention import TESTS_PACKAGE_NAME
from winipedia_utils.utils.data.structures.text.string import make_name_from_obj
from winipedia_utils.utils.os.os import run_subprocess


class PyprojectConfigFile(TomlConfigFile):
    """Config file for pyproject.toml."""

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file.

        We remove the wrong dependencies from the config before dumping.
        So we do not want dependencies under tool.poetry.dependencies but
        under project.dependencies. And we do not want dev dependencies under
        tool.poetry.dev-dependencies but under tool.poetry.group.dev.dependencies.
        """
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to pyproject.toml file."
            raise TypeError(msg)
        config = cls.remove_wrong_dependencies(config)
        super().dump(config)

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_repository_name(cls) -> str:
        """Get the repository name.

        Is the parent folder the project ives in and should be the same as the
        project name.
        """
        cwd = Path.cwd()
        return cwd.name

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        return {
            "project": {
                "name": make_name_from_obj(cls.get_repository_name(), capitalize=False),
                "readme": "README.md",
                "dynamic": ["dependencies"],
            },
            "build-system": {
                "requires": ["poetry-core>=2.0.0,<3.0.0"],
                "build-backend": "poetry.core.masonry.api",
            },
            "tool": {
                "poetry": {
                    "packages": [{"include": cls.get_repository_name()}],
                    "dependencies": dict.fromkeys(cls.get_dependencies(), "*"),
                    "group": {
                        "dev": {
                            "dependencies": dict.fromkeys(
                                cls.get_dev_dependencies() | DEV_DEPENDENCIES,
                                "*",
                            )
                        }
                    },
                },
                "ruff": {
                    "exclude": [".*", "**/migrations/*.py"],
                    "lint": {
                        "select": ["ALL"],
                        "ignore": ["D203", "D213", "COM812", "ANN401"],
                        "fixable": ["ALL"],
                        "pydocstyle": {"convention": "google"},
                    },
                },
                "mypy": {
                    "strict": True,
                    "warn_unreachable": True,
                    "show_error_codes": True,
                    "files": ".",
                },
                "pytest": {"ini_options": {"testpaths": [TESTS_PACKAGE_NAME]}},
                "bandit": {
                    "exclude_dirs": [ExperimentConfigFile.get_path().as_posix()],
                },
            },
        }

    @classmethod
    def get_package_name(cls) -> str:
        """Get the package name."""
        project_dict = cls.load().get("project", {})
        package_name = str(project_dict.get("name", ""))
        return package_name.replace("-", "_")

    @classmethod
    def remove_wrong_dependencies(cls, config: dict[str, Any]) -> dict[str, Any]:
        """Remove the wrong dependencies from the config."""
        # raise if the right sections do not exist
        if config.get("tool", {}).get("poetry", {}).get("dependencies") is None:
            msg = "No dependencies section in config"
            raise ValueError(msg)

        if (
            config.get("tool", {}).get("poetry", {}).get("group", {}).get("dev", {})
            is None
        ):
            msg = "No dev dependencies section in config"
            raise ValueError(msg)

        # remove the wrong dependencies sections if they exist
        if config.get("project", {}).get("dependencies") is not None:
            del config["project"]["dependencies"]
        if config.get("tool", {}).get("poetry", {}).get("dev-dependencies") is not None:
            del config["tool"]["poetry"]["dev-dependencies"]

        return config

    @classmethod
    def get_all_dependencies(cls) -> set[str]:
        """Get all dependencies."""
        return cls.get_dependencies() | cls.get_dev_dependencies()

    @classmethod
    def get_dev_dependencies(cls) -> set[str]:
        """Get the dev dependencies."""
        dev_dependencies = set(
            cls.load()
            .get("tool", {})
            .get("poetry", {})
            .get("group", {})
            .get("dev", {})
            .get("dependencies", {})
            .keys()
        )
        if not dev_dependencies:
            dev_dependencies = set(
                cls.load().get("dependency-groups", {}).get("dev", [])
            )
            dev_dependencies = {d.split("(")[0].strip() for d in dev_dependencies}
        return dev_dependencies

    @classmethod
    def get_dependencies(cls) -> set[str]:
        """Get the dependencies."""
        deps = set(cls.load().get("project", {}).get("dependencies", {}))
        deps = {d.split("(")[0].strip() for d in deps}
        if not deps:
            deps = set(
                cls.load()
                .get("tool", {})
                .get("poetry", {})
                .get("dependencies", {})
                .keys()
            )
        return deps

    @classmethod
    def get_expected_dev_dependencies(cls) -> set[str]:
        """Get the expected dev dependencies."""
        return set(
            cls.get_configs()["tool"]["poetry"]["group"]["dev"]["dependencies"].keys()
        )

    @classmethod
    def get_authors(cls) -> list[dict[str, str]]:
        """Get the authors."""
        return cast(
            "list[dict[str, str]]", cls.load().get("project", {}).get("authors", [])
        )

    @classmethod
    def get_main_author(cls) -> dict[str, str]:
        """Get the main author.

        Assumes the main author is the first author.
        """
        return cls.get_authors()[0]

    @classmethod
    def get_main_author_name(cls) -> str:
        """Get the main author name."""
        return cls.get_main_author()["name"]

    @classmethod
    @cache
    def fetch_latest_python_version(cls) -> Version:
        """Fetch the latest python version from python.org."""
        url = "https://endoflife.date/api/python.json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # first element has metadata for latest stable
        latest_version = data[0]["latest"]
        return Version(latest_version)

    @classmethod
    def get_latest_possible_python_version(cls) -> Version:
        """Get the latest possible python version."""
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        version = version_constraint.get_upper_inclusive()
        if version is None:
            version = cls.fetch_latest_python_version()
        return version

    @classmethod
    def get_first_supported_python_version(cls) -> Version:
        """Get the first supported python version."""
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        lower = version_constraint.get_lower_inclusive()
        if lower is None:
            msg = "Need a lower bound for python version"
            raise ValueError(msg)
        return lower

    @classmethod
    def get_supported_python_versions(cls) -> list[Version]:
        """Get all supported python versions."""
        constraint = cls.load()["project"]["requires-python"]
        version_constraint = VersionConstraint(constraint)
        return version_constraint.get_version_range(
            level="minor", upper_default=cls.fetch_latest_python_version()
        )

    @classmethod
    def update_poetry(cls) -> None:
        """Update poetry."""
        args = [POETRY_ARG, "self", "update"]
        run_subprocess(args)

    @classmethod
    def update_with_dev(cls) -> None:
        """Install all dependencies with dev."""
        args = [POETRY_ARG, "update", "--with", "dev"]
        run_subprocess(args)


class TypedConfigFile(ConfigFile):
    """Config file for py.typed."""

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "typed"

    @classmethod
    def load(cls) -> dict[str, Any] | list[Any]:
        """Load the config file."""
        return {}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if config:
            msg = "Cannot dump to py.typed file."
            raise ValueError(msg)

    @classmethod
    def get_configs(cls) -> dict[str, Any] | list[Any]:
        """Get the config."""
        return {}


class PyTypedConfigFile(ConfigFile):
    """Config file for py.typed."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path(PyprojectConfigFile.get_package_name())


class DotPythonVersionConfigFile(ConfigFile):
    """Config file for .python-version."""

    VERSION_KEY = "version"

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return ""  # so it builds the path .python-version

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "python-version"

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Get the config."""
        return {
            cls.VERSION_KEY: str(
                PyprojectConfigFile.get_first_supported_python_version()
            )
        }

    @classmethod
    def load(cls) -> dict[str, Any]:
        """Load the config file."""
        return {cls.VERSION_KEY: cls.get_path().read_text()}

    @classmethod
    def dump(cls, config: dict[str, Any] | list[Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, dict):
            msg = f"Cannot dump {config} to .python-version file."
            raise TypeError(msg)
        cls.get_path().write_text(config[cls.VERSION_KEY])
