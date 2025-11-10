from pathlib import Path


def validator_exists(_: dict, inp: str) -> bool:
    return Path(inp).exists()


def validator_potential(_: dict, inp: str) -> bool:
    try:
        Path(inp).mkdir(exist_ok=True, parents=True)
    except Exception:  # noqa: BLE001
        return False
    else:
        return True
