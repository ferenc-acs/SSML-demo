# SSML Demo

A Streamlit application that demonstrates Single Step Markup Language (SSML) capabilities using Google's Gemini 2.0 Flash model to generate expressive speech markup, rendered via Windows SAPI 5 (via PowerShell).

## Features

- **Emotion-driven TTS**: Convert text to speech with specific emotions (Neutral, Excited, Depressed).
- **AI-Powered SSML**: Uses Gemini 2.0 to generate valid SAPI 5 SSML tags for pitch and rate.
- **Secure Credentials**: Integrated `keyring` support to securely store your API keys.

## Prerequisites

- Python 3.12+
- `uv` package manager (recommended)
- Windows (or WSL with access to `powershell.exe`) for SAPI voice rendering.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ferenc-acs/SSML-demo.git
   cd SSML-demo
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

This project supports secure credential storage for your Gemini API key.

1. Run the setup script to store your API key securely:
   ```bash
   uv run scripts/setup_credentials.py
   ```
2. Follow the prompts to enter your API Key.
3. Access to the API key will now be automatic when running the application.

## Usage

Run the Streamlit app:
```bash
uv run ssml_demo.py
```

## License

MIT

