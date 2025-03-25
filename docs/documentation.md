# Git-tion: GitHub to Notion Bridge

Git-tion is a bridge application that connects GitHub issues to Notion databases, allowing teams to automatically create Notion tickets from GitHub issues using a simple command.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation Options](#installation-options)
  - [Quick Start with Setup Script](#quick-start-with-setup-script)
  - [Docker Installation](#docker-installation)
  - [Manual Installation](#manual-installation)
- [Configuration](#configuration)
  - [GitHub App Setup](#github-app-setup)
  - [Notion Integration Setup](#notion-integration-setup)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [Creating Notion Tickets](#creating-notion-tickets)
  - [Customizing the Integration](#customizing-the-integration)
- [Development](#development)
  - [Running Locally](#running-locally)
  - [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

Git-tion monitors GitHub repositories for issue comments containing a specific command (default: `@git-tion !send`). When this command is detected, the application:

1. Creates a new ticket in your configured Notion database
2. Copies relevant information from the GitHub issue (title, description, links)
3. Sets the ticket status to "Icebox" (or your configured default)
4. Adds a comment to the GitHub issue with a link to the Notion ticket

This allows teams to easily triage GitHub issues into their Notion workspace for planning and prioritization.

## Getting Started

### Prerequisites

- GitHub account with permissions to create GitHub Apps
- Notion account with permissions to create integrations
- A Notion database to store tickets
- For local development: Python 3.8+
- For Docker installation: Docker and Docker Compose

### Installation Options

Git-tion offers several installation options to fit your needs:

1. **Automated Setup Script**: Guided CLI setup for individual deployments
2. **Docker Installation**: Containerized deployment using Docker Compose
3. **Manual Installation**: Step-by-step setup for custom environments

### Quick Start with Setup Script

The fastest way to get started is with our setup script:

```bash
# Clone the repository
git clone https://github.com/yourusername/github-notion-bridge.git
cd github-notion-bridge

# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The script will guide you through:

1. Setting up your development environment
2. Installing dependencies
3. Configuring GitHub and Notion integrations
4. Creating your environment variables

### Docker Installation

For a containerized setup:

```bash
# Clone the repository
git clone https://github.com/yourusername/github-notion-bridge.git
cd github-notion-bridge

# Create your environment file
cp .env.sample .env
# Edit .env with your configuration

# Build and run with Docker Compose
docker-compose up -d
```

Access ngrok at http://localhost:4040 to get your public URL for the GitHub webhook.

### Manual Installation

If you prefer a manual setup:

1. Clone the repository

   ```bash
   git clone https://github.com/yourusername/github-notion-bridge.git
   cd github-notion-bridge
   ```

2. Create a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

4. Create your environment file

   ```bash
   cp .env.sample .env
   # Edit .env with your configuration
   ```

5. Run the application

   ```bash
   python app.py
   ```

6. Expose your local server with ngrok (for development)
   ```bash
   ngrok http 5000
   ```

## Configuration

### GitHub App Setup

1. Go to your GitHub account settings > Developer settings > GitHub Apps > New GitHub App
2. Configure the app:
   - **Name**: Choose a name for your app (e.g., "Git-tion Bridge")
   - **Homepage URL**: Your application URL or repository URL
   - **Webhook URL**: Your application URL + "/webhook" (e.g., https://your-app.example.com/webhook)
   - **Webhook secret**: Generate a secure random string
   - **Permissions**:
     - Issues: Read & write
     - Metadata: Read-only
   - **Subscribe to events**: Issue comment
3. Create the app and note your App ID
4. Generate a private key
5. Install the app on your repositories

### Notion Integration Setup

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
   - **Name**: Choose a name (e.g., "GitHub Issue Bridge")
   - **Associated workspace**: Select your workspace
3. Copy the "Internal Integration Token"
4. Open your Notion database
5. Share the database with your integration (Click "Share" > Add integrations > Select your integration)
6. Copy your database ID from the URL:
   ```
   https://www.notion.so/workspace/1234abcd5678efgh9012ijkl?v=...
                                   ^^^^^^^^^^^^^^^^^^^^
                                   This is your database ID
   ```

### Environment Variables

Configure the following environment variables in your `.env` file:

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

## Usage

### Creating Notion Tickets

1. Go to any issue in your GitHub repository
2. Add a comment with the command: `@git-tion !send`
3. The bot will create a Notion ticket and reply with a confirmation comment

### Customizing the Integration

You can customize the application behavior by modifying:

- **Command trigger**: Change the `@git-tion !send` command in `app.py`
- **Default status**: Change the "Icebox" status in the `create_notion_ticket` function
- **Ticket properties**: Modify the properties structure in the `create_notion_ticket` function
- **Comment format**: Update the comment template in the `add_github_comment` function

## Development

### Running Locally

For local development:

```bash
# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the application
python app.py

# In a separate terminal, run ngrok to expose your webhook
ngrok http 5000
```

Update your GitHub App's webhook URL with the ngrok URL.

### Testing

Run the automated tests:

```bash
pip install -r requirements-dev.txt
pytest test/
```

## Troubleshooting

### Webhook Issues

If your webhook isn't receiving events:

1. Check that your webhook URL is correctly set in the GitHub App settings
2. Verify your ngrok tunnel is running (if using local development)
3. Check that your `GITHUB_SECRET` matches the webhook secret in GitHub App settings
4. Look at the application logs for error messages

### Notion Integration Issues

If tickets aren't being created in Notion:

1. Verify your Notion integration token is correct
2. Check that you've shared the database with your integration
3. Verify the database ID is correct
4. Ensure your database has the required properties:
   - "Task name" (title)
   - "Status" (status)
   - "GitHub Issue" (URL)
   - "Repository" (text)

### GitHub App Authentication Issues

If you're having GitHub authentication problems:

1. Verify your GitHub App ID is correct
2. Check that your private key is properly formatted with `\n` newlines
3. Ensure the app is installed on the repository
4. Verify the app has the necessary permissions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
