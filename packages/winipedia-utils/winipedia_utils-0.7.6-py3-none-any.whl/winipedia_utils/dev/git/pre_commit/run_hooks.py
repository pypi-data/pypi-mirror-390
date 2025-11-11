"""Contains the pre-commit to run all hooks required by the winipedia_utils package.

This script is meant to be run by pre-commit (https://pre-commit.com/)
and should not be modified manually.
"""

import sys

from winipedia_utils.dev.git.pre_commit import hooks
from winipedia_utils.utils.logging.ansi import GREEN, RED, RESET
from winipedia_utils.utils.logging.logger import get_logger
from winipedia_utils.utils.modules.function import get_all_functions_from_module
from winipedia_utils.utils.os.os import run_subprocess

logger = get_logger(__name__)


def run_hooks() -> None:
    """Import all funcs defined in hooks.py and runs them."""
    hook_funcs = get_all_functions_from_module(hooks)

    for hook_func in hook_funcs:
        subprocess_args = hook_func()
        result = run_subprocess(
            subprocess_args, check=False, capture_output=True, text=True
        )
        passed = result.returncode == 0

        log_method = logger.info
        status_str = (f"{GREEN}PASSED" if passed else f"{RED}FAILED") + RESET
        if not passed:
            log_method = logger.error
            status_str += f"""
---------------------------------------------------------------------------------------------
Stdout:

{result.stdout}

---------------------------------------------------------------------------------------------
Stderr:

{result.stderr}

---------------------------------------------------------------------------------------------
"""

        # make the dashes always the same lentgth by adjusting to len of hook name
        num_dashes = 50 - len(hook_func.__name__)
        log_method(
            "Hook %s -%s> %s",
            hook_func.__name__,
            "-" * num_dashes,
            status_str,
        )
        if not passed:
            sys.exit(1)
