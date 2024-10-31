# Poker Assistant - Installation Guide

## Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- OpenAI API key for AI analysis features

## Installation Steps

### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone <repository-url>
cd poker-assistant
```

### 2. Install Dependencies
The project requires several Python packages. Install them using pip:
```bash
pip install streamlit sqlalchemy openai pillow opencv-python pytesseract numpy
```

### 3. Database Setup
The application requires a PostgreSQL database. Set up your database and configure the following environment variables:
```bash
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
PGUSER=<username>
PGPASSWORD=<password>
PGHOST=<host>
PGPORT=<port>
PGDATABASE=<database>
```

### 4. OpenAI API Configuration
For AI analysis features, set up your OpenAI API key:
```bash
OPENAI_API_KEY=<your-api-key>
```

### 5. Application Configuration
Create a `.streamlit` directory and add a `config.toml` file with the following contents:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### 6. Running the Application
Start the application using Streamlit:
```bash
streamlit run main.py
```

The application will be available at `http://localhost:5000`

## Project Structure
```
├── .streamlit/
│   └── config.toml
├── components/
│   ├── screen_capture_ui.py
│   ├── tournament_ui.py
│   └── ui_elements.py
├── poker/
│   ├── ai_analysis.py
│   ├── calculator.py
│   ├── database.py
│   ├── evaluator.py
│   ├── gto_engine.py
│   ├── recommendations.py
│   ├── screen_capture.py
│   └── tournament_engine.py
├── utils/
│   └── constants.py
└── main.py
```

## Features and Components

### 1. Core Features
- Hand evaluation and GTO-based recommendations
- Tournament strategy adjustments
- Position-based play analysis
- Real-time screen capture and OCR
- AI-powered player profiling

### 2. UI Components
- Stack size input
- Position selector
- Hand selector
- Betting controls
- Community cards selector
- Tournament controls
- Screen capture interface

### 3. Database Components
The application uses PostgreSQL to store:
- Hand histories
- Player profiles
- Tournament results
- Performance statistics

## Troubleshooting

### Common Issues

1. Database Connection Issues
```
Error: Could not connect to database
Solution: Verify your PostgreSQL credentials and ensure the database server is running
```

2. OpenAI API Issues
```
Error: OpenAI API key not found
Solution: Make sure you've set the OPENAI_API_KEY environment variable
```

3. Screen Capture Issues
```
Error: Screen capture not working
Solution: Ensure you have granted screen sharing permissions in your browser
```

### Getting Help
If you encounter any issues:
1. Check the application logs
2. Verify all environment variables are set correctly
3. Ensure all dependencies are installed properly
4. Check your database connection

## Development

### Adding New Features
1. Create new components in the appropriate directory
2. Update main.py to include new features
3. Add any new dependencies to the installation instructions

### Testing
Run the application locally and test:
1. Basic functionality (hand evaluation, recommendations)
2. Tournament features
3. Screen capture capabilities
4. Database operations

### Security Notes
- Never commit sensitive information (API keys, passwords)
- Use environment variables for all sensitive data
- Keep your dependencies updated
