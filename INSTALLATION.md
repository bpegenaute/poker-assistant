# Poker Assistant - Installation Guide

## Prerequisites

### All Platforms
- Python 3.11 or higher
- PostgreSQL database
- OpenAI API key for AI analysis features
- Tesseract OCR

### macOS 14+ Requirements
1. **XCode Command Line Tools**
```bash
xcode-select --install
```

2. **Homebrew Package Manager**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. **Python Installation (via Homebrew)**
```bash
brew install python@3.11
```

4. **Tesseract OCR Installation**
```bash
brew install tesseract
```

5. **PostgreSQL Installation**
```bash
brew install postgresql@14
brew services start postgresql@14
```

6. **Screen Recording Permissions**
- Open System Settings > Privacy & Security > Screen Recording
- Enable permissions for your terminal application and browser
- Restart your terminal and browser after enabling permissions

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd poker-assistant
```

### 2. Install Dependencies
The project requires several Python packages. Install them using pip:
```bash
pip install -r requirements.txt
```

### 3. Database Setup
Configure PostgreSQL database and set environment variables:
```bash
# macOS Environment Setup
echo 'export DATABASE_URL="postgresql://<username>:<password>@<host>:<port>/<database>"' >> ~/.zshrc
echo 'export PGUSER="<username>"' >> ~/.zshrc
echo 'export PGPASSWORD="<password>"' >> ~/.zshrc
echo 'export PGHOST="<host>"' >> ~/.zshrc
echo 'export PGPORT="<port>"' >> ~/.zshrc
echo 'export PGDATABASE="<database>"' >> ~/.zshrc
source ~/.zshrc
```

### 4. OpenAI API Configuration
```bash
echo 'export OPENAI_API_KEY="<your-api-key>"' >> ~/.zshrc
source ~/.zshrc
```

### 5. Application Configuration
Create a `.streamlit` directory and add a `config.toml` file:
```bash
mkdir -p .streamlit
cat > .streamlit/config.toml << EOL
[server]
headless = true
address = "0.0.0.0"
port = 5000
EOL
```

### 6. Running the Application
```bash
streamlit run main.py
```

## Troubleshooting

### macOS Specific Issues

#### 1. Screen Capture Issues
```
Error: Screen capture not working
Solution: 
1. Check System Settings > Privacy & Security > Screen Recording
2. Ensure permissions are granted for your terminal and browser
3. Restart applications after permission changes
4. Run `tccutil reset ScreenCapture` if permissions are stuck
```

#### 2. OCR Setup Issues
```
Error: Tesseract not found
Solution:
1. Verify installation: brew list tesseract
2. Check PATH: echo $PATH | grep tesseract
3. Reinstall if needed: brew reinstall tesseract
4. Set TESSDATA_PREFIX: export TESSDATA_PREFIX=$(brew --prefix)/share/tessdata
```

#### 3. Database Configuration
```
Error: Could not connect to database
Solution:
1. Verify PostgreSQL is running: brew services list
2. Check connection: psql -h localhost -U <username> -d <database>
3. Reset PostgreSQL if needed: brew services restart postgresql
```

#### 4. Environment Variables
```
Error: Environment variable not set
Solution:
1. Check variables: env | grep PG
2. Reload shell: source ~/.zshrc
3. Verify in new terminal window
4. Use launchctl to set system-wide: launchctl setenv VAR_NAME "value"
```

## Automated Setup (macOS)

Save the following as `setup_macos.sh`:
```bash
#!/bin/bash

# Check for Homebrew and install if missing
if ! command -v brew &> /dev/null; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install required packages
brew install python@3.11 postgresql@14 tesseract

# Start PostgreSQL
brew services start postgresql@14

# Install Python dependencies
pip3.11 install -r requirements.txt

# Setup environment variables (needs manual input)
echo "Please enter your database configuration:"
read -p "Database Username: " db_user
read -s -p "Database Password: " db_pass
echo
read -p "Database Name: " db_name
read -p "OpenAI API Key: " openai_key

# Create environment variable file
cat > ~/.poker_assistant_env << EOL
export DATABASE_URL="postgresql://${db_user}:${db_pass}@localhost:5432/${db_name}"
export PGUSER="${db_user}"
export PGPASSWORD="${db_pass}"
export PGHOST="localhost"
export PGPORT="5432"
export PGDATABASE="${db_name}"
export OPENAI_API_KEY="${openai_key}"
EOL

echo "source ~/.poker_assistant_env" >> ~/.zshrc

# Create database
createdb "${db_name}"

echo "Setup complete! Please restart your terminal and run 'streamlit run main.py'"
```

Make the script executable:
```bash
chmod +x setup_macos.sh
```

Run the setup script:
```bash
./setup_macos.sh
```
