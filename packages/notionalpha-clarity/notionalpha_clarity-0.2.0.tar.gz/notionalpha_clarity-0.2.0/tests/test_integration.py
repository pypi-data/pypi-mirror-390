"""
Integration Tests for NotionAlpha Clarity Python SDK

Tests the full flow with mocked provider SDKs:
1. Initialize client with provider
2. Make LLM call (mocked at SDK level)
3. Capture transaction ID from response header
4. Track outcome with transaction ID
5. Verify outcome is linked to transaction
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from notionalpha import NotionAlphaClient


# Test configuration
TEST_CONFIG = {
    'org_id': 'org_test123',
    'team_id': '550e8400-e29b-41d4-a716-446655440000',
    'environment': 'production',
    'feature_id': 'feature-test',
    'provider': {
        'type': 'openai',
        'provider_id': '660e8400-e29b-41d4-a716-446655440001',
    }
}

PROXY_BASE_URL = 'https://aiproxy.notionalpha.com/v1'
API_BASE_URL = 'https://api.notionalpha.com'


class TestOpenAIProviderIntegration:
    """Test OpenAI provider integration"""

    @patch('notionalpha.providers.openai.OpenAI')
    @patch('requests.post')
    def test_full_flow_llm_call_capture_transaction_track_outcome(self, mock_post, mock_openai_class):
        """Test complete flow: LLM call → capture transaction ID → track outcome"""
        mock_transaction_id = 'txn_test_12345'
        mock_response_id = 'chatcmpl-test123'

        # Mock OpenAI SDK response
        mock_response = Mock()
        mock_response.id = mock_response_id
        mock_response.choices = [Mock(message=Mock(content='Hello! How can I help you today?'))]
        mock_response.usage = Mock(prompt_tokens=10, completion_tokens=20, total_tokens=30)

        # Mock raw response with headers
        mock_raw_response = Mock()
        mock_raw_response.headers = {'X-NotionAlpha-Transaction-Id': mock_transaction_id}
        mock_raw_response.parse = Mock(return_value=mock_response)

        # Setup OpenAI client mock
        mock_client = Mock()
        mock_client.chat.completions.with_raw_response.create = Mock(return_value=mock_raw_response)
        mock_openai_class.return_value = mock_client

        # Mock outcome tracking response
        mock_post.return_value = Mock(
            ok=True,
            json=Mock(return_value={
                'success': True,
                'outcomeId': 'outcome_test_123',
                'transactionId': mock_transaction_id,
            })
        )

        # Initialize client
        client = NotionAlphaClient(**TEST_CONFIG)

        # Make LLM call
        response, transaction_id = client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': 'Hello!'}]
        )

        # Verify response
        assert response is not None
        assert response.id == mock_response_id
        assert response.choices[0].message.content == 'Hello! How can I help you today?'

        # Verify transaction ID was captured
        assert transaction_id == mock_transaction_id

        # Track outcome
        outcome_result = client.track_outcome(
            transaction_id=transaction_id,
            type='customer_support_ticket_resolved',
            metadata={
                'feedback': 'Great response!',
                'satisfactionScore': 95,
            }
        )

        # Verify outcome was tracked
        assert outcome_result['success'] is True
        assert outcome_result['transactionId'] == mock_transaction_id
    
    @patch('notionalpha.providers.openai.OpenAI')
    def test_missing_transaction_id_header_fallback(self, mock_openai_class):
        """Test handling of missing transaction ID header (fallback to 'unknown')"""
        mock_response_id = 'chatcmpl-test456'

        # Mock OpenAI SDK response
        mock_response = Mock()
        mock_response.id = mock_response_id
        mock_response.choices = [Mock(message=Mock(content='Response without transaction ID'))]

        # Mock raw response WITHOUT transaction ID header
        mock_raw_response = Mock()
        mock_raw_response.headers = {}  # No transaction ID header
        mock_raw_response.parse = Mock(return_value=mock_response)

        # Setup OpenAI client mock
        mock_client = Mock()
        mock_client.chat.completions.with_raw_response.create = Mock(return_value=mock_raw_response)
        mock_openai_class.return_value = mock_client

        client = NotionAlphaClient(**TEST_CONFIG)
        response, transaction_id = client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': 'Test'}]
        )

        # Should fallback to 'unknown' when header is missing
        assert transaction_id == 'unknown'

    @patch('notionalpha.providers.openai.OpenAI')
    def test_api_error_handling(self, mock_openai_class):
        """Test proper handling of API errors"""
        # Setup OpenAI client mock to raise exception
        mock_client = Mock()
        mock_client.chat.completions.with_raw_response.create = Mock(
            side_effect=Exception("Invalid API key")
        )
        mock_openai_class.return_value = mock_client

        client = NotionAlphaClient(**TEST_CONFIG)

        with pytest.raises(Exception):  # Should raise ProviderError
            client.chat.completions.create(
                model='gpt-4',
                messages=[{'role': 'user', 'content': 'Test'}]
            )


class TestAnthropicProviderIntegration:
    """Test Anthropic provider integration"""

    @patch('notionalpha.providers.anthropic.Anthropic')
    def test_full_flow_with_anthropic_provider(self, mock_anthropic_class):
        """Test complete flow with Anthropic provider"""
        mock_transaction_id = 'txn_anthropic_12345'
        mock_message_id = 'msg_test123'

        anthropic_config = {
            **TEST_CONFIG,
            'provider': {
                'type': 'anthropic',
                'provider_id': '770e8400-e29b-41d4-a716-446655440002',
            }
        }

        # Mock Anthropic SDK response
        mock_content = Mock()
        mock_content.text = 'Hello from Claude!'
        mock_response = Mock()
        mock_response.id = mock_message_id
        mock_response.content = [mock_content]

        # Mock raw response with headers
        mock_raw_response = Mock()
        mock_raw_response.headers = {'X-NotionAlpha-Transaction-Id': mock_transaction_id}
        mock_raw_response.parse = Mock(return_value=mock_response)

        # Setup Anthropic client mock
        mock_client = Mock()
        mock_client.messages.with_raw_response.create = Mock(return_value=mock_raw_response)
        mock_anthropic_class.return_value = mock_client

        client = NotionAlphaClient(**anthropic_config)
        response, transaction_id = client.messages.create(
            model='claude-3-opus-20240229',
            max_tokens=1024,
            messages=[{'role': 'user', 'content': 'Hello!'}]
        )

        assert response.id == mock_message_id
        assert transaction_id == mock_transaction_id
        assert response.content[0].text == 'Hello from Claude!'


class TestOutcomeTracking:
    """Test outcome tracking functionality"""

    @patch('requests.post')
    def test_track_outcome_without_transaction_id_fuzzy_matching(self, mock_post):
        """Test tracking outcome without transaction ID (fuzzy matching)"""
        # Mock outcome tracking response
        mock_post.return_value = Mock(
            ok=True,
            json=Mock(return_value={
                'success': True,
                'outcomeId': 'outcome_fuzzy_123',
                'matched': 'fuzzy',
                'transactionId': None,
            })
        )

        client = NotionAlphaClient(**TEST_CONFIG)

        result = client.track_outcome(
            transaction_id=None,  # No transaction ID - fuzzy matching
            type='revenue_generated',
            metadata={
                'amount': 100,
                'timestamp': '2024-01-01T00:00:00Z',
            }
        )

        assert result['success'] is True
        assert result['matched'] == 'fuzzy'

