"""Session-level test fixtures and utilities.

This module provides fixtures and test functions that operate at the session scope,
ensuring that project-wide conventions are followed and that the overall project
structure is correct. These fixtures are automatically applied to the test session
through pytest's autouse mechanism.
"""

from importlib import import_module
from pathlib import Path

import winipedia_utils
from winipedia_utils.dev.configs.base.base import ConfigFile
from winipedia_utils.dev.configs.pyproject import (
    PyprojectConfigFile,
)
from winipedia_utils.dev.testing.convention import (
    TESTS_PACKAGE_NAME,
    make_test_obj_importpath_from_obj,
)
from winipedia_utils.utils.logging.logger import get_logger
from winipedia_utils.utils.modules.module import to_path
from winipedia_utils.utils.modules.package import (
    find_packages,
    get_src_package,
    walk_package,
)
from winipedia_utils.utils.testing.assertions import assert_with_msg
from winipedia_utils.utils.testing.fixtures import autouse_session_fixture

logger = get_logger(__name__)


@autouse_session_fixture
def assert_dev_dependencies_config_is_correct() -> None:
    """Verify that the dev dependencies in consts.py are correct.

    This fixture runs once per test session and checks that the dev dependencies
    in consts.py are correct by comparing them to the dev dependencies in
    pyproject.toml.

    Raises:
        AssertionError: If the dev dependencies in consts.py are not correct

    """
    if PyprojectConfigFile.get_package_name() != winipedia_utils.__name__:
        # this const is only used in winipedia_utils
        # to be able to install them with setup.py
        return
    actual_dev_dependencies = PyprojectConfigFile.get_dev_dependencies()
    expected_dev_dependencies = PyprojectConfigFile.get_configs()["tool"]["poetry"][
        "group"
    ]["dev"]["dependencies"].keys()
    assert_with_msg(
        set(actual_dev_dependencies) == set(expected_dev_dependencies),
        "Dev dependencies in consts.py are not correct",
    )


@autouse_session_fixture
def assert_config_files_are_correct() -> None:
    """Verify that the dev dependencies are installed.

    This fixture runs once per test session and checks that the dev dependencies
    are installed by trying to import them.

    Raises:
        ImportError: If a dev dependency is not installed

    """
    # subclasses of ConfigFile
    ConfigFile.init_config_files()


@autouse_session_fixture
def assert_no_namespace_packages() -> None:
    """Verify that there are no namespace packages in the project.

    This fixture runs once per test session and checks that all packages in the
    project are regular packages with __init__.py files, not namespace packages.

    Raises:
        AssertionError: If any namespace packages are found

    """
    packages = find_packages(depth=None)
    namespace_packages = find_packages(depth=None, include_namespace_packages=True)

    any_namespace_packages = set(namespace_packages) - set(packages)
    assert_with_msg(
        not any_namespace_packages,
        f"Found namespace packages: {any_namespace_packages}. "
        f"All packages should have __init__.py files.",
    )


@autouse_session_fixture
def assert_all_src_code_in_one_package() -> None:
    """Verify that all source code is in a single package.

    This fixture runs once per test session and checks that there is only one
    source package besides the tests package.

    Raises:
        AssertionError: If there are multiple source packages

    """
    packages = find_packages(depth=0)
    src_package = get_src_package().__name__
    expected_packages = {TESTS_PACKAGE_NAME, src_package}
    assert_with_msg(
        set(packages) == expected_packages,
        f"Expected only packages {expected_packages}, but found {packages}",
    )


@autouse_session_fixture
def assert_src_package_correctly_named() -> None:
    """Verify that the source package is correctly named.

    This fixture runs once per test session and checks that the source package
    is correctly named after the project.

    Raises:
        AssertionError: If the source package is not correctly named

    """
    src_package = get_src_package().__name__
    config = PyprojectConfigFile()
    expected_package = config.get_package_name()
    assert_with_msg(
        src_package == expected_package,
        f"Expected source package to be named {expected_package}, "
        f"but it is named {src_package}",
    )


@autouse_session_fixture
def assert_project_structure_mirrored() -> None:
    """Verify that the project structure is mirrored in tests.

    This fixture runs once per test session and checks that for every package and
    module in the source package, there is a corresponding test package and module.

    Raises:
        AssertionError: If any package or module doesn't have a corresponding test

    """
    src_package = get_src_package()

    # we will now go through all the modules in the src package and check
    # that there is a corresponding test module
    for package, modules in walk_package(src_package):
        test_package_name = make_test_obj_importpath_from_obj(package)
        test_package = import_module(test_package_name)
        assert_with_msg(
            bool(test_package),
            f"Expected test package {test_package_name} to be a module",
        )

        for module in modules:
            test_module_name = make_test_obj_importpath_from_obj(module)
            test_module = import_module(test_module_name)
            assert_with_msg(
                bool(test_module),
                f"Expected test module {test_module_name} to be a module",
            )


@autouse_session_fixture
def assert_no_unit_test_package_usage() -> None:
    """Verify that the unit test package is not used in the project.

    This fixture runs once per test session and checks that the unit test package
    is not used in the project.

    Raises:
        AssertionError: If the unit test package is used

    """
    for path in Path().rglob("*.py"):
        assert_with_msg(
            "UnitTest".lower() not in path.read_text(encoding="utf-8"),
            f"Found unit test package usage in {path}. Use pytest instead.",
        )


@autouse_session_fixture
def assert_no_dev_usage_in_non_dev_files() -> None:
    """Verify that any utils from the dev folder are not used in non-dev files.

    E.g. winipedia_utils.utils can be used anywhere, winipedia_utils.dev not.

    This fixture runs once per test session and checks that any utils from the
    dev folder are not used in non-dev files.

    Raises:
        AssertionError: If any utils from the dev folder are used in non-dev files

    """
    src_pkg = get_src_package().__name__
    dev_pkg = src_pkg + ".dev"
    dev_path = to_path(dev_pkg, is_package=True)
    usages: list[Path] = []
    for path in Path(src_pkg).rglob("*.py"):
        # check if any part of the path contains dev_path
        if dev_path in path.parents:
            continue

        if dev_pkg in path.read_text(encoding="utf-8"):
            usages.append(path)

    # log a warning for each usage
    for path in usages:
        logger.warning(
            "Found %s usage in %s. This is not recommended in non-dev files.",
            dev_pkg,
            path,
        )
