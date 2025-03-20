import pytest
from unittest.mock import patch, MagicMock

# Import the app to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_notion_ticket


@patch('app.requests.post')
def test_create_notion_ticket_success(mock_post):
    """Test successful Notion ticket creation"""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-page-id-123456789",
        "url": "https://www.notion.so/Test-Page-test-page-id-123456789"
    }
    mock_post.return_value = mock_response
    
    # Test data
    title = "Test Issue"
    description = "This is a test issue description"
    issue_number = 42
    issue_url = "https://github.com/user/repo/issues/42"
    repo = "user/repo"
    
    # Call the function
    page_id = create_notion_ticket(
        title=title,
        description=description,
        issue_number=issue_number,
        issue_url=issue_url,
        repo=repo
    )
    
    # Verify the result
    assert page_id == "test-page-id-123456789"
    
    # Verify the API call
    mock_post.assert_called_once()
    
    # Verify the request data
    args, kwargs = mock_post.call_args
    assert "https://api.notion.com/v1/pages" in args
    
    # Check that the title includes the issue number
    assert "[#42]" in str(kwargs['json']['properties']['Task name']['title'][0]['text']['content'])
    
    # Check that the status is set to "Icebox"
    assert kwargs['json']['properties']['Status']['status']['name'] == "Icebox"
    
    # Check that GitHub issue URL is included
    assert issue_url in str(kwargs['json'])
    
    # Check that repo is included
    assert repo in str(kwargs['json'])


@patch('app.requests.post')
def test_create_notion_ticket_failure(mock_post):
    """Test Notion ticket creation failure"""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Error creating page"
    mock_post.return_value = mock_response
    
    # Test data
    title = "Test Issue"
    description = "This is a test issue description"
    issue_number = 42
    issue_url = "https://github.com/user/repo/issues/42"
    repo = "user/repo"
    
    # Call the function and expect an exception
    with pytest.raises(Exception) as excinfo:
        create_notion_ticket(
            title=title,
            description=description,
            issue_number=issue_number,
            issue_url=issue_url,
            repo=repo
        )
    
    # Verify that the error message contains the status code
    assert "400" in str(excinfo.value)
    
    # Verify the API call
    mock_post.assert_called_once()


@patch('app.inspect_database')
@patch('app.requests.post')
def test_create_notion_ticket_empty_description(mock_post, mock_inspect):
    """Test Notion ticket creation with an empty description"""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "test-page-id-123456789",
        "url": "https://www.notion.so/Test-Page-test-page-id-123456789"
    }
    mock_post.return_value = mock_response
    
    # Test data
    title = "Test Issue"
    description = ""  # Empty description
    issue_number = 42
    issue_url = "https://github.com/user/repo/issues/42"
    repo = "user/repo"
    
    # Call the function
    page_id = create_notion_ticket(
        title=title,
        description=description,
        issue_number=issue_number,
        issue_url=issue_url,
        repo=repo
    )
    
    # Verify the result
    assert page_id == "test-page-id-123456789"
    
    # Verify the API call
    mock_post.assert_called_once()
    
    # Check that the description contains the default text for empty descriptions
    args, kwargs = mock_post.call_args
    children = kwargs['json']['children']
    description_found = False
    
    for block in children:
        if block['type'] == 'paragraph':
            text_content = block['paragraph']['rich_text'][0]['text']['content']
            if "No description provided" in text_content:
                description_found = True
                break
    
    assert description_found, "Default text for empty description not found"