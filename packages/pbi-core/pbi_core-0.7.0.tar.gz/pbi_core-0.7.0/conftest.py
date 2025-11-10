import os
import pathlib

import pytest

from pbi_core import LocalReport


@pytest.fixture(autouse=True, scope="session")
def set_working_dir() -> None:
    os.chdir(pathlib.Path(__file__).parent / "example_pbis")


_ssas_pbix: LocalReport = LocalReport.load_pbix("example_pbis/test_ssas.pbix")


@pytest.fixture(scope="session")
def ssas_pbix() -> LocalReport:
    return _ssas_pbix
