from __future__ import annotations

import importlib
import logging

from ghflowgen.utils.pypi import get_pypi_versions
from ghflowgen.version import get_latest_major_versions, get_latest_minor_versions

logger = logging.getLogger(__name__)


def check_imports() -> None:
    logger.info("Checking imports...")
    objects_to_import = [
        "ghflowgen.utils",
        "ghflowgen.utils.export.save_json",
        "ghflowgen.utils.pypi.get_pypi_versions",
        "ghflowgen.version",
        "ghflowgen.version.get_latest_major_versions",
        "ghflowgen.version.get_latest_minor_versions",
        "ghflowgen.version.get_versions",
    ]
    for a in objects_to_import:
        module_path, name = a.rsplit(".", maxsplit=1)
        module = importlib.import_module(module_path)
        obj = getattr(module, name)
        assert obj is not None


def check_version() -> None:
    logger.info("Checking ghflowgen.version...")
    assert get_latest_major_versions("torch", upper="2.9") == ("1.13.1", "2.8.0")
    assert get_latest_minor_versions("torch", lower="2.0", upper="2.9") == (
        "2.0.1",
        "2.1.2",
        "2.2.2",
        "2.3.1",
        "2.4.1",
        "2.5.1",
        "2.6.0",
        "2.7.1",
        "2.8.0",
    )


def check_utils_pypi() -> None:
    logger.info("Checking ghflowgen.utils.pypi...")
    versions = get_pypi_versions("torch")
    assert isinstance(versions, tuple)
    assert len(versions) >= 42
    assert "2.8.0" in versions


def main() -> None:
    check_imports()
    check_utils_pypi()
    check_version()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
