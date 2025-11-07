"""
Comprehensive tests for AutoBranch feature
Tests all scenarios including:
- Basic suggest_branches functionality
- analyze_text alias
- Health check
- Error handling
- Parameter validation
- Different detection modes
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from chatroutes import ChatRoutes
from chatroutes.resources.autobranch import AutoBranchResource


class TestAutoBranchResource:
    """Test suite for AutoBranch resource"""

    @pytest.fixture
    def client(self):
        """Create a ChatRoutes client for testing"""
        return ChatRoutes(api_key='test_api_key')

    @pytest.fixture
    def autobranch_resource(self, client):
        """Create an AutoBranch resource for testing"""
        return client.autobranch

    # ===== Basic Functionality Tests =====

    @patch('requests.post')
    def test_suggest_branches_basic(self, mock_post, autobranch_resource):
        """Test basic suggest_branches functionality"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [
                {
                    'id': 'branch-1',
                    'title': 'Product Question',
                    'description': 'User is asking about product features',
                    'triggerText': 'product features',
                    'branchPoint': {'start': 0, 'end': 15},
                    'confidence': 0.85,
                    'reasoning': 'Product-related query detected',
                    'estimatedDivergence': 'medium'
                }
            ],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 1,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test
        result = autobranch_resource.suggest_branches(
            text="Tell me about product features",
            suggestions_count=3
        )

        # Assertions
        assert result is not None
        assert 'suggestions' in result
        assert len(result['suggestions']) == 1
        assert result['suggestions'][0]['title'] == 'Product Question'
        assert result['metadata']['detectionMethod'] == 'pattern'

        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['text'] == "Tell me about product features"
        assert call_args[1]['json']['suggestionsCount'] == 3
        assert call_args[1]['headers']['Authorization'] == 'ApiKey test_api_key'

    @patch('requests.post')
    def test_suggest_branches_with_all_parameters(self, mock_post, autobranch_resource):
        """Test suggest_branches with all optional parameters"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [],
            'metadata': {
                'detectionMethod': 'hybrid',
                'totalBranchPointsFound': 0,
                'modelUsed': 'gpt-4'
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test with all parameters
        result = autobranch_resource.suggest_branches(
            text="Complex user query",
            suggestions_count=5,
            hybrid_detection=True,
            threshold=0.8,
            llm_model='gpt-4',
            llm_provider='openai',
            llm_api_key='sk-test-key'
        )

        # Assertions
        assert result is not None
        assert result['metadata']['detectionMethod'] == 'hybrid'
        assert result['metadata']['modelUsed'] == 'gpt-4'

        # Verify all parameters were sent
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        assert json_data['text'] == "Complex user query"
        assert json_data['suggestionsCount'] == 5
        assert json_data['hybridDetection'] is True
        assert json_data['threshold'] == 0.8
        assert json_data['llmModel'] == 'gpt-4'
        assert json_data['llmProvider'] == 'openai'
        assert json_data['llmApiKey'] == 'sk-test-key'

    @patch('requests.post')
    def test_suggest_branches_hybrid_detection(self, mock_post, autobranch_resource):
        """Test suggest_branches with hybrid detection enabled"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [
                {
                    'id': 'branch-1',
                    'title': 'Technical Support',
                    'description': 'User needs technical assistance',
                    'triggerText': 'technical issue',
                    'branchPoint': {'start': 10, 'end': 25},
                    'confidence': 0.92,
                    'reasoning': 'LLM detected technical support need',
                    'estimatedDivergence': 'high'
                }
            ],
            'metadata': {
                'detectionMethod': 'hybrid',
                'totalBranchPointsFound': 1,
                'modelUsed': 'gpt-4'
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = autobranch_resource.suggest_branches(
            text="I have a technical issue with my account",
            hybrid_detection=True,
            llm_model='gpt-4'
        )

        assert result['metadata']['detectionMethod'] == 'hybrid'
        assert result['metadata']['modelUsed'] == 'gpt-4'
        assert len(result['suggestions']) == 1

    @patch('requests.post')
    def test_analyze_text_alias(self, mock_post, autobranch_resource):
        """Test analyze_text method (alias for suggest_branches)"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 0,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Test analyze_text
        result = autobranch_resource.analyze_text(
            text="Sample text",
            suggestions_count=2
        )

        assert result is not None
        mock_post.assert_called_once()

    # ===== Health Check Tests =====

    @patch('requests.get')
    def test_health_check_success(self, mock_get, autobranch_resource):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'status': 'healthy',
            'version': '1.0.0',
            'service': 'autobranch'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = autobranch_resource.health()

        assert result['status'] == 'healthy'
        assert result['version'] == '1.0.0'
        assert result['service'] == 'autobranch'

        # Verify correct endpoint was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert '/health' in call_args[0][0]

    # ===== Error Handling Tests =====

    @patch('requests.post')
    def test_suggest_branches_network_error(self, mock_post, autobranch_resource):
        """Test handling of network errors"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(Exception) as exc_info:
            autobranch_resource.suggest_branches(text="Test text")

        assert "AutoBranch request failed" in str(exc_info.value)

    @patch('requests.post')
    def test_suggest_branches_timeout_error(self, mock_post, autobranch_resource):
        """Test handling of timeout errors"""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        with pytest.raises(Exception) as exc_info:
            autobranch_resource.suggest_branches(text="Test text")

        assert "AutoBranch request failed" in str(exc_info.value)

    @patch('requests.post')
    def test_suggest_branches_http_error(self, mock_post, autobranch_resource):
        """Test handling of HTTP errors"""
        import requests
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_post.return_value = mock_response

        with pytest.raises(Exception) as exc_info:
            autobranch_resource.suggest_branches(text="Test text")

        assert "AutoBranch request failed" in str(exc_info.value)

    @patch('requests.get')
    def test_health_check_error(self, mock_get, autobranch_resource):
        """Test health check failure"""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("Service unavailable")

        with pytest.raises(Exception) as exc_info:
            autobranch_resource.health()

        assert "AutoBranch health check failed" in str(exc_info.value)

    # ===== Configuration Tests =====

    def test_default_base_url(self, client):
        """Test default AutoBranch base URL"""
        assert client.autobranch._base_url == "http://autobranch.chatroutes.internal:8000"

    def test_custom_base_url(self):
        """Test custom AutoBranch base URL"""
        client = ChatRoutes(
            api_key='test_key',
            autobranch_base_url='http://custom.autobranch.url:9000'
        )
        assert client.autobranch._base_url == 'http://custom.autobranch.url:9000'

    # ===== Response Structure Tests =====

    @patch('requests.post')
    def test_multiple_suggestions(self, mock_post, autobranch_resource):
        """Test response with multiple branch suggestions"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [
                {
                    'id': 'branch-1',
                    'title': 'Sales Inquiry',
                    'description': 'Customer wants pricing information',
                    'triggerText': 'pricing',
                    'branchPoint': {'start': 0, 'end': 7},
                    'confidence': 0.9,
                    'reasoning': 'Pricing keyword detected',
                    'estimatedDivergence': 'low'
                },
                {
                    'id': 'branch-2',
                    'title': 'Technical Support',
                    'description': 'Customer needs technical help',
                    'triggerText': 'technical',
                    'branchPoint': {'start': 20, 'end': 29},
                    'confidence': 0.85,
                    'reasoning': 'Technical keyword detected',
                    'estimatedDivergence': 'medium'
                },
                {
                    'id': 'branch-3',
                    'title': 'General Question',
                    'description': 'General inquiry',
                    'triggerText': 'question',
                    'branchPoint': {'start': 40, 'end': 48},
                    'confidence': 0.75,
                    'reasoning': 'Question pattern detected',
                    'estimatedDivergence': 'high'
                }
            ],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 3,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = autobranch_resource.suggest_branches(
            text="pricing and technical question",
            suggestions_count=3
        )

        assert len(result['suggestions']) == 3
        assert result['metadata']['totalBranchPointsFound'] == 3
        assert all('confidence' in s for s in result['suggestions'])
        assert all('branchPoint' in s for s in result['suggestions'])

    @patch('requests.post')
    def test_no_suggestions_found(self, mock_post, autobranch_resource):
        """Test response when no branch points are found"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 0,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = autobranch_resource.suggest_branches(text="simple greeting")

        assert len(result['suggestions']) == 0
        assert result['metadata']['totalBranchPointsFound'] == 0

    # ===== Different Threshold Tests =====

    @patch('requests.post')
    def test_high_threshold(self, mock_post, autobranch_resource):
        """Test with high confidence threshold"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [
                {
                    'id': 'branch-1',
                    'title': 'High Confidence Branch',
                    'description': 'Very clear branch point',
                    'triggerText': 'urgent issue',
                    'branchPoint': {'start': 0, 'end': 11},
                    'confidence': 0.95,
                    'reasoning': 'Strong signal detected',
                    'estimatedDivergence': 'high'
                }
            ],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 1,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = autobranch_resource.suggest_branches(
            text="urgent issue needs attention",
            threshold=0.9
        )

        assert len(result['suggestions']) == 1
        assert result['suggestions'][0]['confidence'] >= 0.9

    # ===== Integration Tests =====

    def test_autobranch_resource_initialization(self, client):
        """Test that AutoBranch resource is properly initialized"""
        assert hasattr(client, 'autobranch')
        assert isinstance(client.autobranch, AutoBranchResource)
        assert client.autobranch._client == client

    @patch('requests.post')
    def test_api_key_propagation(self, mock_post, client):
        """Test that API key is properly passed to AutoBranch requests"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 0,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client.autobranch.suggest_branches(text="test")

        call_args = mock_post.call_args
        assert call_args[1]['headers']['Authorization'] == f'ApiKey {client.api_key}'

    # ===== Edge Cases =====

    @patch('requests.post')
    def test_empty_text(self, mock_post, autobranch_resource):
        """Test with empty text"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 0,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = autobranch_resource.suggest_branches(text="")
        assert result is not None

    @patch('requests.post')
    def test_very_long_text(self, mock_post, autobranch_resource):
        """Test with very long text input"""
        long_text = "This is a test. " * 1000

        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 0,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = autobranch_resource.suggest_branches(text=long_text)

        call_args = mock_post.call_args
        assert len(call_args[1]['json']['text']) > 10000

    @patch('requests.post')
    def test_special_characters_in_text(self, mock_post, autobranch_resource):
        """Test with special characters in text"""
        special_text = "Test with émojis 🎉 and special chars: @#$%^&*()"

        mock_response = Mock()
        mock_response.json.return_value = {
            'suggestions': [],
            'metadata': {
                'detectionMethod': 'pattern',
                'totalBranchPointsFound': 0,
                'modelUsed': None
            }
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = autobranch_resource.suggest_branches(text=special_text)

        call_args = mock_post.call_args
        assert call_args[1]['json']['text'] == special_text


# ===== Pytest Configuration =====

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
