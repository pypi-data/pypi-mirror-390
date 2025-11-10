from pathlib import Path

from attrs import fields

from pbi_core.attrs import BaseValidation, define

PACKAGE_DIR = Path(__file__).parents[3]
assert PACKAGE_DIR.name == "pbi_core"


@define()
class BaseStartupConfig(BaseValidation):
    workspace_dir: Path

    def __attrs_post_init__(self) -> None:
        for a in fields(self.__class__):
            val: Path = getattr(self, a.name)
            if val is not None and not val.is_absolute():
                val = PACKAGE_DIR / val
            setattr(self, a.name, val)
