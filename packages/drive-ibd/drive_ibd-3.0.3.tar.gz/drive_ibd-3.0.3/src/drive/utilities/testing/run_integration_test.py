import argparse
import pytest
from pathlib import Path
import sysconfig
import sys

from log import CustomLogger

logger = CustomLogger.get_logger(__name__)


def check_for_file(file_path: Path) -> bool:
    return file_path.exists()


def get_sysconfig_path() -> Path:
    site_packages_path = sysconfig.get_paths().get("platlib")

    # if the sites package doesn't exist then we need to tell the user.
    if site_packages_path is None:
        logger.fatal(
            "Was not able to find the site-packages directory in the virtualenv that DRIVE was installed into. This error is unexpected. Please report this error to the maintainers. Terminating program..."
        )
        system_paths = ", ".join(sysconfig.get_paths())
        logger.debug(f"Current System paths are: {system_paths}")
        sys.exit(1)

    return Path(site_packages_path) / "tests"


def run_integration_test(args: argparse.Namespace) -> None:
    logger.info("Running integration test to ensure that DRIVE was installed correctly")

    test_path = get_sysconfig_path()

    possible_file_paths = [
        test_path / "test_integration.py",
        Path("tests/test_integration.py"),
        Path("/app/tests/test_integration.py"),
    ]

    test_ran = False

    for path in possible_file_paths:
        if check_for_file(path):
            logger.info(
                f"Found the integration test file: {path}. Running integration test."
            )
            pytest.main(
                [
                    "-v",
                    str(path),
                    "-W",
                    "ignore::DeprecationWarning",
                ]
            )

            test_ran = True
            break

    # if we don't find the test in the site package directory then we can test for it in different places
    if not test_ran:
        search_paths = ", ".join([str(path) for path in possible_file_paths])
        logger.fatal(
            f"Could not find the unit test script in any of the paths {search_paths}. Please ensure that one of these paths exist."
        )
        sys.exit(1)
