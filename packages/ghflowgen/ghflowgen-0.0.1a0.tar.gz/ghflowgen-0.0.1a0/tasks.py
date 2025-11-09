r"""Define some tasks that are executed with invoke."""

from __future__ import annotations

from typing import TYPE_CHECKING

from invoke import task

if TYPE_CHECKING:
    from invoke.context import Context

NAME = "ghflowgen"
SOURCE = f"src/{NAME}"
TESTS = "tests"
UNIT_TESTS = f"{TESTS}/unit"
INTEGRATION_TESTS = f"{TESTS}/integration"


@task
def check_format(c: Context) -> None:
    r"""Check code format."""
    c.run("black --check .", pty=True)


@task
def check_lint(c: Context) -> None:
    r"""Check code format."""
    c.run("ruff check --output-format=github .", pty=True)


@task
def create_venv(c: Context) -> None:
    r"""Create a virtual environment."""
    c.run("uv venv", pty=True)
    c.run("source .venv/bin/activate", pty=True)
    c.run("make install-invoke", pty=True)


@task
def doctest_src(c: Context) -> None:
    r"""Check the docstrings in source folder."""
    c.run(f"python -m pytest --xdoctest {SOURCE}", pty=True)
    c.run(
        'find . -type f -name "*.md" | xargs python -m doctest -o NORMALIZE_WHITESPACE '
        "-o ELLIPSIS -o REPORT_NDIFF",
        pty=True,
    )


@task
def install(c: Context, all_deps: bool = False, docs: bool = False) -> None:
    r"""Install packages."""
    cmd = ["uv pip install -r pyproject.toml --group dev"]
    if docs:
        cmd.append("--group docs")
    if all_deps:
        cmd.append("--all-extras")
    c.run(" ".join(cmd), pty=True)
    c.run("uv pip install -e .", pty=True)


@task
def update(c: Context) -> None:
    r"""Update the dependencies and pre-commit hooks."""
    c.run("uv sync --upgrade --all-extras", pty=True)
    c.run("uv tool upgrade --all", pty=True)
    c.run("pre-commit autoupdate", pty=True)


@task
def unit_test(c: Context, cov: bool = False) -> None:
    r"""Run the unit tests."""
    cmd = ["python -m pytest --xdoctest --timeout 10"]
    if cov:
        cmd.append(f"--cov-report html --cov-report xml --cov-report term --cov={NAME}")
    cmd.append(f"{UNIT_TESTS}")
    c.run(" ".join(cmd), pty=True)


@task
def integration_test(c: Context, cov: bool = False) -> None:
    r"""Run the unit tests."""
    cmd = ["python -m pytest --xdoctest --timeout 10"]
    if cov:
        cmd.append(
            f"--cov-report html --cov-report xml --cov-report term  --cov-append --cov={NAME}"
        )
    cmd.append(f"{INTEGRATION_TESTS}")
    c.run(" ".join(cmd), pty=True)


@task
def show_installed_packages(c: Context) -> None:
    r"""Show the installed packages."""
    c.run("uv pip list", pty=True)
    c.run("uv pip check", pty=True)


@task
def show_python_config(c: Context) -> None:
    r"""Show the python configuration."""
    c.run("uv python list --only-installed", pty=True)
    c.run("uv python find", pty=True)
    c.run("which python", pty=True)


@task
def publish_pypi(c: Context) -> None:
    r"""Publish the package to PyPI."""
    c.run("uv build", pty=True)
    c.run(
        f'uv run --with {NAME} --refresh-package {NAME} --no-project -- python -c "import {NAME}"',
        pty=True,
    )
    c.run("uv publish --token ${PYPI_TOKEN}", pty=True)


@task
def publish_doc_dev(c: Context) -> None:
    r"""Publish development (e.g. unstable) docs."""
    # delete previous version if it exists
    c.run("mike delete --config-file docs/mkdocs.yml main", pty=True, warn=True)
    c.run("mike deploy --config-file docs/mkdocs.yml --push --update-aliases main dev", pty=True)


@task
def publish_doc_latest(c: Context) -> None:
    r"""Publish latest (e.g. stable) docs."""
    from feu.git import get_last_version_tag_name  # noqa: PLC0415
    from packaging.version import Version  # noqa: PLC0415

    try:
        version = Version(get_last_version_tag_name())
        tag = f"{version.major}.{version.minor}"
    except RuntimeError:
        tag = "0.0"

    # delete previous version if it exists
    c.run(f"mike delete --config-file docs/mkdocs.yml {tag}", pty=True, warn=True)
    c.run(
        f"mike deploy --config-file docs/mkdocs.yml --push --update-aliases {tag} latest", pty=True
    )
    c.run("mike set-default --config-file docs/mkdocs.yml --push --allow-empty latest", pty=True)
