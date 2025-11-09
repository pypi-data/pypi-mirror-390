"""Versioning."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("shikaku")
except importlib.metadata.PackageNotFoundError:
    __version__ = None  # type: ignore[assignment]
