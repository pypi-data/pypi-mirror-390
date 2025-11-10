"""
NotionAlpha Clarity SDK Types

Core type definitions for the Python SDK
"""

from typing import Any, Dict, Literal, Optional, TypedDict, Union
from datetime import datetime


class OpenAIProviderConfig(TypedDict):
    """OpenAI provider configuration"""
    type: Literal['openai']
    provider_id: str


class AnthropicProviderConfig(TypedDict):
    """Anthropic provider configuration"""
    type: Literal['anthropic']
    provider_id: str


class AzureOpenAIProviderConfig(TypedDict):
    """Azure OpenAI provider configuration"""
    type: Literal['azure-openai']
    provider_id: str
    deployment_name: str


ProviderConfig = Union[OpenAIProviderConfig, AnthropicProviderConfig, AzureOpenAIProviderConfig]


class ClarityConfig(TypedDict, total=False):
    """Configuration for NotionAlpha Clarity client"""
    org_id: str  # Required
    team_id: str  # Required
    environment: str  # Optional, default: 'production'
    feature_id: Optional[str]  # Optional
    provider: ProviderConfig  # Required
    api_base_url: str  # Optional, default: 'https://api.notionalpha.com'
    proxy_base_url: str  # Optional, default: 'https://aiproxy.notionalpha.com'


class ClarityLLMResponse(TypedDict):
    """Response from LLM call with transaction ID"""
    response: Any  # Original provider response
    transaction_id: str  # Transaction ID for linking outcomes
    cost: Optional[Dict[str, Any]]  # Cost information if available


OutcomeType = Literal[
    'customer_support',
    'code_generation',
    'content_creation',
    'sales_marketing',
    'custom'
]


class OutcomePayload(TypedDict, total=False):
    """Outcome tracking payload"""
    transaction_id: Optional[str]  # Transaction ID from LLM response
    type: Union[OutcomeType, str]  # Outcome type
    metadata: Dict[str, Any]  # Outcome metadata
    timestamp: Optional[datetime]  # Optional timestamp


class ValueRealizationSummary(TypedDict):
    """Value realization summary"""
    total_cost: float
    total_value: float
    roi: float
    outcome_count: int
    transaction_count: int
    period_start: str
    period_end: str


# Error types
class ClarityError(Exception):
    """Base exception for Clarity SDK"""
    def __init__(
        self,
        message: str,
        code: str,
        status_code: Optional[int] = None,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.details = details


class ConfigurationError(ClarityError):
    """Configuration error"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, 'CONFIGURATION_ERROR', None, details)


class APIError(ClarityError):
    """API error"""
    def __init__(
        self,
        message: str,
        status_code: int,
        details: Optional[Any] = None
    ):
        super().__init__(message, 'API_ERROR', status_code, details)


class ProviderError(ClarityError):
    """Provider error"""
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(message, 'PROVIDER_ERROR', None, details)

