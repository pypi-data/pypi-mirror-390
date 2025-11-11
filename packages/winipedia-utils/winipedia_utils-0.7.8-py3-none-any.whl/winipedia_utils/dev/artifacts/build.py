"""Build artifacts for the project."""

from winipedia_utils.dev.artifacts.builder.base.base import Builder

if __name__ == "__main__":
    Builder.init_all_non_abstract_subclasses()
