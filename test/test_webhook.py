import json
import hmac
import hashlib
import pytest
from unittest.mock import patch, MagicMock

# Import the app to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, verify_signature


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_verify_signature_valid():
    """Test that valid signatures are verified correctly"""
    # Create a test secret and payload
    secret = "test_secret"
    payload = b'{"test": "payload"}'
    
    # Generate a signature
    signature = 'sha256=' + hmac.new(
        key=secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Test with mocked environment variable
    with patch('app.GITHUB_SECRET', secret):
        assert verify_signature(payload, signature) is True


def test_verify_signature_invalid():
    """Test that invalid signatures are rejected"""
    # Create a test secret and payload
    secret = "test_secret"
    payload = b'{"test": "payload"}'
    
    # Generate an invalid signature
    signature = 'sha256=' + hmac.new(
        key=b"wrong_secret",
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    # Test with mocked environment variable
    with patch('app.GITHUB_SECRET', secret):
        assert verify_signature(payload, signature) is False


def test_webhook_invalid_signature(client):
    """Test that webhook rejects requests with invalid signatures"""
    # Create a test payload
    payload = {"test": "payload"}
    
    # Send a request with an invalid signature
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        content_type='application/json',
        headers={'X-Hub-Signature-256': 'invalid_signature'}
    )
    
    assert response.status_code == 401
    assert b'Invalid signature' in response.data


@patch('app.verify_signature')
def test_webhook_issue_comment_no_command(mock_verify, client):
    """Test that webhook ignores comments without commands"""
    # Set up the mock to return True for signature verification
    mock_verify.return_value = True
    
    # Create a test payload for an issue comment without the command
    payload = {
        "action": "created",
        "comment": {
            "body": "This is a regular comment"
        }
    }
    
    # Send a request
    response = client.post(
        '/webhook',
        data=json.dumps(payload),
        content_type='application/json',
        headers={'X-GitHub-Event': 'issue_comment'}
    )
    
    assert response.status_code == 200
    assert b'no command found' in response.data


@patch('app.verify_signature')
@patch('app.handle_issue_comment')
def test_webhook_issue_comment_with_command(mock_handle, mock_verify, client):
    """Test that webhook processes comments with commands"""
    # Set up the mocks
    mock_verify.return_value = True
    mock_handle.return_value = MagicMock(status_code=200)
    
    # Create a test payload for an issue comment with the command
    payload = {
        "action": "created",
        "comment": {
            "body": "Let's create a Notion ticket @git-tion !send"
        }
    }
    
    # Send a request
    client.post(
        '/webhook',
        data=json.dumps(payload),
        content_type='application/json',
        headers={'X-GitHub-Event': 'issue_comment'}
    )
    
    # Verify that handle_issue_comment was called
    mock_handle.assert_called_once()


@patch('app.verify_signature')
def test_webhook_ignores_non_issue_comment_events(mock_verify, client):
    """Test that webhook ignores non-issue-comment events"""
    # Set up the mock to return True for signature verification
    mock_verify.return_value = True
    
    # Send a request with a different event type
    response = client.post(
        '/webhook',
        data=json.dumps({"test": "payload"}),
        content_type='application/json',
        headers={'X-GitHub-Event': 'push'}
    )
    
    assert response.status_code == 200
    assert b'ignored' in response.data