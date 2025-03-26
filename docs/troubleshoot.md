# Git-tion Troubleshooting Guide

Welcome to the Git-tion Troubleshooting Guide! This interactive guide will help you diagnose and fix common issues with your GitHub to Notion Bridge Bot.

## How to Use This Guide

Describe your issue below, and I'll help you troubleshoot. For the best assistance, please provide:

- What step you're stuck on (installation, configuration, GitHub setup, Notion setup, etc.)
- Any error messages you're seeing (exact text is helpful)
- Your environment (Docker, local installation, cloud deployment)

## Common Issues

### 1. Webhook Not Receiving Events

**Symptoms:**

- GitHub issue comments with `@git-tion !send` don't create Notion tickets
- No response from the bot on GitHub issues
- GitHub App shows failed webhook deliveries

**Possible Causes:**

- Incorrect webhook URL in GitHub App settings
- Webhook secret mismatch
- Network/firewall blocking requests
- Application not running

**Troubleshooting Steps:**

- Verify the webhook URL in GitHub App settings matches your application URL
- Check that your webhook secret in `.env` matches the GitHub App settings
- Examine application logs for incoming requests
- Test if your application is accessible from the internet
- Verify GitHub event deliveries in GitHub App settings

### 2. Notion Tickets Not Being Created

**Symptoms:**

- GitHub webhook is received (visible in logs)
- No errors in application logs
- No ticket appears in Notion database

**Possible Causes:**

- Incorrect Notion token
- Incorrect database ID
- Database not shared with the integration
- Missing or misnamed database properties

**Troubleshooting Steps:**

- Verify your Notion token is correct and has not expired
- Check that your database ID is correct
- Ensure you've shared your database with the integration
- Verify database has the required properties: "Task name", "Status", etc.

### 3. GitHub Authentication Issues

**Symptoms:**

- Errors related to GitHub API authentication
- Messages about invalid tokens or permissions

**Possible Causes:**

- Invalid GitHub App ID
- Incorrectly formatted private key
- App not installed on the repository
- Insufficient permissions

**Troubleshooting Steps:**

- Verify your GitHub App ID is correct
- Check your private key is properly formatted with `\n` for newlines
- Ensure the app is installed on the repository
- Check that the app has Issues (read & write) and Metadata (read) permissions

### 4. Docker Environment Issues

**Symptoms:**

- Container fails to start
- Application crashes on startup
- Environment variables not being recognized

**Possible Causes:**

- Missing or incorrect environment variables
- Missing ngrok or ngrok authtoken
- Volume mounts not configured correctly
- Network issues between containers

**Troubleshooting Steps:**

- Verify `.env` file is properly mounted
- Check container logs: `docker logs gittion-app`
- Ensure ngrok is installed and run this command

```bash
ngrok config add-authtoken *your-token*
```

- Ensure network configuration is correct
- Verify that required ports are exposed

### 5. Webhook Command Not Recognized

**Symptoms:**

- Bot doesn't respond to the `@git-tion !send` command
- Application logs show webhook received but no action taken

**Possible Causes:**

- Command format has changed in code
- Issue with parsing the comment body
- Webhook event not triggering the correct handler

**Troubleshooting Steps:**

- Check the command string in your code matches what you're typing
- Verify the webhook is receiving the "issue_comment" event type
- Test with different command formats

## For Advanced Debugging

### Application Logs

To view detailed logs:

```bash
# For Docker installations
docker logs gittion-app

# For local installations
tail -f logs/app.log
```

### Webhook Testing

To manually test your webhook:

```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issue_comment" \
  -H "X-Hub-Signature-256: sha256=..." \
  -d '{"action":"created","comment":{"body":"@git-tion !send"},"issue":{"number":1,"title":"Test","body":"Test issue","html_url":"https://github.com/user/repo/issues/1"},"repository":{"full_name":"user/repo"},"installation":{"id":12345678}}'
```

### Database Schema

For Notion database configuration, ensure you have these properties:

- "Task name" (title type)
- "Status" (status type with option for "Icebox")
- "GitHub Issue" (url type)
- "Repository" (rich text type)

## Ready for Your Issue

Please describe what issue you're facing, and I'll help you troubleshoot!
