import importlib.metadata

try:
    __version__ = importlib.metadata.version("bae-mem")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"

from bae_mem.client.main import AsyncMemoryClient, MemoryClient  # noqa: E402
from bae_mem.memory.main import AsyncMemory, Memory  # noqa: E402

__all__ = [
    "AsyncMemory",
    "AsyncMemoryClient",
    "Memory",
    "MemoryClient",
]
