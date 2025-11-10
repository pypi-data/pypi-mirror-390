"""
Tests for NotionAlphaClient
"""

import pytest
from notionalpha import NotionAlphaClient
from notionalpha.types import ConfigurationError


class TestNotionAlphaClient:
    """Test NotionAlphaClient initialization and configuration"""
    
    def test_init_with_valid_config(self):
        """Test client initialization with valid configuration"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            provider={'type': 'openai', 'provider_id': 'provider-123'}
        )
        
        assert client.org_id == 'org_test123'
        assert client.team_id == 'team-uuid-123'
        assert client.environment == 'production'
        assert client.provider['type'] == 'openai'
    
    def test_init_with_custom_environment(self):
        """Test client initialization with custom environment"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            environment='staging',
            provider={'type': 'openai', 'provider_id': 'provider-123'}
        )
        
        assert client.environment == 'staging'
    
    def test_init_with_feature_id(self):
        """Test client initialization with feature ID"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            feature_id='test-feature',
            provider={'type': 'openai', 'provider_id': 'provider-123'}
        )
        
        assert client.feature_id == 'test-feature'
    
    def test_init_missing_org_id(self):
        """Test client initialization fails without org_id"""
        with pytest.raises(ConfigurationError, match='org_id is required'):
            NotionAlphaClient(
                org_id='',
                team_id='team-uuid-123',
                provider={'type': 'openai', 'provider_id': 'provider-123'}
            )
    
    def test_init_missing_team_id(self):
        """Test client initialization fails without team_id"""
        with pytest.raises(ConfigurationError, match='team_id is required'):
            NotionAlphaClient(
                org_id='org_test123',
                team_id='',
                provider={'type': 'openai', 'provider_id': 'provider-123'}
            )
    
    def test_init_missing_provider(self):
        """Test client initialization fails without provider"""
        with pytest.raises(ConfigurationError, match='provider is required'):
            NotionAlphaClient(
                org_id='org_test123',
                team_id='team-uuid-123',
                provider=None
            )
    
    def test_init_unsupported_provider(self):
        """Test client initialization fails with unsupported provider"""
        with pytest.raises(ConfigurationError, match='Unsupported provider type'):
            NotionAlphaClient(
                org_id='org_test123',
                team_id='team-uuid-123',
                provider={'type': 'unsupported', 'provider_id': 'provider-123'}
            )
    
    def test_openai_provider_initialization(self):
        """Test OpenAI provider is initialized correctly"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            provider={'type': 'openai', 'provider_id': 'provider-123'}
        )
        
        assert hasattr(client, 'chat')
        assert client.chat is not None
    
    def test_anthropic_provider_initialization(self):
        """Test Anthropic provider is initialized correctly"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            provider={'type': 'anthropic', 'provider_id': 'provider-123'}
        )
        
        assert hasattr(client, 'messages')
        assert client.messages is not None
    
    def test_azure_openai_provider_initialization(self):
        """Test Azure OpenAI provider is initialized correctly"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            provider={
                'type': 'azure-openai',
                'provider_id': 'provider-123',
                'deployment_name': 'gpt-4o-mini'
            }
        )

        assert hasattr(client, 'chat')
        assert client.chat is not None

    def test_azure_openai_provider_with_resource_name_legacy(self):
        """Test Azure OpenAI provider with resource name (legacy format)"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            provider={
                'type': 'azure-openai',
                'provider_id': 'provider-123',
                'deployment_name': 'gpt-4o-mini',
                'resource_name': 'my-azure-resource'
            }
        )

        assert hasattr(client, 'chat')
        assert client.chat is not None

    def test_azure_openai_provider_with_ai_foundry_hostname(self):
        """Test Azure OpenAI provider with AI Foundry hostname"""
        client = NotionAlphaClient(
            org_id='org_test123',
            team_id='team-uuid-123',
            provider={
                'type': 'azure-openai',
                'provider_id': 'provider-123',
                'deployment_name': 'gpt-4o-mini',
                'resource_name': 'myproject.services.ai.azure.com'
            }
        )

        assert hasattr(client, 'chat')
        assert client.chat is not None

