"""
OpenAI Provider Wrapper

Wraps OpenAI SDK to route through NotionAlpha proxy
Automatically captures transaction IDs for outcome tracking
Captures signals with enrichment for agent intelligence (T198)
"""

import asyncio
import json
from typing import Any, Dict, Optional, Tuple
from openai import OpenAI
from openai.types.chat import ChatCompletion
import httpx

from ..types import ProviderError
from ..signal_analyzer import SignalAnalyzer, SignalAnalyzerConfig


class OpenAIProvider:
    """
    OpenAI provider wrapper
    
    Routes requests through NotionAlpha proxy for:
    - Automatic cost tracking (FinOps)
    - Security detection (threats, PII, etc.)
    - Transaction ID capture for outcome linking
    """
    
    def __init__(
        self,
        provider_id: str,
        org_id: str,
        team_id: str,
        environment: str,
        feature_id: Optional[str],
        proxy_base_url: str,
        signal_enrichment: Optional[SignalAnalyzerConfig] = None,
        signal_capture_url: Optional[str] = None,
    ):
        self.provider_id = provider_id
        self.org_id = org_id
        self.team_id = team_id
        self.environment = environment
        self.feature_id = feature_id
        self.proxy_base_url = proxy_base_url

        # Initialize signal analyzer if enrichment configured (T198)
        self.signal_analyzer = SignalAnalyzer(signal_enrichment) if signal_enrichment else None

        # Signal capture URL defaults to backend API
        self.signal_capture_url = signal_capture_url or f'{proxy_base_url}/api/v1/signals'

        # Initialize OpenAI client with NotionAlpha proxy
        default_headers = {
            'X-Org-ID': org_id,
            'X-Team-ID': team_id,
            'X-Environment': environment,
        }

        if feature_id:
            default_headers['X-Feature-ID'] = feature_id

        self.client = OpenAI(
            base_url=f'{proxy_base_url}/v1/{provider_id}',
            api_key='dummy-key',  # Not used (credentials stored in NotionAlpha)
            default_headers=default_headers,
        )
    
    async def _capture_signal(
        self,
        transaction_id: str,
        messages: list,
        model: str,
        response: ChatCompletion
    ) -> None:
        """
        Capture signal with enrichment (T198)
        Called after successful LLM completion
        """
        # Only capture if signal analyzer is configured
        if not self.signal_analyzer:
            return

        try:
            # Extract prompt and response content
            prompt = '\n'.join([
                f"{m.get('role', 'unknown')}: {m.get('content', '')}"
                for m in messages
            ])

            response_content = ''
            if response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if choice.message and choice.message.content:
                    response_content = choice.message.content

            # Analyze signal with enrichment
            analysis = await self.signal_analyzer.analyze({
                'prompt': prompt,
                'response': response_content,
                'model': model,
                'input_tokens': response.usage.prompt_tokens if response.usage else None,
                'output_tokens': response.usage.completion_tokens if response.usage else None,
                'processing_time_ms': None,  # Not available from OpenAI response
            })

            # POST signal to backend
            signal_payload = {
                'orgId': self.org_id,
                'teamId': self.team_id,
                'transactionId': transaction_id,
                'signalType': 'llm_completion',
                'contextClassification': analysis['context_classification'],
                'intentAnalysis': analysis['intent_analysis'],
                'complexityScore': analysis['complexity_score'],
                'estimatedValueCategory': analysis['estimated_value_category'],
                'queryType': analysis['query_type'],
                'promptLength': len(prompt),
                'responseLength': len(response_content),
                'featureId': self.feature_id,
                'metadata': {
                    'model': model,
                    'provider': 'openai',
                    'environment': self.environment,
                },
            }

            async with httpx.AsyncClient() as client:
                await client.post(
                    self.signal_capture_url,
                    headers={'Content-Type': 'application/json'},
                    json=signal_payload,
                    timeout=10.0
                )

            # Silent failure - don't throw if signal capture fails
        except Exception as e:
            print(f'[OpenAI Provider] Signal capture failed: {e}')
            # Don't propagate error - signal capture is best-effort

    @property
    def chat(self):
        """Access chat completions interface"""
        return ChatCompletions(self.client, self)


class ChatCompletions:
    """Chat completions interface wrapper"""

    def __init__(self, client: OpenAI, provider: 'OpenAIProvider'):
        self.client = client
        self.provider = provider

    @property
    def completions(self):
        """Access completions interface"""
        return Completions(self.client, self.provider)


class Completions:
    """Completions interface wrapper"""

    def __init__(self, client: OpenAI, provider: 'OpenAIProvider'):
        self.client = client
        self.provider = provider

    def create(self, **kwargs: Any) -> Tuple[ChatCompletion, str]:
        """
        Create chat completion

        Args:
            **kwargs: Arguments to pass to OpenAI chat.completions.create()

        Returns:
            Tuple of (response, transaction_id)

        Raises:
            ProviderError: If request fails

        Example:
            >>> response, transaction_id = clarity.chat.completions.create(
            ...     model='gpt-4o-mini',
            ...     messages=[{'role': 'user', 'content': 'Hello!'}]
            ... )
            >>>
            >>> # Use transactionId for outcome tracking
            >>> clarity.track_outcome(
            ...     transaction_id=transaction_id,
            ...     type='customer_support',
            ...     metadata={'time_saved_minutes': 15}
            ... )
        """
        try:
            # Make request through proxy and get raw response with headers
            raw_response = self.client.chat.completions.with_raw_response.create(**kwargs)

            # Extract transaction ID from NotionAlpha proxy response header
            transaction_id = (
                raw_response.headers.get('X-NotionAlpha-Transaction-Id') or
                raw_response.headers.get('x-notionalpha-transaction-id') or  # lowercase fallback
                'unknown'
            )

            # Parse the actual response object
            response = raw_response.parse()

            # Capture signal asynchronously (fire and forget)
            if self.provider.signal_analyzer:
                messages = kwargs.get('messages', [])
                model = kwargs.get('model', 'unknown')
                # Run async capture in background
                asyncio.create_task(
                    self.provider._capture_signal(transaction_id, messages, model, response)
                )

            return response, transaction_id

        except Exception as e:
            raise ProviderError(f'OpenAI request failed: {str(e)}', details=str(e))

