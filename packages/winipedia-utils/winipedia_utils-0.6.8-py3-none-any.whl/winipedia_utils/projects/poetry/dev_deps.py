"""Contains a dict with the dev dependencies.

For poetry when winipedia_utils is a dependency.
winipedia_utils will add these automatically to the pyproject.toml file.
winipedia utils PyprojectConfigFile will auto dump the config here so it can access it
when being a dependency in another project.
"""

DEV_DEPENDENCIES: set[str] = {
    "ruff",
    "types-networkx",
    "types-defusedxml",
    "types-pyyaml",
    "pytest",
    "types-setuptools",
    "pytest-mock",
    "bandit",
    "pre-commit",
    "mypy",
    "types-tqdm",
}
