"""
NotionAlpha Clarity Python SDK

Unified SDK for AI Value Realization Platform
"""

from .client import NotionAlphaClient
from .types import (
    ClarityConfig,
    ProviderConfig,
    OpenAIProviderConfig,
    AnthropicProviderConfig,
    AzureOpenAIProviderConfig,
    ClarityLLMResponse,
    OutcomePayload,
    OutcomeType,
    ValueRealizationSummary,
    ClarityError,
    ConfigurationError,
    APIError,
    ProviderError,
)
from .signal_analyzer import (
    SignalAnalyzer,
    SignalAnalyzerConfig,
    SignalData,
    SignalAnalysis,
)

__version__ = "0.2.0"

__all__ = [
    "NotionAlphaClient",
    "ClarityConfig",
    "ProviderConfig",
    "OpenAIProviderConfig",
    "AnthropicProviderConfig",
    "AzureOpenAIProviderConfig",
    "ClarityLLMResponse",
    "OutcomePayload",
    "OutcomeType",
    "ValueRealizationSummary",
    "ClarityError",
    "ConfigurationError",
    "APIError",
    "ProviderError",
    "SignalAnalyzer",
    "SignalAnalyzerConfig",
    "SignalData",
    "SignalAnalysis",
]

