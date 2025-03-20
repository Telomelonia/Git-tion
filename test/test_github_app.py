import pytest
import time
import jwt
from unittest.mock import patch, MagicMock, ANY

# Import the app to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import get_github_app_token, add_github_comment


@patch('app.jwt.encode')
@patch('app.requests.post')
def test_get_github_app_token(mock_post, mock_jwt_encode):
    """Test GitHub App token acquisition"""
    # Set up the mocks
    mock_jwt_encode.return_value = "test-jwt-token"
    
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "token": "test-installation-token",
        "expires_at": "2023-01-01T00:00:00Z"
    }
    mock_post.return_value = mock_response
    
    # Test data
    installation_id = 12345678
    app_id = "test-app-id"
    private_key = "test-private-key"
    
    # Test with mocked environment variables
    with patch('app.GITHUB_APP_ID', app_id), \
         patch('app.GITHUB_PRIVATE_KEY', private_key):
        
        # Call the function
        token = get_github_app_token(installation_id)
        
        # Verify the result
        assert token == "test-installation-token"
        
        # Verify the JWT creation
        mock_jwt_encode.assert_called_once()
        args, kwargs = mock_jwt_encode.call_args
        assert args[0]['iss'] == app_id
        assert abs(args[0]['iat'] - int(time.time())) < 10  # Should be recent
        assert args[0]['exp'] > args[0]['iat']  # Expiry should be after issued time
        assert kwargs['algorithm'] == 'RS256'
        
        # Verify the API call
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert f"https://api.github.com/app/installations/{installation_id}/access_tokens" in args
        assert kwargs['headers']['Authorization'] == f"Bearer test-jwt-token"


@patch('app.requests.post')
def test_get_github_app_token_failure(mock_post):
    """Test GitHub App token acquisition failure"""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not found"
    mock_post.return_value = mock_response
    
    # Test data
    installation_id = 12345678
    
    # Test with mocked environment variables and jwt.encode
    with patch('app.GITHUB_APP_ID', "test-app-id"), \
         patch('app.GITHUB_PRIVATE_KEY', "test-private-key"), \
         patch('app.jwt.encode', return_value="test-jwt-token"):
        
        # Call the function and expect an exception
        with pytest.raises(Exception) as excinfo:
            get_github_app_token(installation_id)
        
        # Verify that the error message contains the status code
        assert "404" in str(excinfo.value)


@patch('app.get_github_app_token')
@patch('app.requests.post')
def test_add_github_comment_success(mock_post, mock_get_token):
    """Test successful GitHub comment addition"""
    # Set up the mocks
    mock_get_token.return_value = "test-installation-token"
    
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_post.return_value = mock_response
    
    # Test data
    repo_full_name = "user/repo"
    issue_number = 42
    notion_page_id = "test-page-id-123456789"
    installation_id = 12345678
    
    # Call the function
    add_github_comment(
        repo_full_name=repo_full_name,
        issue_number=issue_number,
        notion_page_id=notion_page_id,
        installation_id=installation_id
    )
    
    # Verify the token acquisition
    mock_get_token.assert_called_once_with(installation_id)
    
    # Verify the API call
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    
    # Check the URL contains repo and issue number
    assert f"https://api.github.com/repos/{repo_full_name}/issues/{issue_number}/comments" in args
    
    # Check that authorization uses the token
    assert kwargs['headers']['Authorization'] == f"token test-installation-token"
    
    # Check that the comment body contains the Notion URL
    assert "notion.so" in kwargs['json']['body']
    assert notion_page_id.replace('-', '') in kwargs['json']['body']


@patch('app.get_github_app_token')
@patch('app.requests.post')
def test_add_github_comment_failure(mock_post, mock_get_token):
    """Test GitHub comment addition failure"""
    # Set up the mocks
    mock_get_token.return_value = "test-installation-token"
    
    mock_response = MagicMock()
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_post.return_value = mock_response
    
    # Test data
    repo_full_name = "user/repo"
    issue_number = 42
    notion_page_id = "test-page-id-123456789"
    installation_id = 12345678
    
    # Call the function and expect an exception
    with pytest.raises(Exception) as excinfo:
        add_github_comment(
            repo_full_name=repo_full_name,
            issue_number=issue_number,
            notion_page_id=notion_page_id,
            installation_id=installation_id
        )
    
    # Verify that the error message contains the status code
    assert "403" in str(excinfo.value)