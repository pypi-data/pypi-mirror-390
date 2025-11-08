from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import yaml
import msgspec


class TerrainConfig(msgspec.Struct):
    """Terrain configuration."""

    movement_cost: float


class UnitConfig(msgspec.Struct):
    """Unit configuration."""

    roles: set[str]
    stamina_recovery: float
    integrity_recovery: float
    hp: float
    attack: float
    counter_attack: float
    initiative: float
    engagement_capacity: int
    integrity_sensitivity: float
    stamina_sensitivity: float
    integrity_decay: float
    attack_stamina_cost: float
    counter_stamina_cost: float


class GameRules(msgspec.Struct):
    """Configuration of game rules."""

    units: dict[str, UnitConfig]
    terrain: dict[str, TerrainConfig]


def load_yaml(file: Path) -> dict[str, Any]:
    """Load YAML file as a dict."""
    with file.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


@cache
def get_rules() -> GameRules:
    """Get application configuration."""
    data = load_yaml(Path(__file__).parent / 'rules.yml')
    return msgspec.convert(data, type=GameRules)


if __name__ == '__main__':
    cfg = get_rules()
    print(msgspec.json.encode(cfg).decode())
