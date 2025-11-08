from __future__ import annotations

import typing

from codeborn.client.commands.army import ArmyCommands

if typing.TYPE_CHECKING:
    from codeborn.client.bot import Bot


class GameApi:
    "Game API."

    def __init__(self, bot: Bot):
        self.bot = bot
        self.army = ArmyCommands(bot)
