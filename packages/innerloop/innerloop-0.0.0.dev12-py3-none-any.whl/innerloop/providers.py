"""Typed provider configuration models aligned with OpenCode schema.

These models mirror the JSON structure expected by the OpenCode CLI so a
simple `model_dump_json(by_alias=True)` yields the correct shape.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProviderOptions(BaseModel):
    """Options block serialized under provider[id].options.

    Uses aliases to emit camelCase keys while allowing snake_case initialization.
    Extra keys are allowed to remain forward-compatible with provider SDKs.
    """

    model_config = ConfigDict(extra="allow")

    api_key: str | None = Field(default=None, alias="apiKey", repr=False)
    base_url: str | None = Field(default=None, alias="baseURL")
    timeout: int | None = Field(default=None)


class ProviderConfig(BaseModel):
    """Base configuration for LLM providers.

    - Extra fields (e.g., npm, name, models) are allowed and passed through.
    - The `options` object is explicitly modeled to match OpenCode schema.
    - Pedantic by design: no back-compat magic for flat keys. For ergonomics,
      use the `innerloop.api.providers(...)` helper to build provider maps.
    """

    model_config = ConfigDict(extra="allow")
    options: ProviderOptions = Field(default_factory=ProviderOptions)


class OpenAIProvider(ProviderConfig):
    """Configuration for OpenAI provider."""

    pass


class AnthropicProvider(ProviderConfig):
    """Configuration for Anthropic provider."""

    pass


class OpencodeProvider(ProviderConfig):
    """Configuration for OpenCode provider."""

    pass


class OllamaProvider(ProviderConfig):
    """Configuration for the local Ollama provider."""

    options: ProviderOptions = Field(
        default_factory=lambda: ProviderOptions.model_validate(
            {"baseURL": "http://localhost:11434/v1", "apiKey": "ollama"}
        )
    )


class LMStudioProvider(ProviderConfig):
    """Configuration for the local LM Studio provider."""

    options: ProviderOptions = Field(
        default_factory=lambda: ProviderOptions.model_validate(
            {"baseURL": "http://127.0.0.1:1234/v1", "apiKey": "lm-studio"}
        )
    )


# Typed provider names and class mapping used by the high-level API helpers.
ProviderName = Literal["openai", "anthropic", "opencode", "ollama", "lmstudio"]

PROVIDER_CLASSES: dict[str, type[ProviderConfig]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "opencode": OpencodeProvider,
    "ollama": OllamaProvider,
    "lmstudio": LMStudioProvider,
}
