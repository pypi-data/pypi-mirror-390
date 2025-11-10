from pathlib import Path

import jinja2

from pbi_core.attrs import define
from pbi_core.logging import get_logger

from .base import BaseStartupConfig

logger = get_logger()

PACKAGE_DIR = Path(__file__).parents[3]
assert PACKAGE_DIR.name == "pbi_core"


@define()
class MsmdsrvStartupConfig(BaseStartupConfig):
    cert_dir: Path
    msmdsrv_ini: Path
    msmdsrv_exe: Path

    def msmdsrv_ini_template(self) -> jinja2.Template:
        return jinja2.Template(self.msmdsrv_ini.read_text())

    def get_exe(self) -> Path:
        return self.msmdsrv_exe
