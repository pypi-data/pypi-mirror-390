# Winipedia Utils

A comprehensive Python utility package that enforces best practices, automates project setup, and provides a complete testing framework for modern Python projects.

> **Note:** Code examples in this README are provided for reference. Please check the source code and docstrings for complete and accurate implementations.

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Setup Process](#setup-process)
- [Utilities](#utilities)
- [Configuration Files](#configuration-files)
- [Important Notes](#important-notes)
- [Requirements](#requirements)

## Overview

**Winipedia Utils** is a utility library that serves two primary purposes:

1. **Utility Package** - Provides reusable functions across several domains (concurrency, data handling, security, testing, etc.)
2. **Project Framework** - Automates project setup, testing infrastructure, code quality checks, and best practices enforcement

## Key Features

- **Automatic Test Generation** - Creates mirror test structure matching your source code
- **Security First** - Built-in encryption, keyring integration, and security scanning
- **Concurrent Processing** - Unified interface for multiprocessing and multithreading
- **Data Handling** - Polars-based dataframe utilities with cleaning pipelines
- **Strict Type Checking** - mypy in strict mode with full type annotations
- **Code Quality** - Automated linting, formatting, and security checks
- **Comprehensive Logging** - Automatic method instrumentation and performance tracking

## Quick Start

### How to setup a new project

```bash
# 1: Create a new repository on GitHub
# The default branch must be called main
# add a PAT or Fine-Grained Access Token to your repo secrets called REPO_TOKEN that has write access to the repository (Adminstration and Contents)(needed for branch protection in health_check.yaml - see winipedia_utils.git.github.repo.protect and for commiting as an action in release.yaml)

# 2: Clone the repository
git clone https://github.com/owner/repo.git

# 3: Create a new poetry project
poetry init # or poetry new
# 4: Poetry will ask you some stuff when you run poetry init.
# First author name must be equal to the GitHub repository owner (username).
# The repository name must be equal to the package/project name. 
# (- instead of _ is fine, but only as the project name in pyproject.toml, folder names should all be _)

# 5: Add winipedia-utils to your project
poetry add winipedia-utils

# 6: Run the automated setup
poetry run python -m winipedia_utils.dev.setup
```

The setup script will automatically configure your project with all necessary files and standards.
If you wish to use winipedia_utils without its dev framework then just skip the setup step and you can access the utils via `winipedia_utils.utils`

## Setup Process

The `winipedia_utils.setup` command automates the entire project initialization in three main steps:

1. **Initialize Configuration Files** - Creates all necessary config files with standard configurations
2. **Create Project Root** - Sets up the project root directory with __init__.py files
3. **Run Pre-commit Hooks** - Executes all pre-commit hooks to validate the setup

### Generated Configuration Files

The setup creates the following configuration files:
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `.gitignore` - Git ignore rules (assumes you added one on GitHub before.)
- `pyproject.toml` - Project configuration with Poetry settings
- `.github/workflows/health_check.yaml` - Health check workflow (Runs on every push and pull request using a matrix strategy to test across multiple operating systems and Python versions)
- `.github/workflows/release.yaml` - Release workflow (Creates a release on GitHub when the same actions as in health check pass and commits are pushed to main)
- `.github/workflows/publish.yaml` - Publishing workflow (Publishes to PyPI when a release is created by the release workflow, if you use this workflow, you need to add a PYPI_TOKEN (named PYPI_TOKEN) to your GitHub secrets that has write access to the package on PyPI.)
- `py.typed` - PEP 561 marker for type hints
- `experiment.py` - For experimentation (ignored by git)
- `test_zero.py` - Test file with one empyt test (so that initial tests pass)
- `conftest.py` - Pytest configuration file
- `.python-version` - Python version file for pyenv (if you use pyenv, puts in the lowest supported python version in pyproject.toml opposed to the latest possible python version in workflows)

### GitHub Workflows and Matrix Strategy

The project uses GitHub Actions workflows with a **matrix strategy** to ensure cross-platform compatibility:

#### Matrix Configuration

The health check and release workflows test your code across:
- **Operating Systems**: Ubuntu (latest), Windows (latest), macOS (latest)
- **Python Versions**: All versions specified in your `pyproject.toml` (e.g., 3.12, 3.13, 3.14)

This matrix strategy ensures your code works reliably across different environments before merging or releasing.

#### Configuration File Structure
Config Files are autogenerated via ConfigFile non-abstract subclasses.
All nonabstract subclasses of ConfigFile are automatically created and managed when you commit or run pytest. winipedia_utils automatically discovers the pkg your_pkg.dev.configs and calls them. This way you can adjust or add some settings by subclassing. It is however important the parent class stays a subset of the child class according to the description in the function `nested_structure_is_subset` in `winipedia_utils.iterating.iterate` bc parents are still initialized and the order is not guaranteed.

#### Workflow Structure

Worklfows are a type of ConfigFile.

The health check workflow consists of two jobs:

1. **Matrix Job** (`health_check_matrix`) - Runs all checks in parallel across the matrix of OS and Python versions:
   - Checkout repository
   - Setup Git, Python, and Poetry
   - Add Poetry to PATH (Windows-specific step)
   - Install dependencies
   - Setup CI keyring
   - Protect repository (applies branch protection rules and repository settings)
   - Run pre-commit hooks (linting, formatting, type checking, security, tests)

2. **Aggregation Job** (`health_check`) - Aggregates matrix results into a single status check:
   - Required for branch protection compatibility
   - Only runs after all matrix jobs complete successfully
   - Provides a single status check that can be marked as required in branch protection rules

The release workflow extends the health check workflow and adds a release job that runs after all health checks pass.
A build job is added before the release job if a src/dev/artifacts/builder exists with Builder subclasses. This script is created by the setup command and can be modified to create build artifacts for your project. Winipedia Utils automatically discovers all subclasses of Builder (dev.artifacts.builder.base.base) and calls them if the artifacts folder contains any files.

### Pre-commit Hook Workflow

When you commit code using `git commit`, the following checks run automatically:

Info: If git commit fails bc of ModuleNotFoundError or smth similar, you need to run `poetry run git commit` instead.
winipedia_utils hook is a python script that depends on winipedia_utils being installed. Poetry is needed to install winipedia_utils.
Usually VSCode or other IDEs activates the venv automatically when opening the terminal but if not you need to activate it manually or run `poetry run git commit` instead. It fails fast, so if one hook in winipedia_utils hook fails, the others don't run bc sys.exit(1) is called.

Hooks run in the following order:

- Update package manager (poetry self update)
- Install packages (poetry install --with dev)
- Update packages (poetry update --with dev (winipedia_utils forces all dependencies with * to be updated to latest compatible version))
- Lock dependencies (poetry lock)
- Check package manager configs (poetry check --strict)
- Create tests (python -m winipedia_utils.dev.testing.create_tests)
- Lint code (ruff check --fix)
- Format code (ruff format)
- Check static types (mypy)
- Check security (bandit -c pyproject.toml -r .)
- Run tests (pytest (uses pyproject.toml as config))

### Auto-generated Test Structure

The test generation creates a **mirror structure** of your source code:

```
my_project/
├── my_project/
│   ├── module_a.py
│   └── package_b/
│       └── module_c.py
└── tests/
    ├── test_module_a.py
    └── test_package_b/
        └── test_module_c.py
```

For each function, class, and method, skeleton tests are created with `NotImplementedError` placeholders for you to implement.

If you have autosuse fixtures just write and add them to the `tests/base/fixtures` directory. They will be automatically discovered, plugged into conftest and used in all tests according to defined scope.
The filenames in the fixtures folder are just for organisation purposes for your convenience. You still have to 
apply the pytest.fixture decorator to the fixture function and define the scope. So a session scoped function defined on function.py will still run as a session scoped fixture.

## Configuration Files

Configuration files are managed automatically by the setup system:

- **Deleted files** - If you delete a config file, it will be recreated with standard configurations
- **Empty files** - If you want to disable a config file, make it empty. This signals that the file is unwanted and won't be modified
- **Custom additions** - You can add custom configurations as long as the standard configurations remain intact
- **Modified standards** - If you modify the standard configurations, they will be restored on the next setup run
- **Subclasses** - You can create custom config files by subclassing the standard ones. They will be automatically created and managed when you commit or run pytest. winipedia_utils automatically discovers and calls them. This way you can adjust or add some settings. It is however important the parent class stays a subset of the child class according to the description in the function `nested_structure_is_subset` in `winipedia_utils.iterating.iterate`.

## Branch Protection

As soon as you push to `main` on GitHub (provided the `REPO_TOKEN` secret is set up correctly), the `health_check.yaml` workflow will run and execute `winipedia_utils.dev.git.github.repo.protect`, which uses PyGithub to protect the repository.

### Repository Settings

The following repository settings are configured:

- **name** - Repository name from `pyproject.toml` or folder name (should match repo name)
- **description** - Repository description from `pyproject.toml`
- **default_branch** - `main`
- **delete_branch_on_merge** - `true`
- **allow_update_branch** - `true`
- **allow_merge_commit** - `false`
- **allow_rebase_merge** - `true`
- **allow_squash_merge** - `true`

### Branch Protection Rules

A ruleset named `main protection` is created for the `main` branch with the following rules:

- **Deletion** - Prevents branch deletion
- **Non-fast-forward** - Prevents non-fast-forward pushes (forces linear history by rejecting force pushes)
- **Creation** - Prevents branch creation directly on the protected branch
- **Update** - Prevents direct updates to protected branch (all changes must go through pull requests)
- **Required Linear History** - Enforces linear commit history (no merge commits allowed)
- **Required Signatures** - Requires all commits to be signed with GPG or SSH keys
- **Pull Request Requirements:**
  - Requires 1 approving review (at least one person must approve before merge)
  - Dismisses stale reviews on push (if you push a new commit, all reviews are dismissed and must be re-approved)
  - Requires code owner review (designated code owners must approve changes to their files)
  - Requires last push approval (the most recent push must be approved, not an earlier one)
  - Requires review thread resolution (all comments in reviews must be resolved before merge)
  - Allowed merge methods: `squash` and `rebase` (no merge commits, keeps history clean)
- **Required Status Checks:**
  - Strict mode enabled (all status checks must pass on the latest commit, not older ones)
  - Health check workflow must pass (the aggregated `health_check` job ensures all matrix combinations passed successfully)
- **Bypass Actors** - Repository admins can bypass all rules (for emergency situations)

## Utilities

Winipedia Utils provides comprehensive utility modules for common development tasks:

### Concurrent Processing

Unified interface for multiprocessing and multithreading:

```python
from winipedia_utils.utils.iterating.concurrent.multiprocessing import multiprocess_loop
from winipedia_utils.utils.iterating.concurrent.multithreading import multithread_loop
```

### Data Cleaning & Handling

Build data cleaning pipelines using Polars:

```python
from winipedia_utils.utils.data.dataframe.cleaning import CleaningDF
import polars as pl
```

### Logging Utilities

Simple, standardized logging setup with automatic method instrumentation:

```python
from winipedia_utils.utils.logging.logger import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

**Features:**
- Pre-configured logging levels
- ANSI color support for terminal output
- Automatic method logging via metaclasses

### Object-Oriented Programming Utilities

Advanced metaclasses and mixins for class composition and behavior extension:

```python
from winipedia_utils.utils.oop.mixins.mixin import ABCLoggingMixin, StrictABCLoggingMixin
```

### Security Utilities

Encryption and secure credential storage using keyring:

```python
from winipedia_utils.utils.security.keyring import (
    get_or_create_fernet,
    get_or_create_aes_gcm
)
```

### Testing Utilities

Comprehensive testing framework with automatic test generation:

```python
from winipedia_utils.utils.testing.assertions import assert_with_msg
from winipedia_utils.dev.testing.convention import (
    make_test_obj_name,
    get_test_obj_from_obj,
    make_test_obj_importpath_from_obj
)

# Custom assertions
assert_with_msg(result == expected, "Result does not match expected value")

# Test naming conventions
test_name = make_test_obj_name(my_function)  # "test_my_function"

# Get corresponding test object
test_obj = get_test_obj_from_obj(my_function)

# Get test import path
test_path = make_test_obj_importpath_from_obj(my_function)
```

**Features:**
- Automatic test file generation
- Mirror test structure matching source code
- Test naming conventions
- Fixture management with scopes (function, class, module, package, session)

### Module Introspection Utilities

Tools for working with Python modules, packages, classes, and functions:

```python
from winipedia_utils.utils.modules.package import find_packages, walk_package
from winipedia_utils.utils.modules.module import create_module, import_obj_from_importpath
from winipedia_utils.utils.modules.class_ import get_all_cls_from_module, get_all_methods_from_cls
from winipedia_utils.utils.modules.function import get_all_functions_from_module
```

### Text and String Utilities

String manipulation and configuration file handling:

```python
from winipedia_utils.utils.data.structures.text.string import value_to_truncated_string
```

### OS and System Utilities

Operating system and subprocess utilities:

```python
from winipedia_utils.utils.os.os import run_subprocess
```

### Iteration Utilities

Utilities for working with iterables and nested structures:

```python
from winipedia_utils.utils.iterating.iterate import get_len_with_default, nested_structure_is_subset
```

### Philosophy

The core philosophy of Winipedia Utils is to:

> **Enforce good habits, ensure clean code, and save time when starting new projects**

By automating setup, testing, linting, formatting, and type checking, you can focus on writing business logic instead of configuring tools.

## Requirements

- **Python:** 3.12 or higher
- **Poetry:** For dependency management
- **Git:** For version control and pre-commit hooks

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contributing

Contributions are welcome! Please ensure all code follows the project's quality standards.

