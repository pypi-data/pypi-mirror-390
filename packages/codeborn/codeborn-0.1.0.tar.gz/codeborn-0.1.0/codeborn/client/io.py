import io
import builtins
from collections.abc import Callable
from contextlib import contextmanager
import sys
import traceback


@contextmanager
def auto_flush_print():
    """Temporarily force print() to flush=True for user code."""
    _orig_print = builtins.print

    def _auto_flush_print(*args, **kwargs):
        # avoid recursion when our own redirector prints/logs internally
        if builtins.print is not _orig_print:
            builtins.print = _orig_print
            try:
                kwargs.setdefault('flush', True)
                return _orig_print(*args, **kwargs)
            finally:
                builtins.print = _auto_flush_print
        else:
            kwargs.setdefault('flush', True)
            return _orig_print(*args, **kwargs)

    builtins.print = _auto_flush_print
    try:
        yield
    finally:
        builtins.print = _orig_print


@contextmanager
def log_exceptions():
    """Context manager that captures exceptions and prints a single-line traceback to stderr."""
    try:
        yield
    except Exception:
        err_text = traceback.format_exc()
        print(err_text, file=sys.stderr, flush=True)
        exit(1)


class IORedirect(io.TextIOBase):
    """Redirect stdout/stderr to a callback function."""

    def __init__(self, on_output: Callable[[str], None]) -> None:
        super().__init__()
        self._on_output = on_output
        self._buf: list[str] = []
        self.buffer = io.BytesIO()  # dummy for compatibility

    def write(self, text: str) -> int:
        """Write text to the buffer."""
        self._buf.append(text)
        return len(text)

    def flush(self) -> None:
        """Flush the buffer and call the output callback."""
        if text := ''.join(self._buf).strip().encode('unicode_escape').decode('ascii'):
            self._buf.clear()
            self._on_output(text)
