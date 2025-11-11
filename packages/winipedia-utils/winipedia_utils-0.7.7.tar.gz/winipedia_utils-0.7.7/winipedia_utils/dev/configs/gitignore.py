"""Config utilities for .gitignore."""

from pathlib import Path
from typing import Any

import requests

from winipedia_utils.dev.configs.base.base import ConfigFile, DotEnvConfigFile
from winipedia_utils.dev.configs.testing import ExperimentConfigFile


class GitIgnoreConfigFile(ConfigFile):
    """Config file for .gitignore."""

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename of the config file."""
        return ""  # so it builds the path .gitignore and not gitignore.gitignore

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        return Path()

    @classmethod
    def get_file_extension(cls) -> str:
        """Get the file extension of the config file."""
        return "gitignore"

    @classmethod
    def load(cls) -> list[str]:
        """Load the config file."""
        return cls.get_path().read_text().splitlines()

    @classmethod
    def dump(cls, config: list[str] | dict[str, Any]) -> None:
        """Dump the config file."""
        if not isinstance(config, list):
            msg = f"Cannot dump {config} to .gitignore file."
            raise TypeError(msg)
        cls.get_path().write_text("\n".join(config))

    @classmethod
    def get_configs(cls) -> list[str]:
        """Get the config."""
        # fetch the standard github gitignore via https://github.com/github/gitignore/blob/main/Python.gitignore
        needed = [
            *cls.get_github_python_gitignore(),
            "# vscode stuff",
            ".vscode/",
            "",
            "# winipedia_utils stuff",
            "# for walk_os_skipping_gitignore_patterns func",
            ".git/",
            "# for executing experimental code",
            ExperimentConfigFile.get_path().as_posix(),
        ]

        dotenv_path = DotEnvConfigFile.get_path().as_posix()
        if dotenv_path not in needed:
            needed.extend(["# for secrets used locally", dotenv_path])

        existing = cls.load()
        needed = [p for p in needed if p not in set(existing)]
        return existing + needed

    @classmethod
    def get_github_python_gitignore(cls) -> list[str]:
        """Get the standard github python gitignore."""
        url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
        res = requests.get(url, timeout=10)
        if not res.ok:
            if not Path(".gitignore").exists():
                msg = f"Failed to fetch {url}. Cannot create .gitignore."
                raise RuntimeError(msg)
            return []
        return res.text.splitlines()
