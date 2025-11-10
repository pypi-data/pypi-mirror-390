import shutil
from pathlib import Path

from pbi_core.ssas.setup.config import PACKAGE_DIR
from pbi_core.ssas.setup.config.exe_config import ExeStartupConfig

from .utils import validator_exists, validator_potential


def get_pbi_bin_folder() -> str | None:
    """Can require admin rights to do."""
    candidate_folders = [
        "C:/Program Files/Microsoft Power BI Desktop",
        "C:/Program Files/WindowsApps",
        "C:/Program Files/Microsoft Power BI Desktop/bin",
    ]
    for folder in candidate_folders:
        for path in Path(folder).glob("**/msmdsrv.exe"):
            return path.parent.absolute().as_posix()
    return None


def gen_exe_setup(target_dir: Path) -> ExeStartupConfig:
    import inquirer  # noqa: PLC0415

    desktop_exe_path = ""
    if bin_folder := get_pbi_bin_folder():
        desktop_exe_path = f"{bin_folder}/PBIDesktop.exe"

    default_workspace_path = (target_dir / "workspaces").absolute().as_posix()
    questions = [
        inquirer.Text(
            "workspace_dir",
            message="Path for temp workspaces",
            default=default_workspace_path,
            validate=validator_potential,
        ),
        inquirer.Text(
            "desktop_exe",
            message="Path to PowerBI's desktop.exe",
            default=desktop_exe_path,
            validate=validator_exists,
        ),
    ]
    answers = inquirer.prompt(questions)
    assert answers is not None

    target_dir.mkdir(exist_ok=True)
    shutil.rmtree(target_dir)
    (target_dir / "pbi").mkdir(exist_ok=True, parents=True)

    config_data = {
        "workspace_dir": Path(answers["workspace_dir"]),
        "desktop_exe": Path(answers["desktop_exe"]),
    }

    for k, v in config_data.items():
        if PACKAGE_DIR in v.parents:
            config_data[k] = v.relative_to(PACKAGE_DIR)

    config_data["workspace_dir"].mkdir(exist_ok=True, parents=True)
    return ExeStartupConfig(**config_data)
