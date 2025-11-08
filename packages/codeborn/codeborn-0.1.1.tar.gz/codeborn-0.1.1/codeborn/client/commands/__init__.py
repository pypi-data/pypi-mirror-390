from __future__ import annotations

import abc
import typing
from uuid import UUID

from codeborn.client.messages import ApiMessage, MessageType

if typing.TYPE_CHECKING:
    from codeborn.client.bot import Bot


Gid: typing.TypeAlias = UUID | str


class DomainApi(abc.ABC):  # noqa: B024
    """API for single part of the game."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def _send(self, payload: dict) -> UUID:
        """Send a command through the api."""

        message = ApiMessage(
            type=MessageType.command,
            payload=payload
        )
        self.bot.send(message)
        return message.gid
