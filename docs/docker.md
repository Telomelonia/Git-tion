# Docker Setup for Git-tion

This guide walks you through setting up and running the GitHub to Notion Bridge Bot using Docker containers.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on your system
- [Docker Compose](https://docs.docker.com/compose/install/) installed on your system
- GitHub account with permissions to create a GitHub App
- Notion account with permissions to create integrations

## Quick Start

1. **Configure your environment**

   First, set up your environment variables:

   ```bash
   # Copy the sample environment file
   cp .env.sample .env

   # Edit the .env file with your credentials
   nano .env
   ```

2. **Build and start the containers**

   ```bash
   docker-compose up -d
   ```

   This will start:

   - The main application on port 5000
   - An ngrok service exposing your webhook to the internet (accessible at http://localhost:4040)

3. **Get your webhook URL**

   Visit http://localhost:4040 to view the ngrok interface and find your public URL. You'll need this URL to configure your GitHub App webhook.

4. **Update your GitHub App webhook URL**

   Go to your GitHub App settings and update the webhook URL with the ngrok URL + `/webhook`
   (e.g., `https://abcd1234.ngrok.io/webhook`)

## Troubleshooting

### Checking logs

```bash
# View logs for the application
docker-compose logs -f app

# View logs for ngrok
docker-compose logs -f ngrok
```

### Restarting services

```bash
# Restart all services
docker-compose restart

# Restart just the app
docker-compose restart app
```

### Stopping the services

```bash
docker-compose down
```

## Production Deployment

For production deployment, you should:

1. Remove the ngrok service from docker-compose.yml
2. Use a proper reverse proxy (like Nginx or Traefik) with HTTPS
3. Set up persistent storage for logs if needed

Example production docker-compose.yml:

```yaml
version: "3.8"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: gittion-app
    restart: always
    ports:
      - "5000:5000"
    volumes:
      - ./.env:/app/.env:ro
      - ./logs:/app/logs
    networks:
      - gittion-network

  # Add your reverse proxy here if needed

networks:
  gittion-network:
    driver: bridge
```

## Using Docker with the Setup Script

You can also use our setup script to configure your environment and then run with Docker:

```bash
# Run the setup script first to configure .env
chmod +x setup.sh
./setup.sh

# Then start Docker services
docker-compose up -d
```

This approach combines the ease of the guided setup with the reliability of containerized deployment.
