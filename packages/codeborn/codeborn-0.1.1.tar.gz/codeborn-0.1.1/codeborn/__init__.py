from pathlib import Path


ROOT = Path(__file__).parent.parent.parent.absolute()
DEFAULT_CONFIG_PATH = ROOT / 'config.toml'


def to_abs_path(path: Path | str) -> Path:
    """Convert a path to an absolute path based on the ROOT directory."""
    if isinstance(path, str):
        path = Path(path)

    if not path.is_absolute():
        path = ROOT / path

    return path.resolve()
