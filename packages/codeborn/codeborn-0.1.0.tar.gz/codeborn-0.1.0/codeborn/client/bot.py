from __future__ import annotations

import asyncio
import contextlib
import sys
import threading
from datetime import datetime, timedelta
from contextlib import redirect_stdout, redirect_stderr
from typing import Any

from codeborn.client.game_api import GameApi
from codeborn.client.io import IORedirect, auto_flush_print, log_exceptions
from codeborn.client.messages import ApiMessage, MessageType


MEMORY_UPLOAD_INTERVAL = 90  # seconds


class Bot:
    """Base class for user-created Codeborn bots.

    The framework handles async I/O and service messages (like heartbeats)
    in the background so you can write normal synchronous code.
    """

    def __init__(self) -> None:
        self.api = GameApi(self)

        self._loop = asyncio.new_event_loop()
        self._background_loop = threading.Thread(target=self._start_background_loop, daemon=True)
        self._background_loop_ready = threading.Event()

        self._stdout = sys.stdout
        self._stderr = sys.stderr

        self.game_state: dict[str, Any] = {}
        self.game_state_timestamp: datetime = datetime.now()
        self._game_state_ready = threading.Event()

        self.memory: dict[str, Any] = {}
        self.memory_timestamp: datetime = datetime.now()
        self._memory_ready = threading.Event()

    def _start_background_loop(self) -> None:
        """Run the asyncio event loop in a background thread."""
        asyncio.set_event_loop(self._loop)
        self._background_loop_ready.set()

        async def background_tasks():
            listener = asyncio.create_task(self._listen())
            memory_uploader = asyncio.create_task(self._upload_memory())
            await asyncio.wait([listener, memory_uploader], return_when=asyncio.FIRST_COMPLETED)

        self._loop.run_until_complete(background_tasks())

    async def _listen(self) -> None:
        """Listen for messages from the engine asynchronously."""
        while True:
            if message_bytes := await asyncio.to_thread(sys.stdin.buffer.readline):
                try:
                    message = ApiMessage.from_bytes(message_bytes)
                except Exception:
                    continue
            else:
                break

            if self._handle_engine_message(message):
                continue

            self.on_message(message)

    async def _upload_memory(self) -> None:
        """Periodically send memory snapshot to the engine."""
        while True:
            await asyncio.sleep(MEMORY_UPLOAD_INTERVAL)
            try:
                message = ApiMessage(
                    type=MessageType.memory_upload,
                    payload={
                        'data': self.memory,
                    },
                )
                self.send(message)
                self.memory_timestamp = datetime.now()
            except Exception as exc:
                self.log_error(f'Memory upload failed: {exc!r}')

    def _handle_engine_message(self, message: ApiMessage) -> bool:
        """Handle built-in messages (not exposed to user code)."""
        match message.type:
            case MessageType.heartbeat_request:
                message = ApiMessage(type=MessageType.heartbeat_response)
                self.send(message)
                return True
            case MessageType.state_sync:
                self.game_state = message.payload
                self.game_state_timestamp = message.datetime
                self._game_state_ready.set()
                return True
            case MessageType.memory_download:
                self.memory = message.payload['data']
                self.memory_timestamp = datetime.fromisoformat(message.payload['updated_at'])
                self._memory_ready.set()
                return True
            case _:
                return False

    def start(self) -> None:
        """Entry point for user code."""
        with contextlib.suppress(KeyboardInterrupt):
            self._background_loop.start()
            with (
                redirect_stdout(IORedirect(self.log_info)),  # type: ignore
                redirect_stderr(IORedirect(self.log_error)),  # type: ignore
                auto_flush_print(),
                log_exceptions()
            ):
                self._background_loop_ready.wait()
                self._game_state_ready.wait()
                self._memory_ready.wait()
                self.run()

    # User API

    def on_message(self, message: ApiMessage) -> None:
        """Handle messages received from the engine."""
        pass

    def run(self) -> None:
        """User-defined main loop.

        Override this method.
        """
        while True:
            pass

    @property
    def game_state_age(self) -> timedelta:
        """Age of the current game state."""
        return datetime.now() - self.game_state_timestamp

    def send(self, message: ApiMessage) -> None:
        """Send a message to the engine."""
        self._stdout.buffer.write(message.to_bytes())
        self._stdout.buffer.flush()

    def log_debug(self, text: str) -> None:
        """Log a debug message to the engine."""
        message = ApiMessage(
            type=MessageType.bot_log,
            payload={
                'level': 'DEBUG',
                'text': text
            }
        )
        self.send(message)

    def log_info(self, text: str) -> None:
        """Log an info message to the engine."""
        message = ApiMessage(
            type=MessageType.bot_log,
            payload={
                'level': 'INFO',
                'text': text
            }
        )
        self.send(message)

    def log_error(self, text: str) -> None:
        """Log an error message to the engine."""
        message = ApiMessage(
            type=MessageType.bot_log,
            payload={
                'level': 'ERROR',
                'text': text
            }
        )
        self.send(message)
