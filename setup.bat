@echo off
setlocal enabledelayedexpansion

echo 🚀 Setting up Git-tion: GitHub to Notion Bridge Bot
echo ==================================================
echo.

echo Checking dependencies...
:: Check for Python
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    exit /b 1
)

:: Check for pip
pip --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo pip is not installed or not in your PATH.
    echo It should come with Python installation.
    exit /b 1
)

:: Check for git
git --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/download/win
    exit /b 1
)

echo All dependencies are installed!
echo.

:: Create virtual environment
echo Setting up Python virtual environment...
if not exist venv (
    python -m venv venv
    echo Virtual environment created!
) else (
    echo Virtual environment already exists, using existing one.
)

:: Activate virtual environment
call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed!
echo.

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating environment configuration...
    copy .env.sample .env

    :: Generate GitHub webhook secret
    echo.
    echo Generating a secure webhook secret for GitHub...
    :: Generate a webhook secret using Windows PowerShell
    for /f "tokens=*" %%a in ('powershell -Command "[System.Guid]::NewGuid().ToString()"') do set WEBHOOK_SECRET=%%a
    echo Generated webhook secret: !WEBHOOK_SECRET!
    echo Please save this value for configuring your GitHub App!
    echo.

    :: Use PowerShell to replace placeholder in .env file
    powershell -Command "(Get-Content .env) -replace 'your_github_webhook_secret', '!WEBHOOK_SECRET!' | Set-Content .env"

    :: Notion setup
    echo Let's set up your Notion integration:
    echo 1. Go to https://www.notion.so/my-integrations and click 'New integration'
    echo 2. Give it a name like 'GitHub Issue Bridge'
    echo 3. Select the workspace where your database lives
    echo 4. Click 'Submit' and copy the 'Internal Integration Token'
    echo.
    
    set /p NOTION_SETUP="Have you created a Notion integration and have the token? (y/n): "
    if /i "!NOTION_SETUP!"=="y" (
        set /p NOTION_TOKEN="Enter your Notion token: "
        powershell -Command "(Get-Content .env) -replace 'your_notion_integration_token', '!NOTION_TOKEN!' | Set-Content .env"
        
        echo.
        echo To get your Notion database ID:
        echo 1. Open your Notion database in a web browser
        echo 2. The URL will look like: https://www.notion.so/workspace/1234abcd5678efgh9012ijkl?v=...
        echo 3. The database ID is the part after the workspace name and before the ?v= parameter
        
        set /p NOTION_DB_ID="Enter your Notion database ID: "
        powershell -Command "(Get-Content .env) -replace 'your_notion_database_id', '!NOTION_DB_ID!' | Set-Content .env"
        
        echo.
        echo Don't forget to share your Notion database with your integration:
        echo 1. Open your Notion database
        echo 2. Click 'Share' in the top right
        echo 3. Click 'Add people, emails, groups, or integrations'
        echo 4. Find your integration by name and click 'Invite'
    ) else (
        echo.
        echo You'll need to update the NOTION_TOKEN and NOTION_DATABASE_ID in your .env file later.
    )
    
    :: GitHub App setup
    echo.
    echo Now let's set up your GitHub App:
    echo 1. Go to your GitHub account settings
    echo 2. Click 'Developer settings' ^> 'GitHub Apps' ^> 'New GitHub App'
    echo 3. Fill in the required fields:
    echo    - GitHub App name: Choose a unique name
    echo    - Homepage URL: Can be the repository URL or a placeholder
    echo    - Webhook URL: Use your deployed URL or ngrok URL + /webhook
    echo    - Webhook secret: Use the generated secret (!WEBHOOK_SECRET!)
    echo 4. Set permissions:
    echo    - Repository permissions:
    echo      - Issues: Read ^& write
    echo      - Metadata: Read-only
    echo 5. Subscribe to events:
    echo    - Issue comment
    echo 6. Create the app and note the App ID
    echo 7. Generate a private key and download it
    
    set /p GITHUB_SETUP="Have you created a GitHub App and have the App ID? (y/n): "
    if /i "!GITHUB_SETUP!"=="y" (
        set /p GITHUB_APP_ID="Enter your GitHub App ID: "
        powershell -Command "(Get-Content .env) -replace 'your_github_app_id', '!GITHUB_APP_ID!' | Set-Content .env"
        
        echo.
        echo Now we need to add your private key to the .env file.
        echo Please save your private key file as 'github-private-key.pem' in the current directory.
        echo Press any key when you've placed the file...
        pause > nul
        
        if exist github-private-key.pem (
            :: Read the private key file and format it with escaped newlines
            for /f "delims=" %%i in ('powershell -Command "$key = Get-Content -Raw 'github-private-key.pem'; $key = $key -replace '`r`n', '\n'; $key"') do set PRIVATE_KEY=%%i
            
            :: Update the .env file with the private key
            powershell -Command "$content = Get-Content -Path '.env' -Raw; $content = $content -replace 'Your Private Key Here', '!PRIVATE_KEY!'; Set-Content -Path '.env' -Value $content"
            
            echo Private key added to .env file!
            echo Removing temporary private key file...
            del github-private-key.pem
        ) else (
            echo Private key file not found. You'll need to manually update the GITHUB_PRIVATE_KEY in your .env file.
        )
    ) else (
        echo.
        echo You'll need to update the GITHUB_APP_ID and GITHUB_PRIVATE_KEY in your .env file later.
    )
    
    echo.
    echo Environment configuration created!
) else (
    echo Environment file (.env) already exists. Skipping configuration.
    echo If you want to reconfigure, either edit the .env file directly or delete it and run this script again.
)

:: Creating local development helper script
if not exist run_local.bat (
    echo.
    echo Creating local development helper script...
    (
        echo @echo off
        echo call venv\Scripts\activate.bat
        echo python app.py
    ) > run_local.bat
    echo Created run_local.bat for easy local development!
)

echo.
echo Setup complete! 🎉
echo.
echo Next steps:
echo 1. Make sure your GitHub App is installed on your repository
echo    (Go to your GitHub App page ^> Install App ^> Select repositories)
echo 2. Share your Notion database with your integration if you haven't already
echo 3. Run the app locally with: run_local.bat
echo 4. Expose your local server with ngrok: ngrok http 5000
echo    (Download ngrok from https://ngrok.com/download if you don't have it)
echo 5. Update your GitHub App's webhook URL with your ngrok URL
echo.
echo For production deployment:
echo - Deploy to Heroku: git push heroku main
echo - Or use Docker: docker build -t git-tion . ^&^& docker run -p 5000:5000 git-tion
echo.
echo To test the integration:
echo 1. Go to any issue in your GitHub repository
echo 2. Add a comment with: @git-tion !send
echo 3. The bot will create a Notion ticket and reply with a confirmation

:: Keep the window open if the script was double-clicked
echo.
echo Press any key to exit...
pause > nul