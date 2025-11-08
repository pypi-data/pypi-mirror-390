from typing import Iterable
from uuid import UUID

from codeborn.client.commands import DomainApi, Gid


class ArmyCommands(DomainApi):
    """Commands related to army."""

    def move(self, army: Gid, x: int, y: int) -> UUID:
        """Send command to move army to a given location.

        The x|y params must be integer coordinates of the new location at most
        1 square away.
        """
        return self._send({
            'command': 'move',
            'army_gid': army,
            'location': {
                'x': x,
                'y': y
            }
        })

    def split(self, army: Gid, units: dict[Gid, int]) -> UUID:
        """Send command to split army into two.

        The units param represents unit uuids and counts for the new army.
        """
        return self._send({
            'command': 'move',
            'army_gid': army,
            'units': units
        })

    def merge(self, armies: Iterable[Gid]) -> UUID:
        """Send command to merge multiple armies into one.

        All armies must be at the same location at the time of merge.
        """
        return self._send({
            'command': 'merge',
            'armies': list(armies)
        })
