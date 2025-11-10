import shutil
from pathlib import Path

from pbi_core.ssas.setup import get_startup_config


def get_workspaces() -> list[Path]:
    settings = get_startup_config()
    return list(settings.workspace_dir.iterdir())


def list_workspaces() -> None:
    settings = get_startup_config()
    workspaces = get_workspaces()
    if len(workspaces) == 0:
        print(f"No workspaces to remove from {settings.workspace_dir}")
    else:
        print("Folders to remove:")
        for folder in workspaces:
            print(" " * 4, folder)
        resp = input(f"Total workspaces: {len(workspaces)}. Press Y to continue: ")
        if resp.lower() != "y":
            print("Aborting")
            exit()


def clear_workspaces() -> None:
    settings = get_startup_config()
    workspaces = get_workspaces()
    if len(workspaces) == 0:
        print(f"No workspaces to remove from {settings.workspace_dir.absolute().as_posix()}")

    list_workspaces()

    for folder in workspaces:
        print(f"Deleting: {folder.absolute().as_posix()}")
        try:
            shutil.rmtree(folder)
        except PermissionError:
            print("\tWorkspace currently being used by an SSAS instance")
