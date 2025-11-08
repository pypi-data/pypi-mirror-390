"""InnerLoop SDK public API.

Re-exports the modern Loop API and common configuration models.
"""

from .errors import (  # noqa: F401
    CliExitError,
    CliNotFoundError,
    CliTimeoutError,
    InnerLoopError,
)
from .mcp import (  # noqa: F401
    LocalMcpServer,
    RemoteMcpServer,
)
from .permissions import Permission  # noqa: F401
from .providers import (  # noqa: F401
    AnthropicProvider,
    LMStudioProvider,
    OllamaProvider,
    OpenAIProvider,
)
from .response import Response  # noqa: F401
from .api import (
    Loop,
    run,
    arun,
    allow,
    jail,
    mcp,
    providers,
    build_structured_prompt,
    build_structured_reprompt,
)  # noqa: F401
from .capabilities import capabilities_prompt  # noqa: F401

__all__ = [
    "Permission",
    "Response",
    "InnerLoopError",
    "CliExitError",
    "CliNotFoundError",
    "CliTimeoutError",
    # Typed configuration exports
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "LMStudioProvider",
    "LocalMcpServer",
    "RemoteMcpServer",
    # New functional API
    "Loop",
    "run",
    "arun",
    "allow",
    "jail",
    "mcp",
    "providers",
    "build_structured_prompt",
    "build_structured_reprompt",
    "capabilities_prompt",
]
