#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import shutil
import uuid
import secrets
import re
import getpass
from pathlib import Path

# Text formatting for colored output (works in most terminals)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def disable_if_windows():
        # Disable colors on Windows unless ANSICON or ConEMU is used
        if platform.system() == "Windows" and not (os.environ.get('ANSICON') or 
                                                 os.environ.get('ConEmuANSI') == 'ON'):
            Colors.HEADER = ''
            Colors.BLUE = ''
            Colors.GREEN = ''
            Colors.YELLOW = ''
            Colors.RED = ''
            Colors.BOLD = ''
            Colors.UNDERLINE = ''
            Colors.END = ''


# Disable colors on Windows unless in a compatible terminal
Colors.disable_if_windows()

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{text}{Colors.END}")

def print_step(text):
    print(f"\n{Colors.BLUE}➤ {text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}! {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✖ {text}{Colors.END}")

def run_command(command, shell=True):
    """Run a command and return its output"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_dependencies():
    """Check if required dependencies are installed"""
    print_step("Checking dependencies...")
    missing_deps = []
    
    # Check Python version
    python_version = platform.python_version()
    if not python_version.startswith(('3.6', '3.7', '3.8', '3.9', '3.10', '3.11')):
        print_warning(f"Python version {python_version} may not be compatible. Python 3.6+ is recommended.")
    else:
        print_success(f"Python {python_version} detected")
    
    # Check for pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print_success("pip is installed")
    except subprocess.CalledProcessError:
        missing_deps.append("pip")
    
    # Check for git
    if shutil.which("git"):
        print_success("git is installed")
    else:
        missing_deps.append("git")
    
    # Report missing dependencies
    if missing_deps:
        print_error("The following dependencies are missing:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install them and run this script again.")
        sys.exit(1)
    
    print_success("All required dependencies are installed!")

def setup_virtual_env():
    """Create and activate a Python virtual environment"""
    print_step("Setting up Python virtual environment...")
    
    venv_dir = Path("venv")
    if not venv_dir.exists():
        run_command([sys.executable, "-m", "venv", "venv"])
        print_success("Virtual environment created!")
    else:
        print_warning("Virtual environment already exists, using existing one.")
    
    # Get the path to the activation script
    if platform.system() == "Windows":
        activate_script = venv_dir / "Scripts" / "activate"
    else:
        activate_script = venv_dir / "bin" / "activate"
    
    print_success(f"Virtual environment is ready at: {venv_dir}")
    
    # Install dependencies
    print_step("Installing dependencies...")
    
    # Get the path to the pip executable in the virtual environment
    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        pip_path = venv_dir / "bin" / "pip"
    
    run_command(f'"{pip_path}" install -r requirements.txt')
    print_success("Dependencies installed!")

def generate_webhook_secret():
    """Generate a secure random string for GitHub webhook secret"""
    return secrets.token_hex(20)

def create_env_file():
    """Create and configure the .env file"""
    print_step("Creating environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print_warning("Environment file (.env) already exists.")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower() == 'y'
        if not overwrite:
            print_warning("Skipping environment configuration.")
            return
    
    # Copy the sample .env file
    shutil.copy(".env.sample", ".env")
    
    # Generate GitHub webhook secret
    webhook_secret = generate_webhook_secret()
    print_success(f"Generated webhook secret: {webhook_secret}")
    print_warning("Please save this value for configuring your GitHub App!")
    
    # Update the .env file with the webhook secret
    with open(".env", "r") as f:
        env_content = f.read()
    
    env_content = env_content.replace("your_github_webhook_secret", webhook_secret)
    
    # Notion setup instructions
    print_step("Setting up your Notion integration:")
    print("1. Go to https://www.notion.so/my-integrations and click 'New integration'")
    print("2. Give it a name like 'GitHub Issue Bridge'")
    print("3. Select the workspace where your database lives")
    print("4. Click 'Submit' and copy the 'Internal Integration Token'")
    
    setup_notion = input("\nHave you created a Notion integration and have the token? (y/n): ").lower() == 'y'
    if setup_notion:
        notion_token = getpass.getpass("Enter your Notion token: ")
        env_content = env_content.replace("your_notion_integration_token", notion_token)
        
        print("\nTo get your Notion database ID:")
        print("1. Open your Notion database in a web browser")
        print("2. The URL will look like: https://www.notion.so/workspace/1234abcd5678efgh9012ijkl?v=...")
        print("3. The database ID is the part after the workspace name and before the ?v= parameter")
        
        notion_db_id = input("Enter your Notion database ID: ")
        env_content = env_content.replace("your_notion_database_id", notion_db_id)
        
        print_warning("\nDon't forget to share your Notion database with your integration:")
        print("1. Open your Notion database")
        print("2. Click 'Share' in the top right")
        print("3. Click 'Add people, emails, groups, or integrations'")
        print("4. Find your integration by name and click 'Invite'")
    else:
        print_warning("\nYou'll need to update the NOTION_TOKEN and NOTION_DATABASE_ID in your .env file later.")
    
    # GitHub App setup instructions
    print_step("Setting up your GitHub App:")
    print("1. Go to your GitHub account settings")
    print("2. Click 'Developer settings' > 'GitHub Apps' > 'New GitHub App'")
    print("3. Fill in the required fields:")
    print("   - GitHub App name: Choose a unique name")
    print("   - Homepage URL: Can be the repository URL or a placeholder")
    print("   - Webhook URL: Use your deployed URL or ngrok URL + /webhook")
    print(f"   - Webhook secret: Use the generated secret ({webhook_secret})")
    print("4. Set permissions:")
    print("   - Repository permissions:")
    print("     - Issues: Read & write")
    print("     - Metadata: Read-only")
    print("5. Subscribe to events:")
    print("   - Issue comment")
    print("6. Create the app and note the App ID")
    print("7. Generate a private key and download it")
    
    setup_github = input("\nHave you created a GitHub App and have the App ID? (y/n): ").lower() == 'y'
    if setup_github:
        github_app_id = input("Enter your GitHub App ID: ")
        env_content = env_content.replace("your_github_app_id", github_app_id)
        
        print_warning("\nNow we need to add your private key to the .env file.")
        print("Please paste the contents of your private key file (press Ctrl+D on Unix or Ctrl+Z followed by Enter on Windows when done):")
        
        # Read the private key from stdin
        try:
            private_key_lines = []
            while True:
                try:
                    line = input()
                    private_key_lines.append(line)
                except EOFError:
                    break
        except KeyboardInterrupt:
            print("\nPrivate key input cancelled.")
            private_key_lines = []
        
        if private_key_lines:
            # Format the private key with proper newlines for the .env file
            private_key = "\\n".join(private_key_lines)
            env_content = env_content.replace("Your Private Key Here", private_key)
            print_success("Private key added to .env file!")
        else:
            print_warning("No private key provided. You'll need to update GITHUB_PRIVATE_KEY in your .env file manually.")
    else:
        print_warning("\nYou'll need to update the GITHUB_APP_ID and GITHUB_PRIVATE_KEY in your .env file later.")
    
    # Write the updated content back to the .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print_success("Environment configuration created!")

def create_run_script():
    """Create a platform-specific script to run the application"""
    print_step("Creating helper scripts...")
    
    if platform.system() == "Windows":
        with open("run_local.bat", "w") as f:
            f.write("@echo off\n")
            f.write("call venv\\Scripts\\activate.bat\n")
            f.write("python app.py\n")
        print_success("Created run_local.bat for easy local development")
    else:
        with open("run_local.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("source venv/bin/activate\n")
            f.write("python app.py\n")
        os.chmod("run_local.sh", 0o755)  # Make the script executable
        print_success("Created run_local.sh for easy local development")

def main():
    """Main setup function"""
    print_header("🚀 Setting up Git-tion: GitHub to Notion Bridge Bot")
    print_header("==================================================")
    
    # Check dependencies
    check_dependencies()
    
    # Set up virtual environment
    setup_virtual_env()
    
    # Create and configure .env file
    create_env_file()
    
    # Create run script
    create_run_script()
    
    # Setup complete
    print_header("\n✨ Setup Complete! ✨")
    print("\nNext steps:")
    print("1. Make sure your GitHub App is installed on your repository")
    print("   (Go to your GitHub App page > Install App > Select repositories)")
    print("2. Share your Notion database with your integration if you haven't already")
    
    if platform.system() == "Windows":
        print("3. Run the app locally with: run_local.bat")
    else:
        print("3. Run the app locally with: ./run_local.sh")
    
    print("4. Expose your local server with ngrok: ngrok http 5000")
    print("5. Update your GitHub App's webhook URL with your ngrok URL")
    
    print("\nFor production deployment:")
    print("- Deploy to Heroku: git push heroku main")
    print("- Or use Docker: docker build -t git-tion . && docker run -p 5000:5000 git-tion")
    
    print("\nTo test the integration:")
    print("1. Go to any issue in your GitHub repository")
    print("2. Add a comment with: @git-tion !send")
    print("3. The bot will create a Notion ticket and reply with a confirmation")
    
    print("\nHappy coding! 🎉")

if __name__ == "__main__":
    main()