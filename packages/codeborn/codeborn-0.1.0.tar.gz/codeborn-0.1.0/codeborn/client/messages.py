
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

import msgspec


class MessageType(StrEnum):
    """Types of messages exchanged between the Codeborn engine and agents."""

    # Heartbeat
    heartbeat_response = 'heartbeat_response'
    heartbeat_request = 'heartbeat_request'

    # Logging
    bot_log = 'bot_log'

    # Game state
    state_sync = 'state_sync'

    # Memory
    memory_download = 'memory_download'
    memory_upload = 'memory_upload'

    # Commands
    command = 'command'
    command_result = 'command_result'


class ApiMessage(msgspec.Struct, kw_only=True, frozen=True):
    """A message sent between the Codeborn engine and agents."""

    type: MessageType
    gid: UUID = msgspec.field(default_factory=uuid4)
    payload: dict[str, Any] = msgspec.field(default_factory=dict)
    datetime: datetime = msgspec.field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_bytes(cls, raw: bytes) -> ApiMessage:
        """Decode a JSON string or bytes into a Message instance."""
        return msgspec.json.decode(raw, type=cls)

    def to_bytes(self) -> bytes:
        """Encode the Message instance into a JSON string."""
        return msgspec.json.encode(self) + b'\n'
