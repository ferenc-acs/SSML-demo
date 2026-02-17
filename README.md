# SSML Demo

A Streamlit application that demonstrates Speech Synthesis Markup Language (SSML) capabilities using Google's Gemini 2.0 Flash model to generate expressive speech markup, rendered via Windows SAPI 5 on Windows and Piper on Linux.

## Features

- **Emotion-driven TTS**: Convert text to speech with specific emotions (Neutral, Excited, Depressed).
- **AI-Powered SSML**: Uses Gemini 2.0 to generate valid SAPI 5 SSML tags for pitch and rate.
- **Cross-platform TTS**: Windows SAPI backend and Linux Piper backend with auto-selection.
- **Secure Credentials**: Integrated `keyring` support to securely store your API keys.

## Prerequisites

- Python 3.12+
- `uv` package manager (recommended)
- Windows 11 for SAPI voice rendering, or Linux for Piper playback.

### Linux Additional Requirements

- Piper binary available on PATH or set `PIPER_BINARY`.
- A Piper model file set `PIPER_MODEL_PATH`.
- Audio playback tool: `aplay` (alsa-utils), `paplay` (PulseAudio utils), or `ffplay` (FFmpeg).
- Optional: `ssml2piper` for better SSML conversion on Linux.
- Optional: `simpleaudio` for Python playback (may require Python headers).

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

### Backend Selection

The app auto-selects the backend by OS. Override with:

```bash
export TTS_BACKEND=windows_sapi
# or
export TTS_BACKEND=linux_piper
```

## Usage

Run the Streamlit app:
```bash
uv run ssml_demo.py
```

### Linux Setup Example

```bash
export PIPER_BINARY=piper
export PIPER_MODEL_PATH=/path/to/en_US-model.onnx
export PIPER_SPEAKER_ID=0
uv run ssml_demo.py
```

If you installed Piper via the snap (`piper-tts`), the app will auto-detect:

- `/snap/bin/piper-tts.piper-cli`
- `/snap/piper-tts/1/voices/en_US-lessac-medium.onnx`

### Linux Audio Check Script

```bash
export PIPER_BINARY=piper
export PIPER_MODEL_PATH=/path/to/en_US-model.onnx
uv run scripts/check_linux_audio.py
```

Optional SSML conversion helper:

```bash
uv pip install ssml2piper
```

Optional playback helper (may require Python headers):

```bash
uv pip install simpleaudio
```

## License

MIT

## Release Notes

### 2026-02-17

- Added cross-platform TTS backends (Windows SAPI + Linux Piper).
- Introduced Linux audio diagnostics and a CLI check script.
- Added snap auto-detection for `piper-tts` defaults on Linux.
- Made optional helpers (`ssml2piper`, `simpleaudio`) non-mandatory.
