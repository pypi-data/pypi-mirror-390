"""Entry point for the headless coder Python core package."""

__version__ = "0.1.0"

from .cancellation import AbortController, CancellationError, CancellationSignal, link_signal
from .registry import (
    clear_registered_adapters,
    create_coder,
    get_adapter_factory,
    register_adapter,
    unregister_adapter,
)
from .types import (
    AdapterFactory,
    AdapterName,
    CoderStreamEvent,
    CoderType,
    EventIterator,
    HeadlessCoder,
    Provider,
    PromptInput,
    PromptMessage,
    RunOpts,
    RunResult,
    SandboxMode,
    StartOpts,
    ThreadHandle,
    now,
)

__all__ = [
    "__version__",
    "AbortController",
    "AdapterFactory",
    "AdapterName",
    "CancellationError",
    "CancellationSignal",
    "CoderStreamEvent",
    "CoderType",
    "EventIterator",
    "HeadlessCoder",
    "Provider",
    "PromptInput",
    "PromptMessage",
    "RunOpts",
    "RunResult",
    "SandboxMode",
    "StartOpts",
    "ThreadHandle",
    "clear_registered_adapters",
    "create_coder",
    "get_adapter_factory",
    "link_signal",
    "now",
    "register_adapter",
    "unregister_adapter",
]
