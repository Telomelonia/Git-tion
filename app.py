import os
import json
import logging
import hmac
import hashlib
import requests
import time
import jwt
from flask import Flask, request, jsonify
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables
GITHUB_SECRET = os.environ.get('GITHUB_SECRET')
GITHUB_APP_ID = os.environ.get('GITHUB_APP_ID')
GITHUB_PRIVATE_KEY = os.environ.get('GITHUB_PRIVATE_KEY', '').replace('\\n', '\n')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

# Webhook route to receive GitHub events
@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({"error": "Invalid signature"}), 401
    
    # Parse the payload
    payload = request.json
    
    # Check if this is an issue comment event
    if request.headers.get('X-GitHub-Event') == 'issue_comment':
        return handle_issue_comment(payload)
    
    return jsonify({"status": "ignored"}), 200

def verify_signature(payload_body, signature_header):
    """Verify that the webhook is from GitHub by checking the signature"""
    if not signature_header:
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        key=GITHUB_SECRET.encode(),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def get_github_app_token(installation_id):
    """Get an access token for a GitHub App installation"""
    now = int(time.time())
    payload = {
        'iat': now,
        'exp': now + (10 * 60),  # 10 minutes expiration
        'iss': GITHUB_APP_ID
    }
    
    # Create JWT for GitHub App
    jwt_token = jwt.encode(payload, GITHUB_PRIVATE_KEY, algorithm='RS256')
    
    # Get installation token
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code != 201:
        logger.error(f"Failed to get installation token: {response.text}")
        raise Exception(f"Failed to get installation token: {response.status_code}")
    
    return response.json()['token']

def inspect_database():
    """Inspect the Notion database structure for debugging"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        database = response.json()
        properties = database.get('properties', {})
        for name, prop in properties.items():
            logger.info(f"Property: {name}, Type: {prop.get('type')}")
    else:
        logger.error(f"Error inspecting database: {response.status_code}, {response.text}")

def handle_issue_comment(payload):
    """Handle issue comment events"""
    # Check if this is a new comment
    if payload.get('action') != 'created':
        return jsonify({"status": "not a new comment"}), 200
    
    # Get the comment body
    comment_body = payload.get('comment', {}).get('body', '')
    
    # Check if the command is in the comment
    if '@git-tion !send' not in comment_body:
        return jsonify({"status": "no command found"}), 200
    
    # Get issue details
    issue = payload.get('issue', {})
    issue_number = issue.get('number')
    issue_title = issue.get('title')
    issue_body = issue.get('body', '')
    issue_url = issue.get('html_url')
    repo_full_name = payload.get('repository', {}).get('full_name')
    installation_id = payload.get('installation', {}).get('id')
    
    logger.info(f"Processing command for issue #{issue_number} in {repo_full_name}")
    
    try:
        # Create a ticket in Notion
        notion_page_id = create_notion_ticket(
            title=issue_title,
            description=issue_body,
            issue_number=issue_number,
            issue_url=issue_url,
            repo=repo_full_name
        )
        
        # Add a comment to the GitHub issue
        add_github_comment(
            repo_full_name=repo_full_name,
            issue_number=issue_number,
            notion_page_id=notion_page_id,
            installation_id=installation_id
        )
        
        return jsonify({"status": "success", "notion_page_id": notion_page_id}), 200
    
    except Exception as e:
        logger.error(f"Error processing issue: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def create_notion_ticket(title, description, issue_number, issue_url, repo):
    """Create a new ticket in the Notion database"""
    logger.info(f"Creating Notion ticket for issue #{issue_number}")
    
    # Prepare the properties for the Notion page
    properties = {
        "Task name": {
            "title": [
                {
                    "text": {
                        "content": f"[#{issue_number}] {title}"
                    }
                }
            ]
        },
        "Status": {
            "status": { 
                "name": "Icebox"
            }
        },
        "GitHub Issue": {
            "url": issue_url
        },
        "Repository": {
            "rich_text": [
                {
                    "text": {
                        "content": repo
                    }
                }
            ]
        }
    }
    
    # Prepare the content for the page
    children = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Imported from GitHub Issue #" + str(issue_number)
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": description if description else "No description provided."
                        }
                    }
                ]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"GitHub Issue: {issue_url}"
                        },
                        "href": issue_url
                    }
                ]
            }
        }
    ]
    
    # Create the page in Notion
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties,
        "children": children
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 200:
        logger.error(f"Failed to create Notion page: {response.text}")
        raise Exception(f"Failed to create Notion page: {response.status_code}")
    
    notion_data = response.json()
    notion_page_id = notion_data.get('id')
    notion_url = f"https://notion.so/{notion_page_id.replace('-', '')}"
    
    logger.info(f"Created Notion ticket: {notion_url}")
    return notion_page_id

def add_github_comment(repo_full_name, issue_number, notion_page_id, installation_id):
    """Add a comment to the GitHub issue confirming the Notion ticket was created"""
    logger.info(f"Adding comment to GitHub issue #{issue_number}")
    
    # Get an installation token for the GitHub App
    token = get_github_app_token(installation_id)
    
    notion_url = f"https://notion.so/{notion_page_id.replace('-', '')}"
    comment_body = f"✅ Created Notion ticket: [View in Notion]({notion_url})"
    
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{issue_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment_body
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code != 201:
        logger.error(f"Failed to add GitHub comment: {response.text}")
        raise Exception(f"Failed to add GitHub comment: {response.status_code}")
    
    logger.info("Added comment to GitHub issue")

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)