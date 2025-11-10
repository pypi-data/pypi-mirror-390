"""module contains functions that return the input for subprocess.run().

Each function is named after the hook it represents. The docstring of each function
describes the hook it represents. The function returns a list of strings that
represent the command to run. The first string is the command, and the following
strings are the arguments to the command. These funcs will be called by
run_hooks.py, which will pass the returned list to subprocess.run().
"""

from winipedia_utils.dev.projects.poetry.poetry import (
    POETRY_ARG,
    get_poetry_run_module_args,
)


def add_updates_to_git() -> list[str]:
    """Add the updated dependencies to git.

    This function returns the input for subprocess.run() to add the updated
    dependencies to git, so that the hook does not fail bc the file was changed.
    """
    return ["git", "add", "pyproject.toml", "poetry.lock"]


def check_package_manager_configs() -> list[str]:
    """Check that poetry.lock and pyproject.toml is up to date.

    This function returns the input for subprocess.run() to check that poetry.lock
    is up to date.
    """
    return [POETRY_ARG, "check", "--strict"]


def create_missing_tests() -> list[str]:
    """Create all tests for the project.

    This function returns the input for subprocess.run() to create all tests.
    """
    from winipedia_utils.dev.testing import (  # noqa: PLC0415  # avoid circular import
        create_tests,
    )

    return get_poetry_run_module_args(create_tests)


def lint_code() -> list[str]:
    """Check the code.

    This function returns the input for subprocess.run() to lint the code.
    It autofixes all errors that can be autofixed with --fix.
    """
    return ["ruff", "check", "--fix"]


def format_code() -> list[str]:
    """Format the code.

    This function calls ruff format to format the code.
    """
    return ["ruff", "format"]


def check_static_types() -> list[str]:
    """Check the types.

    This function returns the input for subprocess.run() to check the static types.
    """
    return ["mypy", "--exclude-gitignore"]


def check_security() -> list[str]:
    """Check the security of the code.

    This function returns the input for subprocess.run() to check the security of
    the code.
    """
    return ["bandit", "-c", "pyproject.toml", "-r", "."]


def run_tests() -> list[str]:
    """Run the tests.

    This function returns the input for subprocess.run() to run all tests.
    """
    return ["pytest"]
