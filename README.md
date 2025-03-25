# GitHub to Notion Bridge Bot

A webhook-based application that monitors GitHub issues for specific command comments and automatically creates tickets in a Notion database. The bot operates as a dedicated GitHub App with its own identity, ensuring comments and actions appear from the bot account rather than a personal user account.

## Features

- Monitors GitHub issues for command comments (e.g., `@git-tion !send`)
- Creates a new ticket in a specified Notion database in the "Icebox" section
- Includes relevant information from the GitHub issue (title, description, issue number, link)
- Replies to the GitHub issue confirming the Notion ticket was created
- Acts as a dedicated bot with its own identity (rather than using a personal account)
- Includes automated testing and CI/CD pipeline integration

## Prerequisites

- Python 3.8+
- GitHub account with permission to create GitHub Apps
- Notion account with permission to create integrations
- A Notion database to store tickets

## Quick Setup

### Automated Setup (Recommended)

We provide a cross-platform setup script that guides you through the entire configuration process:

```bash
# Run the Python setup script
python setup.py
```

This interactive script will:

1. Check your environment for dependencies
2. Set up a Python virtual environment
3. Install all required packages
4. Generate a secure webhook secret
5. Guide you through Notion and GitHub App configuration
6. Create helper scripts for local development

### Platform-Specific Setup Scripts

If you prefer, you can also use platform-specific setup scripts:

**Linux/macOS:**

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

**Windows:**

```bash
# Run the batch script
setup.bat
```

## Manual Setup Instructions

If you prefer to set up manually, follow these detailed steps:

### 1. Create a Notion Integration

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click "New integration"
3. Give it a name (e.g., "GitHub Issue Bridge")
4. Select the workspace where your database lives
5. Click "Submit"
6. Copy the "Internal Integration Token" - you'll need this for the `NOTION_TOKEN` environment variable

### 2. Share Your Notion Database with the Integration

1. Open your Notion database
2. Click "Share" in the top right
3. Click "Add people, emails, groups, or integrations"
4. Find your integration by name and click "Invite"

### 3. Get Your Notion Database ID

1. Open your Notion database in a web browser
2. Look at the URL, which should look like: `https://www.notion.so/workspace/1234abcd5678efgh9012ijkl?v=...`
3. The database ID is the part after the workspace name and before the `?v=` parameter (in this example, `1234abcd5678efgh9012ijkl`)
4. Copy this ID - you'll need it for the `NOTION_DATABASE_ID` environment variable

### 4. Create a GitHub App

1. Go to your GitHub account settings
2. Click "Developer settings" > "GitHub Apps" > "New GitHub App"
3. Fill in the required fields:
   - GitHub App name: Choose a unique name
   - Homepage URL: Can be the repository URL or a placeholder for now
   - Webhook URL: Will be updated later after deployment
   - Webhook secret: Generate a secure random string (you'll need this for the `GITHUB_SECRET` environment variable)
4. Permissions:
   - Repository permissions:
     - Issues: Read & write
     - Metadata: Read-only
   - Subscribe to events:
     - Issue comment
5. Create the GitHub App
6. After creation, note your GitHub App ID (you'll need this for the `GITHUB_APP_ID` environment variable)
7. Generate a private key by clicking "Generate a private key" (you'll need this for the `GITHUB_PRIVATE_KEY` environment variable)
8. Install the app on your repository by clicking "Install App" in the left sidebar

### 5. Environment Setup

Create a `.env` file with the following variables:

```
# GitHub API credentials
GITHUB_SECRET=your_github_webhook_secret
GITHUB_APP_ID=your_github_app_id
GITHUB_PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----\nYour Private Key Here\n-----END RSA PRIVATE KEY-----

# Notion API credentials
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# Optional: Port for the webhook server
PORT=5000
```

### 6. Install Dependencies

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Deployment Options

### Local Development

After setup, you can run the application locally:

```bash
# Use the helper script created during setup
# On Windows
run_local.bat
# On macOS/Linux
./run_local.sh

# Or run directly
python app.py
```

For webhook testing, you'll need to expose your local server to the internet:

```bash
# Using ngrok
ngrok http 5000
```

Then update your GitHub App's webhook URL with your ngrok URL.

### Deploy to Heroku

1. Create a new Heroku app:

   ```bash
   heroku create github-notion-bridge
   ```

2. Set the environment variables:

   ```bash
   heroku config:set GITHUB_SECRET=your_github_webhook_secret
   heroku config:set GITHUB_APP_ID=your_github_app_id
   heroku config:set GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\nYour Private Key Here\n-----END RSA PRIVATE KEY-----"
   heroku config:set NOTION_TOKEN=your_notion_integration_token
   heroku config:set NOTION_DATABASE_ID=your_notion_database_id
   ```

3. Deploy the application:

   ```bash
   git push heroku main
   ```

### Docker Deployment

1. Build the Docker image:

   ```bash
   docker build -t git-tion .
   ```

2. Run the container:

   ```bash
   docker run -p 5000:5000 -e PORT=5000 --env-file .env git-tion
   ```

## Usage

1. Go to any issue in your GitHub repository
2. Add a comment with the text `@git-tion !send`
3. The bot will create a Notion ticket and reply with a confirmation comment as the GitHub App

## Testing

### Manual Testing

1. **Create a test issue**: Create a new issue in your repository
2. **Add a test comment**: Comment `@git-tion !send` on the issue
3. **Verify Notion creation**: Check that a new entry appears in your Notion database
4. **Verify GitHub comment**: Ensure the bot (not your personal account) added a confirmation comment with a link to the Notion page

### Automated Testing

The repository includes automated tests to verify the core functionality. To run tests:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Troubleshooting

### Webhook Not Receiving Events

- Verify your webhook URL is correct in the GitHub App settings
- Check that your server is accessible from the internet
- Verify the webhook secret is correctly set

### Error Creating Notion Tickets

- Verify your Notion integration token is correct
- Ensure your integration has been given access to the database
- Check that the database ID is correct
- Verify your database has the required properties (Title, Status, GitHub Issue, Repository)

### GitHub App Authentication Issues

- Verify your GitHub App ID is correct
- Ensure your private key is properly formatted with `\n` newlines
- Check that your GitHub App has the necessary permissions
- Verify the app is installed on the repository

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
