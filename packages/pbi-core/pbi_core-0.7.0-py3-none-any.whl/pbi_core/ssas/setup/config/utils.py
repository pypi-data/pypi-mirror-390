import textwrap
from pathlib import Path

from pbi_core.logging import get_logger

from .exe_config import ExeStartupConfig
from .msmdsrv_config import MsmdsrvStartupConfig

logger = get_logger()

PACKAGE_DIR = Path(__file__).parents[3]
assert PACKAGE_DIR.name == "pbi_core"


def get_startup_config(config_path: Path | None = None) -> ExeStartupConfig | MsmdsrvStartupConfig:
    config_path = config_path or (PACKAGE_DIR / "local" / "settings.json")
    try:
        logger.info("Loading startup configuration", path=config_path)
        with config_path.open("r") as f:
            config_text = f.read()
            for config_cls in (MsmdsrvStartupConfig, ExeStartupConfig):
                try:
                    cfg = config_cls.model_validate_json(config_text)
                    logger.info(
                        "Loaded startup configuration",
                        path=config_path,
                        config_type=config_cls.__name__,
                    )
                    return cfg  # noqa: TRY300
                except Exception:  # noqa: BLE001, S110
                    pass
    except FileNotFoundError as e:
        logger.exception("Startup configuration not found", path=config_path)
        msg = textwrap.dedent("""
        You do not have a startup configuration set up for pbi_core.

        When loading a pbix file with pbi_core, the package needs one of the following:
            1. The package needs to be initialized once with "python -m pbi_core setup" to find the necessary PowerBI
               files
                - Note: This setup current only works with the "exe" configuration type. See more at https://douglassimonsen.github.io/pbi_core/setup/
            2. To be run while PowerBI Desktop is currently running, so that the SSAS server set up by PowerBI Desktop
               can be used
            3. The load_pbix function can be called with the `load_ssas=False` argument, which will not load the SSAS
               model and therefore not require the SSAS server to be set up.
        """).strip()
        raise FileNotFoundError(msg) from e
    msg = f"Could not validate startup configuration from {config_path}"
    raise ValueError(msg)
