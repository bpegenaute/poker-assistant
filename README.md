# Poker Assistant

A Streamlit-based poker assistant that provides mathematically-sound recommendations with explanations.

## Features
- Real-time GTO-based poker recommendations
- Tournament strategy adjustments
- Position-based play analysis
- Real-time screen capture and OCR
- AI-powered player profiling
- Comprehensive hand analysis
- Interactive UI with detailed statistics

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- OpenAI API key

### Installation
1. Clone the repository
2. Install dependencies:
```bash
pip install streamlit sqlalchemy openai pillow opencv-python pytesseract numpy
```
3. Configure environment variables for database and OpenAI API
4. Run the application:
```bash
streamlit run main.py
```

For detailed installation instructions and configuration options, please see [INSTALLATION.md](INSTALLATION.md).

## Usage
1. Enter your stack size
2. Select your position
3. Input your hole cards
4. Add community cards as they appear
5. Get mathematically-sound recommendations

## Features
- GTO-based decision making
- Tournament-specific adjustments
- Position-based strategies
- Real-time screen analysis
- AI-powered opponent modeling
- Comprehensive statistics tracking

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
