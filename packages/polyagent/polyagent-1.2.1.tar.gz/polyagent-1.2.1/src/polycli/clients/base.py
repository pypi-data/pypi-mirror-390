"""Base client class for all CLI tool clients."""

from abc import ABC, abstractmethod
from typing import Any, Generator
import shutil


class BaseClient(ABC):
    """Base class for all CLI/API clients."""

    # Module-level initialization - check availability once
    _available = None

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """
        Return identifier for backward compatibility.
        Evidence: Lines 313-326 in _determine_backend return these strings.
        """
        pass

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """
        Check if this client can be used.

        Evidence: Lines 312, 321, 323 check availability.
        - Claude/Qwen: Check CLI command exists
        - MiniSWE: Check Python package is importable
        - API: Always available (just needs network)

        Each client must implement their own check.
        """
        pass

    @classmethod
    @abstractmethod
    def run_cli(cls,
                agent: 'PolyAgent',
                prompt: str,
                **kwargs) -> Generator[Any, None, None]:
        """
        Run the client interface (CLI tool, API, or Python package).

        Evidence: Lines 236, 245, 247, 249 call _run_* methods.

        Common parameters (each client takes different subset):
        - prompt: str (all clients)
        - system_prompt: Optional[str] (all clients)
        - ephemeral: bool (all clients)
        - model: str (qwen, api, miniswe)
        - stream_events: bool (claude only)
        - schema_cls: Type[BaseModel] (api, miniswe)
        - memory_serializer: Callable (api, miniswe)
        - stream: bool (api only)
        - **kwargs: Additional params (api only)

        Agent provides access to:
        - agent.messages (conversation history)
        - agent.cwd (working directory)
        - agent.debug (debug flag)
        """
        pass