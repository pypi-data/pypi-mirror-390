"""
Anthropic Provider Wrapper

Wraps Anthropic SDK to route through NotionAlpha proxy
Automatically captures transaction IDs for outcome tracking
Captures signals with enrichment for agent intelligence (T198)
"""

import asyncio
import json
from typing import Any, Dict, Optional, Tuple
from anthropic import Anthropic
from anthropic.types import Message
import httpx

from ..types import ProviderError
from ..signal_analyzer import SignalAnalyzer, SignalAnalyzerConfig


class AnthropicProvider:
    """
    Anthropic provider wrapper
    
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

        # Initialize Anthropic client with NotionAlpha proxy
        default_headers = {
            'X-Org-ID': org_id,
            'X-Team-ID': team_id,
            'X-Environment': environment,
        }

        if feature_id:
            default_headers['X-Feature-ID'] = feature_id

        self.client = Anthropic(
            base_url=f'{proxy_base_url}/v1/{provider_id}',
            api_key='dummy-key',  # Not used (credentials stored in NotionAlpha)
            default_headers=default_headers,
        )

    async def _capture_signal(
        self,
        transaction_id: str,
        messages: list,
        model: str,
        response: Message
    ) -> None:
        """
        Capture signal with enrichment (T198)
        Called after successful LLM completion
        """
        # Only capture if signal analyzer is configured
        if not self.signal_analyzer:
            return

        try:
            # Extract prompt from messages (Anthropic format)
            prompt = '\n'.join([
                f"{m.get('role', 'unknown')}: {self._extract_content(m.get('content', ''))}"
                for m in messages
            ])

            # Extract response content (Anthropic message format with content blocks)
            response_content = ''
            if response.content and len(response.content) > 0:
                # Anthropic responses have content as list of ContentBlock objects
                response_content = '\n'.join([
                    block.text if hasattr(block, 'text') else str(block)
                    for block in response.content
                ])

            # Analyze signal with enrichment
            analysis = await self.signal_analyzer.analyze({
                'prompt': prompt,
                'response': response_content,
                'model': model,
                'input_tokens': response.usage.input_tokens if response.usage else None,
                'output_tokens': response.usage.output_tokens if response.usage else None,
                'processing_time_ms': None,  # Not available from Anthropic response
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
                    'provider': 'anthropic',
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
            print(f'[Anthropic Provider] Signal capture failed: {e}')
            # Don't propagate error - signal capture is best-effort

    def _extract_content(self, content) -> str:
        """
        Extract text content from Anthropic message content
        Handles both string and list of content blocks
        """
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return '\n'.join([
                block.get('text', str(block)) if isinstance(block, dict)
                else block.text if hasattr(block, 'text')
                else str(block)
                for block in content
            ])
        return str(content)

    @property
    def messages(self):
        """Access messages interface"""
        return Messages(self.client, self)


class Messages:
    """Messages interface wrapper"""

    def __init__(self, client: Anthropic, provider: 'AnthropicProvider'):
        self.client = client
        self.provider = provider
    
    def create(self, **kwargs: Any) -> Tuple[Message, str]:
        """
        Create message

        Args:
            **kwargs: Arguments to pass to Anthropic messages.create()

        Returns:
            Tuple of (response, transaction_id)

        Raises:
            ProviderError: If request fails

        Example:
            >>> response, transaction_id = clarity.messages.create(
            ...     model='claude-3-5-sonnet-20241022',
            ...     max_tokens=1024,
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
            raw_response = self.client.messages.with_raw_response.create(**kwargs)

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
            raise ProviderError(f'Anthropic request failed: {str(e)}', details=str(e))

