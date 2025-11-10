import os
import shutil
from pathlib import Path

import bs4

from pbi_core.ssas.setup.config import PACKAGE_DIR
from pbi_core.ssas.setup.config.msmdsrv_config import MsmdsrvStartupConfig

from .utils import validator_exists, validator_potential


def get_msmdsrv_ini_path() -> str | None:
    """Can require admin rights to do."""
    candidate_folders = [
        f"C:/Users/{os.getlogin()}/Microsoft/Power BI Desktop Store App/AnalysisServicesWorkspaces",
        "",
    ]
    for folder in candidate_folders:
        for path in Path(folder).glob("**/msmdsrv.ini"):
            return path.absolute().as_posix()
    return None


def get_certificate_directory() -> str | None:
    candidates = [
        f"C:/Users/{os.getlogin()}/AppData/Local/Microsoft/Power BI Desktop/CertifiedExtensions",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def create_ini_template(raw_path: Path) -> None:
    ini_contents = bs4.BeautifulSoup(raw_path.open(encoding="utf-8"), "xml")
    for tag in ["DataDir", "TempDir", "LogDir", "BackupDir", "CrashReportsFolder", "AllowedBrowsingFolders"]:
        ini_contents.find(tag).string = "{{data_directory}}"  # pyright: ignore reportAttributeAccessIssue
    ini_contents.find("CertifiedExtensions").Directories.string = "{{certificate_directory}}"  # pyright: ignore reportAttributeAccessIssue
    ini_contents.find("ExtensionDir").string = "{{bin_directory}}"  # pyright: ignore reportAttributeAccessIssue
    ini_contents.find("DataSourceImpersonationAccount").Password.string = ""  # pyright: ignore reportAttributeAccessIssue
    ini_contents.find("QueryLogConnectionString").string = ""  # pyright: ignore reportAttributeAccessIssue
    ini_contents.find(
        "PrivateProcess",
    ).string = "4"  # pyright: ignore reportAttributeAccessIssue  # this must point to an existing process (I think??). 4 is the system, so shouldn't ever fail
    with Path(PACKAGE_DIR / "local" / "msmdsrv_template.ini").open("w", encoding="utf-8") as f:
        # [39:] to remove "<?xml version="1.0" encoding="utf-8"?>"
        f.write(str(ini_contents)[39:])


def get_msmdsrv_exe_path() -> str | None:
    """Can require admin rights to do."""
    candidate_folders = ["C:/Program Files/Microsoft Power BI Desktop", "C:/Program Files/WindowsApps"]
    for folder in candidate_folders:
        for path in Path(folder).glob("**/msmdsrv.exe"):
            return path.parent.absolute().as_posix()
    return None


def gen_msmdsrv_setup(target_dir: Path) -> MsmdsrvStartupConfig:
    import inquirer  # noqa: PLC0415 # heavy import

    cert_dir = get_certificate_directory()
    msmdsrv_exe_path = get_msmdsrv_exe_path()
    msmdsrv_ini_path = get_msmdsrv_ini_path()

    default_workspace_path = (target_dir / "workspaces").absolute().as_posix()
    questions = [
        inquirer.Text(
            "workspace_dir",
            message="Path for temp workspaces",
            default=default_workspace_path,
            validate=validator_potential,
        ),
        inquirer.Text(
            "msmdsrv_ini",
            message="Path to PowerBI's msmdsrv.ini",
            default=msmdsrv_ini_path,
            validate=validator_exists,
        ),
        inquirer.Text(
            "bin_path",
            message="Path to PowerBI's bin folder",
            default=msmdsrv_exe_path,
            validate=validator_exists,
        ),
        inquirer.Text(
            "cert_dir",
            message="Path to PowerBI's CertifiedExtensions folder",
            default=cert_dir,
            validate=validator_exists,
        ),
    ]
    answers = inquirer.prompt(questions)
    assert answers is not None

    target_dir.mkdir(exist_ok=True)
    shutil.rmtree(target_dir)
    (target_dir / "pbi").mkdir(exist_ok=True, parents=True)

    shutil.copy(answers["msmdsrv_ini"], target_dir / "msmdsrv.ini")
    create_ini_template(target_dir / "msmdsrv.ini")

    shutil.copytree(answers["bin_path"], target_dir / "bin")
    shutil.copytree(answers["cert_dir"], target_dir / "CertifiedExtensions")

    config_data = {
        "msmdsrv_ini": target_dir / "msmdsrv_template.ini",
        "msmdsrv_exe": target_dir / "bin" / "msmdsrv.exe",
        "cert_dir": target_dir / "CertifiedExtensions",
        "workspace_dir": Path(answers["workspace_dir"]),
    }

    return MsmdsrvStartupConfig(**config_data)
