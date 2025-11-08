from codeborn.simulator.combat import simulate, CombatArmy
from codeborn.simulator.units import SimulatedUnit, UnitType


def prepare_units(army: dict[str, dict]) -> list[SimulatedUnit]:
    """Build a list of units from army configuration."""
    units = []
    for unit_type_name, unit_config in army.items():
        unit_type = UnitType(unit_type_name)
        unit = SimulatedUnit(
            type=unit_type,
            **unit_config
        )
        units.append(unit)
    return units


if __name__ == '__main__':
    instigator = CombatArmy(True, prepare_units({
        'light_infantry': {
            'count': 300,
        },
        'light_cavalry': {
            'count': 30,
        },
        'archer': {
            'count': 50,
        },
        'spearmen': {
            'count': 50,
        },
    }))

    resistor = CombatArmy(False, prepare_units({
        'light_infantry': {
            'count': 300,
        },
        'light_cavalry': {
            'count': 30,
        },
        'archer': {
            'count': 50,
        },
        'spearmen': {
            'count': 50,
        },
    }))

    battle_log = simulate(instigator, resistor)
    print(battle_log.visualize())
