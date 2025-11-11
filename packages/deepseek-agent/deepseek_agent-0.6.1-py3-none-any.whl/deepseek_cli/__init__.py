"""Top-level package for the DeepSeek CLI."""

from __future__ import annotations

try:  # pragma: no cover - import fallback
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - optional dependency guard
    def load_dotenv(*args, **kwargs):
        return False
else:  # pragma: no cover - trivial invocation
    load_dotenv()

from . import testing as testing

__all__ = ["__version__", "testing"]

__version__ = "0.6.1"
