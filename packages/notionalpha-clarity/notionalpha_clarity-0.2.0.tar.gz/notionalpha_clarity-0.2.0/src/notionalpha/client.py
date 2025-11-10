"""
NotionAlpha Clarity Client

Main client for interacting with NotionAlpha Clarity platform
"""

from typing import Any, Dict, Optional, Tuple
from datetime import datetime
import requests

from .types import (
    ClarityConfig,
    ProviderConfig,
    OutcomePayload,
    ValueRealizationSummary,
    ConfigurationError,
    APIError,
    ProviderError,
)


class NotionAlphaClient:
    """
    Main NotionAlpha Clarity client
    
    Example:
        >>> from notionalpha import NotionAlphaClient
        >>> 
        >>> clarity = NotionAlphaClient(
        ...     org_id='org_xxx',
        ...     team_id='team-uuid',
        ...     provider={'type': 'openai', 'provider_id': 'provider-uuid'}
        ... )
        >>> 
        >>> # Make LLM call (FinOps + Security automatic)
        >>> response, transaction_id = clarity.chat.completions.create(
        ...     model='gpt-4o-mini',
        ...     messages=[{'role': 'user', 'content': 'Help'}]
        ... )
        >>> 
        >>> # Track outcome (one line)
        >>> clarity.track_outcome(
        ...     transaction_id=transaction_id,
        ...     type='customer_support',
        ...     metadata={'time_saved_minutes': 15}
        ... )
    """
    
    def __init__(
        self,
        org_id: str,
        team_id: str,
        provider: ProviderConfig,
        environment: str = 'production',
        feature_id: Optional[str] = None,
        api_base_url: str = 'https://api.notionalpha.com',
        proxy_base_url: str = 'https://aiproxy.notionalpha.com',
    ):
        """
        Initialize NotionAlpha Clarity client
        
        Args:
            org_id: Organization ID from NotionAlpha dashboard
            team_id: Team ID for cost attribution
            provider: Provider configuration
            environment: Environment name (default: 'production')
            feature_id: Optional feature ID for granular tracking
            api_base_url: Base URL for NotionAlpha API
            proxy_base_url: Base URL for NotionAlpha proxy
        """
        if not org_id:
            raise ConfigurationError('org_id is required')
        if not team_id:
            raise ConfigurationError('team_id is required')
        if not provider:
            raise ConfigurationError('provider is required')
        
        self.org_id = org_id
        self.team_id = team_id
        self.environment = environment
        self.feature_id = feature_id
        self.provider = provider
        self.api_base_url = api_base_url.rstrip('/')
        self.proxy_base_url = proxy_base_url.rstrip('/')
        
        # Initialize provider-specific client
        self._init_provider()
    
    def _init_provider(self) -> None:
        """Initialize provider-specific client"""
        provider_type = self.provider.get('type')

        try:
            if provider_type == 'openai':
                from .providers.openai import OpenAIProvider
                self._provider = OpenAIProvider(
                    provider_id=self.provider['provider_id'],
                    org_id=self.org_id,
                    team_id=self.team_id,
                    environment=self.environment,
                    feature_id=self.feature_id,
                    proxy_base_url=self.proxy_base_url,
                )
            elif provider_type == 'anthropic':
                from .providers.anthropic import AnthropicProvider
                self._provider = AnthropicProvider(
                    provider_id=self.provider['provider_id'],
                    org_id=self.org_id,
                    team_id=self.team_id,
                    environment=self.environment,
                    feature_id=self.feature_id,
                    proxy_base_url=self.proxy_base_url,
                )
            elif provider_type == 'azure-openai':
                from .providers.azure_openai import AzureOpenAIProvider
                self._provider = AzureOpenAIProvider(
                    provider_id=self.provider['provider_id'],
                    deployment_name=self.provider['deployment_name'],
                    org_id=self.org_id,
                    team_id=self.team_id,
                    environment=self.environment,
                    feature_id=self.feature_id,
                    proxy_base_url=self.proxy_base_url,
                    resource_name=self.provider.get('resource_name'),
                )
            else:
                raise ConfigurationError(f'Unsupported provider type: {provider_type}')
        except ImportError as e:
            raise ConfigurationError(
                f'Failed to import provider {provider_type}. '
                f'Make sure the required SDK is installed: {str(e)}'
            )
    
    @property
    def chat(self):
        """Access chat completions (OpenAI/Azure OpenAI)"""
        if not hasattr(self._provider, 'chat'):
            raise ProviderError(f'Provider {self.provider["type"]} does not support chat completions')
        return self._provider.chat
    
    @property
    def messages(self):
        """Access messages (Anthropic)"""
        if not hasattr(self._provider, 'messages'):
            raise ProviderError(f'Provider {self.provider["type"]} does not support messages')
        return self._provider.messages
    
    def track_outcome(
        self,
        transaction_id: Optional[str] = None,
        type: str = 'custom',
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Track a business outcome
        
        Args:
            transaction_id: Transaction ID from LLM response (for exact matching)
            type: Outcome type (e.g., 'customer_support', 'code_generation')
            metadata: Outcome-specific metadata
            timestamp: Optional timestamp (defaults to now)
        
        Returns:
            API response with outcome ID and matching details
        
        Raises:
            APIError: If API request fails
        """
        if metadata is None:
            metadata = {}
        
        payload = {
            'type': type,
            'metadata': metadata,
        }
        
        if transaction_id:
            payload['transactionId'] = transaction_id
        
        if timestamp:
            payload['timestamp'] = timestamp.isoformat()
        
        try:
            response = requests.post(
                f'{self.api_base_url}/api/outcomes',
                headers={
                    'Content-Type': 'application/json',
                    'X-Org-ID': self.org_id,
                    'X-Team-ID': self.team_id,
                    'X-Environment': self.environment,
                },
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise APIError(
                f'Failed to track outcome: {e.response.text}',
                e.response.status_code,
                e.response.json() if e.response.text else None
            )
        except requests.RequestException as e:
            raise APIError(f'Failed to track outcome: {str(e)}', 500)
    
    def get_value_realization(self) -> ValueRealizationSummary:
        """
        Get value realization summary
        
        Returns:
            Value realization summary with cost, value, ROI, etc.
        
        Raises:
            APIError: If API request fails
        """
        try:
            response = requests.get(
                f'{self.api_base_url}/api/value-realization',
                headers={
                    'X-Org-ID': self.org_id,
                    'X-Team-ID': self.team_id,
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            raise APIError(
                f'Failed to get value realization: {e.response.text}',
                e.response.status_code,
                e.response.json() if e.response.text else None
            )
        except requests.RequestException as e:
            raise APIError(f'Failed to get value realization: {str(e)}', 500)

