import os
import logging

# Configure logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Environment variables
GITHUB_SECRET = os.environ.get('GITHUB_SECRET')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

# Check if required environment variables are set
if not all([GITHUB_SECRET, GITHUB_TOKEN, NOTION_TOKEN, NOTION_DATABASE_ID]):
    missing_vars = []
    if not GITHUB_SECRET: missing_vars.append('GITHUB_SECRET')
    if not GITHUB_TOKEN: missing_vars.append('GITHUB_TOKEN')
    if not NOTION_TOKEN: missing_vars.append('NOTION_TOKEN')
    if not NOTION_DATABASE_ID: missing_vars.append('NOTION_DATABASE_ID')
    
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    # You could raise an exception here or handle it another way