"""Configs for winipedia_utils.

All subclasses of ConfigFile in the configs package are automatically called.
"""

from pathlib import Path

import winipedia_utils
from winipedia_utils.dev import configs
from winipedia_utils.dev.configs.base.base import PythonConfigFile
from winipedia_utils.dev.configs.pyproject import PyprojectConfigFile
from winipedia_utils.utils.modules.module import to_path


class ConfigsConfigFile(PythonConfigFile):
    """Config file for configs.py."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the path to the config file."""
        src_package = PyprojectConfigFile.get_package_name()
        builds_package = configs.__name__.replace(
            winipedia_utils.__name__, src_package, 1
        )
        return to_path(builds_package, is_package=True)

    @classmethod
    def get_content_str(cls) -> str:
        """Get the content."""
        return '''"""Configs for winipedia_utils.

All subclasses of ConfigFile in the configs package are automatically called.
"""
'''
