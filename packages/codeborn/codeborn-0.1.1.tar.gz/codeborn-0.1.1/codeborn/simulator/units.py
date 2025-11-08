from __future__ import annotations

from enum import StrEnum
from functools import cached_property

from codeborn.rules import UnitConfig, get_rules


class UnitRole(StrEnum):
    """Enumeration of different unit roles in combat."""

    infantry = 'infantry'
    cavalry = 'cavalry'
    ranged = 'ranged'

    async def dump(self, exclude: list[str] | set[str] | None = None) -> str:
        """Dump the unit role as a string."""
        return self.value


class UnitType(StrEnum):
    """Enumeration of different unit types."""

    light_infantry = 'light_infantry'
    heavy_infantry = 'heavy_infantry'
    spearmen = 'spearmen'
    light_cavalry = 'light_cavalry'
    heavy_cavalry = 'heavy_cavalry'
    archer = 'archer'
    crossbowman = 'crossbowman'

    @cached_property
    def config(self) -> UnitConfig:
        """Get the configuration for this unit type."""
        return get_rules().units[self.value]

    @cached_property
    def name(self) -> str:
        """Get the name of this unit."""
        return self.value.replace('_', ' ').title()

    @cached_property
    def roles(self) -> set[UnitRole]:
        return {UnitRole(role) for role in self.config.roles}

    @cached_property
    def stamina_recovery(self) -> float:
        """Get the stamina recovery rate for this unit type."""
        return self.config.stamina_recovery

    @cached_property
    def integrity_recovery(self) -> float:
        """Get the stamina recovery rate for this unit type."""
        return self.config.integrity_recovery

    @cached_property
    def hp(self) -> float:
        """Get the HP for this unit type."""
        return self.config.hp

    @cached_property
    def attack(self) -> float:
        """Get the attack strength for this unit type."""
        return self.config.attack

    @cached_property
    def counter_attack(self) -> float:
        """Get the counter attack strength for this unit type."""
        return self.config.attack

    @cached_property
    def initiative(self) -> float:
        """Get the initiative for this unit type."""
        return self.config.initiative

    @cached_property
    def engagement_capacity(self) -> int:
        """Get the engagement capacity for this unit type."""
        return self.config.engagement_capacity

    @cached_property
    def integrity_sensitivity(self) -> float:
        """Get the integrity sensitivity for this unit type."""
        return self.config.integrity_sensitivity

    @cached_property
    def stamina_sensitivity(self) -> float:
        """Get the stamina sensitivity for this unit type."""
        return self.config.stamina_sensitivity

    @cached_property
    def integrity_decay(self) -> float:
        """Get the integrity decay for this unit type."""
        return self.config.integrity_decay

    @cached_property
    def attack_stamina_cost(self) -> float:
        """Get the attack stamina cost for this unit type."""
        return self.config.attack_stamina_cost

    @cached_property
    def counter_stamina_cost(self) -> float:
        """Get the counter-attack stamina cost for this unit type."""
        return self.config.counter_stamina_cost

    async def dump(self, exclude: list[str] | set[str] | None = None) -> str:
        """Dump the unit type as a string."""
        return self.value


class SimulatedUnit:
    def __init__(self, type: UnitType, count: int, integrity: float = 1.0, stamina: float = 1.0) -> None:
        self.type = type
        self.count = count
        self.integrity = integrity
        self.stamina = stamina

    def __repr__(self) -> str:
        """String representation of the unit."""
        return f'<{self.type}:{self.count}>'

    @property
    def name(self) -> str:
        """Get name of the unit."""
        return self.type.name

    @property
    def efficiency_coef(self) -> float:
        """Get efficiency coefficient."""
        return (
            (0.5 + 0.5 * self.integrity ** self.integrity_sensitivity) *
            (0.5 + 0.5 * self.stamina ** self.stamina_sensitivity)
        )

    @property
    def roles(self) -> set[UnitRole]:
        """Get unit roles."""
        return self.type.roles

    @property
    def is_ranged(self) -> bool:
        """True if unit is ranged."""
        return UnitRole.ranged in self.roles

    @property
    def base_hp(self) -> float:
        """Get the base HP."""
        return self.type.hp

    @property
    def hp(self) -> float:
        """Get the effective HP."""
        return self.base_hp * self.efficiency_coef

    @property
    def base_attack(self) -> float:
        """Get the base attack strength."""
        return self.type.attack

    @property
    def attack(self) -> float:
        """Get the effective attack strength."""
        return self.base_attack * self.efficiency_coef

    @property
    def base_counter_attack(self) -> float:
        """Get the base counter attack strength."""
        return self.type.counter_attack

    @property
    def counter_attack(self) -> float:
        """Get the effective counter attack strength."""
        return self.base_counter_attack * self.efficiency_coef

    @property
    def base_initiative(self) -> float:
        """Get the base initiative."""
        return self.type.initiative

    @property
    def initiative(self) -> float:
        """Get the effective initiative."""
        return self.base_initiative * self.efficiency_coef

    @property
    def engagement_capacity(self) -> int:
        """Get engagement capacity."""
        return self.type.engagement_capacity

    @property
    def integrity_sensitivity(self) -> float:
        """Get integrity sensitivity."""
        return self.type.integrity_sensitivity

    @property
    def stamina_sensitivity(self) -> float:
        """Get stamina sensitivity."""
        return self.type.stamina_sensitivity

    @property
    def integrity_decay(self) -> float:
        """Get the integrity decay."""
        return self.type.integrity_decay

    @property
    def attack_stamina_cost(self) -> float:
        """Get attack stamina cost."""
        return self.type.attack_stamina_cost

    @property
    def counter_stamina_cost(self) -> float:
        """Get counter-attack stamina cost."""
        return self.type.counter_stamina_cost
