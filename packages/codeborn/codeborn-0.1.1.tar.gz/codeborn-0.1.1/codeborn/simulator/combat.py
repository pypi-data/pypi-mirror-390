from __future__ import annotations

import math

from codeborn.simulator.units import SimulatedUnit, UnitRole

from io import StringIO
import abc

from pydantic import BaseModel, ConfigDict
from rich.console import Console
from rich.table import Table


class Cohort:
    """Group of soldiers within a unit."""

    def __init__(
        self, count: int, integrity: float, max_engagements: int, engagements: int = 0, free_action: bool = True
    ) -> None:
        self.count = count
        self.integrity = integrity
        self.max_engagements = max_engagements
        self.engagements = engagements
        self.free_action = free_action

    @property
    def available_engagements(self) -> int:
        """Number of engagements the cohort can still participate in."""
        return self.max_engagements - self.engagements

    def split(self, count: int) -> Cohort:
        """Split new cohort from the current one with given number of soldiers."""
        if count >= self.count:
            raise ValueError(f'Cannot split out {count} soldiers from cohort of {self.count}.')

        self.count -= count

        return Cohort(
            count=count,
            integrity=self.integrity,
            max_engagements=self.max_engagements,
            engagements=self.engagements,
            free_action=self.free_action
        )


class CombatUnit:
    """Wrapper over unit to track stats during combat."""

    def __init__(self, unit: SimulatedUnit, is_instigator: bool) -> None:
        self.unit = unit
        self.orig_count = self.unit.count
        self.orig_integrity = self.unit.integrity
        self.is_instigator = is_instigator
        self.cohorts: list[Cohort] = [Cohort(
            count=self.unit.count,
            integrity=self.unit.integrity,
            max_engagements=self.unit.engagement_capacity
        )]

    def __repr__(self) -> str:
        """String representation of the combat unit."""
        return f'<{self.unit.type.value} {'att' if self.is_instigator else 'def'}>'

    def get_count_to_act(self) -> int:
        """Total number of soldiers that can still attack / act."""
        return sum(cohort.count for cohort in self.cohorts if cohort.free_action)

    def get_attacker_cohorts(self, attacker_count: int) -> tuple[list[Cohort], int]:
        """Get acting cohorts with count equal to required actors."""
        engaged_cohorts = []

        # use only cohorts with available action
        attacker_cohorts = [cohort for cohort in self.cohorts if cohort.free_action]

        # less engaged cohorts get to act first
        attacker_cohorts = sorted(attacker_cohorts, key=lambda cohort: -cohort.available_engagements)

        for cohort in attacker_cohorts:
            if attacker_count <= 0:
                break

            if cohort.count > attacker_count:
                cohort = self.spit_cohort(cohort, attacker_count)
            engaged_cohorts.append(cohort)
            attacker_count -= cohort.count

        satisfied_attackers = sum(cohort.count for cohort in engaged_cohorts)
        return engaged_cohorts, satisfied_attackers

    def get_defender_cohorts(self, attacker_count: int) -> tuple[list[Cohort], int, int]:
        """Get targeted cohorts, number of satisfied actors and number of targets."""
        remaining_attackers = attacker_count
        engaged_cohorts = []

        # use only cohorts with available engagements
        defender_cohorts = [cohort for cohort in self.cohorts if cohort.available_engagements]

        # less engaged cohorts get attacked first
        defender_cohorts = sorted(defender_cohorts, key=lambda cohort: -cohort.available_engagements)

        for cohort in defender_cohorts:
            if remaining_attackers <= 0:
                break

            max_attackers_for_this_cohort = cohort.count * cohort.available_engagements
            attackers_allocated = min(remaining_attackers, max_attackers_for_this_cohort)

            if attackers_allocated < max_attackers_for_this_cohort:
                # Split cohort so we can track partial engagement separately
                defenders_needed = math.ceil(attackers_allocated / cohort.available_engagements)
                cohort = self.spit_cohort(cohort, defenders_needed)

            engaged_cohorts.append(cohort)
            remaining_attackers -= attackers_allocated

        satisfied_attackers = min(attacker_count - remaining_attackers, attacker_count)
        defender_count = sum(cohort.count for cohort in engaged_cohorts)

        return engaged_cohorts, satisfied_attackers, defender_count

    def use_action(self, cohorts: list[Cohort]) -> None:
        """Remove free action from given cohorts."""
        for cohort in cohorts:
            cohort.free_action = False

    def distribute_engagements(self, cohorts: list[Cohort]) -> None:
        """Distribute used engagements between targeted units."""
        for cohort in cohorts:
            cohort.engagements = cohort.max_engagements

    def spit_cohort(self, cohort: Cohort, count: int) -> Cohort:
        """Split new cohort from the current one with given number of soldiers."""
        if count == cohort.count:
            return cohort

        cohort = cohort.split(count)
        self.cohorts.append(cohort)
        return cohort

    def remove_empty_cohorts(self) -> None:
        """Remove empty cohorts from the combat unit."""
        self.cohorts = [cohort for cohort in self.cohorts if cohort.count > 0]

    def apply_new_counts(self) -> None:
        """Apply new counts (after deaths) to the underlying unit."""
        self.unit.count = sum(cohort.count for cohort in self.cohorts)

    def apply_new_integrity(self) -> None:
        """Apply new integrity to the underlying unit."""
        integrity_total = 0
        count_total = 0
        for cohort in self.cohorts:
            integrity_total += (cohort.integrity * cohort.count)
            count_total += cohort.count
        self.unit.integrity = integrity_total / count_total


class CombatArmy:
    """Wrapper over army to track stats during combat."""

    def __init__(self, is_instigator: bool, units: list[SimulatedUnit]) -> None:
        self.is_instigator = is_instigator
        self.units = [CombatUnit(unit, is_instigator) for unit in units]


class EngagementLog(BaseModel, abc.ABC):
    """Log of single engagement in the battle."""

    attacker_unit: CombatUnit
    attacker_count: int

    defender_unit: CombatUnit
    defender_count: int

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abc.abstractmethod
    def visualize(self, console: Console) -> None:
        """Visualize output of the attack into console."""

    @property
    def _attacker_color(self) -> str:
        """Color of the attacker unit."""
        return 'red' if self.attacker_unit.is_instigator else 'blue'

    @property
    def _defender_color(self) -> str:
        """Color of the defender unit."""
        return 'red' if self.defender_unit.is_instigator else 'blue'

    @property
    def _attacker_title(self) -> str:
        """Title (name and color) of the attacker unit."""
        return f'[{self._attacker_color}][bold]{self.attacker_unit.unit.name}[/] ({self.attacker_count})[/]'

    @property
    def _defender_title(self) -> str:
        """Title (name and color) of the defender unit."""
        return f'[{self._defender_color}][bold]{self.defender_unit.unit.name}[/] ({self.defender_count})[/]'


class AttackLog(EngagementLog):
    """Log of direct attack in the battle."""

    is_ranged: bool = False
    kills: int
    integrity_loss: float

    def visualize(self, console: Console) -> None:
        """Write attack log in human readable form into given console."""
        dc = self._defender_color

        if self.defender_count > self.kills:
            integrity_loss = f'Integrity loss: [{dc}]{self.integrity_loss * 100:.1f}%[/]'
        else:
            integrity_loss = ''

        console.print(
            f'{self._attacker_title} attacks {self._defender_title}. [{dc}]{self.kills}[/] killed. {integrity_loss}'
        )


class CounterAttackLog(EngagementLog):
    """Log of counter-attack in the battle."""

    kills: int
    integrity_loss: float

    def visualize(self, console: Console) -> None:
        dc = self._defender_color

        if self.defender_count > self.kills:
            integrity_loss = f'Integrity loss: [{dc}]{self.integrity_loss * 100:.1f}%[/]'
        else:
            integrity_loss = ''

        console.print(
            f'{self._attacker_title} counter-attacks {self._defender_title}. '
            f'[{dc}]{self.kills}[/] killed. {integrity_loss}'
        )


class BattleLog(BaseModel):
    """Log of single battle that can be represented as json or in human readable form."""

    instigator_units: list[CombatUnit]
    resistor_units: list[CombatUnit]

    engagements: list[EngagementLog] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def visualize(self) -> str:
        """Represent the battle as a human readable string."""

        def _print_result_table(units: list[CombatUnit], color: str, console: Console) -> None:
            """Write results table of single side to the console."""
            table = Table()
            table.add_column('Name', style=color, no_wrap=True)
            table.add_column('Count (orig)', justify='right')
            table.add_column('Count (final)', justify='right')
            table.add_column('Integrity (orig)', justify='right')
            table.add_column('Integrity (final)', justify='right')

            for unit in units:
                table.add_row(
                    unit.unit.name,
                    str(unit.orig_count),
                    str(unit.unit.count),
                    f'{unit.orig_integrity * 100:.1f}%',
                    f'{unit.unit.integrity * 100:.1f}%',
                )

            console.print(table)

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, color_system='truecolor')

        for attack in self.engagements:
            attack.visualize(console)

        _print_result_table(self.instigator_units, 'red', console)
        _print_result_table(self.resistor_units, 'blue', console)

        return buffer.getvalue()


def sort_by_attack_order(combat_units: list[CombatUnit]) -> list[CombatUnit]:
    """Sort units in order they should resolve their attack.

    Units with highest initiative attack first, then attacker units, then smaller units.
    """
    def sort_key(combat_unit: CombatUnit) -> tuple[float, ...]:
        return (
            combat_unit.unit.initiative,
            combat_unit.is_instigator,
            -combat_unit.unit.count
        )
    return sorted(combat_units, key=sort_key, reverse=True)


def sort_by_defense_order(combat_units: list[CombatUnit]) -> list[CombatUnit]:
    """Sort units in order they should be targeted by other units.

    Infantry is targeted first, then cavalry, then ranged, then larger units, then units with low initiative.
    """
    def sort_key(combat_unit: CombatUnit) -> tuple[float, ...]:
        return (
            UnitRole.infantry in combat_unit.unit.roles,
            UnitRole.cavalry in combat_unit.unit.roles,
            UnitRole.ranged in combat_unit.unit.roles,
            combat_unit.unit.count,
            -combat_unit.unit.initiative,
        )
    return sorted(combat_units, key=sort_key, reverse=True)


def distribute_deaths(cohorts: list[Cohort], killed: int) -> None:
    """Distribute deaths between cohorts."""
    for cohort in cohorts:
        if killed > cohort.count:
            killed -= cohort.count
            cohort.count = 0
        else:
            cohort.count -= killed
            break


def distribute_integrity_loss(cohorts: list[Cohort], integrity_loss: float) -> None:
    """Distribute integrity loss between cohorts."""
    for cohort in cohorts:
        cohort.integrity = max(0, cohort.integrity - integrity_loss)


def get_kills_and_integrity_loss(
    attacker_count: int,
    attacker_unit: CombatUnit,
    defender_count: int,
    defender_unit: CombatUnit,
    is_counter_attack: bool
) -> tuple[int, float]:
    """Calculate number of killed soldiers and damage to integrity"""
    attack_strength = getattr(attacker_unit.unit, 'counter_attack' if is_counter_attack else 'attack')
    total_damage = attack_strength * attacker_count
    kills = min(math.floor(total_damage / defender_unit.unit.hp), defender_count)
    defender_total_hp = defender_count * defender_unit.unit.hp
    damage_ratio = (total_damage * 1) / defender_total_hp
    integrity_loss = defender_unit.unit.integrity_decay * damage_ratio

    return kills, integrity_loss


def simulate(instigator: CombatArmy, resistor: CombatArmy) -> BattleLog:
    """Simulate battle between two armies."""
    instigator_units = sort_by_defense_order(instigator.units)
    resistor_units = sort_by_defense_order(resistor.units)
    all_units = sort_by_attack_order(instigator_units + resistor_units)

    battle_log = BattleLog(instigator_units=instigator_units, resistor_units=resistor_units)

    for attacker_unit in all_units:
        total_attacker_count = attacker_unit.get_count_to_act()
        defender_units = resistor_units if attacker_unit.is_instigator else instigator_units

        for defender_unit in defender_units:
            defender_cohorts, attacker_count, defender_count = defender_unit.get_defender_cohorts(total_attacker_count)
            attacker_cohorts, attacker_count = attacker_unit.get_attacker_cohorts(attacker_count)

            defender_soldiers_killed, defender_integrity_loss = get_kills_and_integrity_loss(
                attacker_count, attacker_unit, defender_count, defender_unit, False
            )
            distribute_deaths(defender_cohorts, defender_soldiers_killed)
            distribute_integrity_loss(defender_cohorts, defender_integrity_loss)

            battle_log.engagements.append(AttackLog(
                is_ranged=attacker_unit.unit.is_ranged,
                attacker_unit=attacker_unit,
                attacker_count=attacker_count,
                defender_unit=defender_unit,
                defender_count=defender_count,
                kills=defender_soldiers_killed,
                integrity_loss=defender_integrity_loss
            ))

            if not attacker_unit.unit.is_ranged:  # ranged attacks don't trigger counter-strike
                defender_unit.use_action(defender_cohorts)
                attacker_soldiers_killed, attacker_integrity_loss = get_kills_and_integrity_loss(
                    defender_count, defender_unit, attacker_count, attacker_unit, True
                )
                distribute_deaths(attacker_cohorts, attacker_soldiers_killed)
                distribute_integrity_loss(attacker_cohorts, attacker_integrity_loss)

                battle_log.engagements.append(CounterAttackLog(
                    attacker_unit=defender_unit,
                    attacker_count=defender_count,
                    defender_unit=attacker_unit,
                    defender_count=attacker_count,
                    kills=attacker_soldiers_killed,
                    integrity_loss=attacker_integrity_loss
                ))

            attacker_unit.use_action(attacker_cohorts)
            defender_unit.distribute_engagements(defender_cohorts)

            total_attacker_count -= attacker_count
            if total_attacker_count <= 0:
                break

    for unit in all_units:
        unit.apply_new_counts()
        unit.apply_new_integrity()

    return battle_log
