from pathlib import Path

from pbi_core.attrs import BaseValidation, define
from pbi_core.logging import get_logger

logger = get_logger()

PACKAGE_DIR = Path(__file__).parents[3]
assert PACKAGE_DIR.name == "pbi_core"


@define()
class ExeStartupConfig(BaseValidation):
    workspace_dir: Path
    desktop_exe: Path

    def get_exe(self) -> Path:
        return self.desktop_exe
