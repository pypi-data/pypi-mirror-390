# type: ignore  # noqa: PGH003
from typing import Literal

from .config import PACKAGE_DIR
from .prompts import gen_exe_setup, gen_msmdsrv_setup


def get_config_type() -> Literal["msmdsrv", "exe"]:
    import inquirer  # noqa: PLC0415 # heavy import

    questions = [
        inquirer.Text(
            "config_type",
            message="Select startup configuration type (msmdsrv/exe). msmdsrv is currently broken",
            default="exe",
            validate=lambda _, x: x in {"msmdsrv", "exe"},
        ),
    ]
    answers = inquirer.prompt(questions)
    ret = answers["config_type"]
    assert ret in {"msmdsrv", "exe"}
    return ret


def interactive_setup() -> None:
    target_dir = PACKAGE_DIR / "local"
    config_type = get_config_type()
    config = {
        "msmdsrv": gen_msmdsrv_setup,
        "exe": gen_exe_setup,
    }[config_type](target_dir)
    with (target_dir / "settings.json").open("w") as f:
        f.write(config.model_dump_json(indent=2))
