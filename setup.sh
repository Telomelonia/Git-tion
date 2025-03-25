#!/bin/bash

set -e

# Text formatting
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${BOLD}${GREEN}🚀 Setting up Git-tion: GitHub to Notion Bridge Bot${NC}"
echo -e "${BOLD}==================================================${NC}\n"

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Function to prompt for yes/no confirmation
confirm() {
  read -p "$1 (y/n): " -n 1 -r
  echo
  [[ $REPLY =~ ^[Yy]$ ]]
}

# Function to generate a secure random string for GitHub webhook secret
generate_secret() {
  if command_exists openssl; then
    openssl rand -hex 20
  else
    # Fallback method if openssl is not available
    cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 40 | head -n 1
  fi
}

echo -e "${BLUE}Checking dependencies...${NC}"
# Check for required dependencies
missing_deps=()

if ! command_exists python3; then
  missing_deps+=("Python 3")
fi

if ! command_exists pip3; then
  missing_deps+=("pip3")
fi

if ! command_exists git; then
  missing_deps+=("git")
fi

if [ ${#missing_deps[@]} -ne 0 ]; then
  echo -e "${RED}The following dependencies are missing:${NC}"
  for dep in "${missing_deps[@]}"; do
    echo "  - $dep"
  done
  echo -e "\n${YELLOW}Please install them and run this script again.${NC}"
  exit 1
fi

echo -e "${GREEN}✓ All dependencies installed!${NC}\n"

# Create virtual environment
echo -e "${BLUE}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
  python3 -m venv venv
  echo -e "${GREEN}✓ Virtual environment created!${NC}"
else
  echo -e "${YELLOW}Virtual environment already exists, using existing one.${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated!${NC}\n"

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed!${NC}\n"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo -e "${BLUE}Creating environment configuration...${NC}"
  cp .env.sample .env
  
  # Generate GitHub webhook secret
  echo -e "\n${YELLOW}Generating a secure webhook secret for GitHub...${NC}"
  WEBHOOK_SECRET=$(generate_secret)
  sed -i.bak "s/your_github_webhook_secret/$WEBHOOK_SECRET/g" .env && rm -f .env.bak
  echo -e "${GREEN}✓ Generated webhook secret: ${WEBHOOK_SECRET}${NC}"
  echo -e "${YELLOW}Please save this value for configuring your GitHub App!${NC}\n"
  
  # Notion setup
  echo -e "${BLUE}Let's set up your Notion integration:${NC}"
  echo -e "1. Go to ${BOLD}https://www.notion.so/my-integrations${NC} and click 'New integration'"
  echo -e "2. Give it a name like 'GitHub Issue Bridge'"
  echo -e "3. Select the workspace where your database lives"
  echo -e "4. Click 'Submit' and copy the 'Internal Integration Token'"
  
  if confirm "Have you created a Notion integration and have the token?"; then
    read -p "Enter your Notion token: " notion_token
    sed -i.bak "s/your_notion_integration_token/$notion_token/g" .env && rm -f .env.bak
    
    echo -e "\nTo get your Notion database ID:"
    echo -e "1. Open your Notion database in a web browser"
    echo -e "2. The URL will look like: https://www.notion.so/workspace/1234abcd5678efgh9012ijkl?v=..."
    echo -e "3. The database ID is the part after the workspace name and before the ?v= parameter"
    
    read -p "Enter your Notion database ID: " notion_db_id
    sed -i.bak "s/your_notion_database_id/$notion_db_id/g" .env && rm -f .env.bak
    
    echo -e "\n${YELLOW}Don't forget to share your Notion database with your integration:${NC}"
    echo -e "1. Open your Notion database"
    echo -e "2. Click 'Share' in the top right"
    echo -e "3. Click 'Add people, emails, groups, or integrations'"
    echo -e "4. Find your integration by name and click 'Invite'"
  else
    echo -e "\n${YELLOW}You'll need to update the NOTION_TOKEN and NOTION_DATABASE_ID in your .env file later.${NC}"
  fi
  
  # GitHub App setup
  echo -e "\n${BLUE}Now let's set up your GitHub App:${NC}"
  echo -e "1. Go to your GitHub account settings"
  echo -e "2. Click 'Developer settings' > 'GitHub Apps' > 'New GitHub App'"
  echo -e "3. Fill in the required fields:"
  echo -e "   - GitHub App name: Choose a unique name"
  echo -e "   - Homepage URL: Can be the repository URL or a placeholder"
  echo -e "   - Webhook URL: Use your deployed URL or ngrok URL + /webhook"
  echo -e "   - Webhook secret: Use the generated secret (${WEBHOOK_SECRET})"
  echo -e "4. Set permissions:"
  echo -e "   - Repository permissions:"
  echo -e "     - Issues: Read & write"
  echo -e "     - Metadata: Read-only"
  echo -e "5. Subscribe to events:"
  echo -e "   - Issue comment"
  echo -e "6. Create the app and note the App ID"
  echo -e "7. Generate a private key and download it"
  
  if confirm "Have you created a GitHub App and have the App ID?"; then
    read -p "Enter your GitHub App ID: " github_app_id
    sed -i.bak "s/your_github_app_id/$github_app_id/g" .env && rm -f .env.bak
    
    echo -e "\n${YELLOW}Now we need to add your private key to the .env file.${NC}"
    echo -e "Please paste the contents of your private key file (press Ctrl+D when done):"
    private_key=$(cat)
    
    # Escape special characters and format the key with proper newlines
    private_key_formatted=$(echo "$private_key" | awk '{printf "%s\\n", $0}')
    
    # Update the .env file with the private key
    sed -i.bak "s|Your Private Key Here|$private_key_formatted|g" .env && rm -f .env.bak
    
    echo -e "\n${GREEN}✓ Private key added to .env file!${NC}"
  else
    echo -e "\n${YELLOW}You'll need to update the GITHUB_APP_ID and GITHUB_PRIVATE_KEY in your .env file later.${NC}"
  fi
  
  echo -e "\n${GREEN}✓ Environment configuration created!${NC}"
else
  echo -e "${YELLOW}Environment file (.env) already exists. Skipping configuration.${NC}"
  echo -e "If you want to reconfigure, either edit the .env file directly or delete it and run this script again."
fi

# Creating test script for local development
if [ ! -f "run_local.sh" ]; then
  echo -e "\n${BLUE}Creating local development helper script...${NC}"
  cat > run_local.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python app.py
EOF
  chmod +x run_local.sh
  echo -e "${GREEN}✓ Created run_local.sh for easy local development!${NC}"
fi

echo -e "\n${GREEN}${BOLD}Setup complete! 🎉${NC}"
echo -e "\n${BOLD}Next steps:${NC}"
echo -e "1. Make sure your GitHub App is installed on your repository"
echo -e "   (Go to your GitHub App page > Install App > Select repositories)"
echo -e "2. Share your Notion database with your integration if you haven't already"
echo -e "3. Run the app locally with: ${BOLD}./run_local.sh${NC}"
echo -e "4. Expose your local server with ngrok: ${BOLD}ngrok http 5000${NC}"
echo -e "5. Update your GitHub App's webhook URL with your ngrok URL"
echo -e "\n${BOLD}For production deployment:${NC}"
echo -e "- Deploy to Heroku: ${BOLD}git push heroku main${NC}"
echo -e "- Or use Docker: ${BOLD}docker build -t git-tion . && docker run -p 5000:5000 git-tion${NC}"
echo -e "\n${BOLD}To test the integration:${NC}"
echo -e "1. Go to any issue in your GitHub repository"
echo -e "2. Add a comment with: ${BOLD}@git-tion !send${NC}"
echo -e "3. The bot will create a Notion ticket and reply with a confirmation"