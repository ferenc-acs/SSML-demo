# /// script
# dependencies = [
#   "streamlit",
#   "google-genai",
#   "keyring",
#   "keyrings.alt",
# ]
# ///

import streamlit as st
from google import genai
import os
import platform
import keyring
from tts_backends import (
    TTSConfigError,
    get_tts_backend,
    diagnose_linux_piper,
    detect_snap_piper_defaults,
)

def main():
    st.set_page_config(page_title="SSML Demo", layout="centered")
    st.title("Edge-TTS with SSML & Gemini")
    st.markdown("Demonstrating emotional text-to-speech using Windows SAPI and Gemini-generated SSML.")

    # Sidebar for configuration
    with st.sidebar:
        try:
            stored_key = keyring.get_password("SSML_Demo", "gemini_api")
        except Exception:
            stored_key = None
        api_key = st.text_input("Gemini API Key", value=stored_key if stored_key else "", type="password")
        if not api_key:
            st.info("Get your API key from [Google AI Studio](https://aistudio.google.com/)")

        platform_label = platform.system()
        st.caption(f"Detected platform: {platform_label}")

        backend_env = os.getenv("TTS_BACKEND", "auto")
        backend_options = ["auto", "windows_sapi", "linux_piper"]
        backend_index = backend_options.index(backend_env) if backend_env in backend_options else 0
        backend_choice = st.selectbox("TTS Backend", backend_options, index=backend_index)

        piper_binary = os.getenv("PIPER_BINARY", "piper")
        piper_model_path = os.getenv("PIPER_MODEL_PATH", "")
        piper_speaker_id = os.getenv("PIPER_SPEAKER_ID", "")

        linux_active = backend_choice == "linux_piper" or (
            backend_choice == "auto" and platform_label == "Linux"
        )
        if linux_active:
            if piper_binary == "piper" and not piper_model_path:
                snap_binary, snap_model = detect_snap_piper_defaults()
                if snap_binary and snap_model:
                    piper_binary = snap_binary
                    piper_model_path = snap_model
                    st.caption("Detected Piper snap defaults.")
            piper_binary = st.text_input("Piper Binary", value=piper_binary)
            piper_model_path = st.text_input("Piper Model Path", value=piper_model_path)
            piper_speaker_id = st.text_input("Piper Speaker ID (Optional)", value=piper_speaker_id)
            if st.button("Check Linux Audio"):
                report = diagnose_linux_piper(piper_binary, piper_model_path)
                if report["ok"]:
                    st.success("Linux audio configuration looks ready.")
                else:
                    st.warning("Linux audio configuration needs attention.")

                if report["piper_found"]:
                    st.info(f"Piper binary found: {report['piper_binary']}")
                else:
                    st.error(f"Piper binary not found: {report['piper_binary']}")

                if report["model_found"]:
                    st.info(f"Piper model found: {report['piper_model_path']}")
                else:
                    st.error("Piper model not found. Set PIPER_MODEL_PATH.")

                if report["playback_tools"]:
                    st.info(f"Playback tools available: {', '.join(report['playback_tools'])}")
                else:
                    st.error("No playback tools found. Install aplay, paplay, ffplay, or simpleaudio.")

                if report["ssml2piper_available"]:
                    st.info("ssml2piper available for SSML conversion.")
                else:
                    st.warning("ssml2piper not installed. SSML will be stripped to plain text.")

        if st.button("Check Available Models"):
            if not api_key:
                st.error("Please enter an API Key first.")
            else:
                client = genai.Client(api_key=api_key)
                try:
                    models = client.models.list()
                    found = False
                    st.write("### Available Generative Models:")
                    for m in models:
                        if 'generateContent' in m.supported_generation_methods:
                            st.write(f"- `{m.name}`")
                            found = True
                    if not found:
                        st.warning("No models found that support `generateContent`.")
                except Exception as e:
                    st.error(f"Error listing models: {e}")

    # Main interface
    text_input = st.text_area("Text to speak", value="I am not sure if this is a good idea, honestly.")
    emotion = st.selectbox("Emotion", ["Neutral", "Excited", "Depressed"])

    if st.button("Speak"):
        if not api_key:
            st.error("Please provide a valid Gemini API Key.")
            return

        client = genai.Client(api_key=api_key)
        
        try:
            # Generate SSML
            if emotion == "Neutral":
                ssml_text = text_input
            else:
                with st.spinner(f"Generating {emotion} SSML..."):
                    prompt = f"""
                    You are an SSML expert for Windows SAPI 5.
                    Convert this text: "{text_input}"
                    To SAPI 5 SSML to express the emotion: {emotion}.
                    
                    Rules:
                    - Use <rate absspeed="X"/> (X between -10 and 10)
                    - Use <pitch absmiddle="X"/> (X between -10 and 10)
                    - Output RAW XML only. No markdown block.
                    - Do not wrap in ```xml ... ```.
                    """
                    response = client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                    ssml_text = response.text.strip()
                    # Clean up if markdown is returned despite instructions
                    if ssml_text.startswith("```"):
                        lines = ssml_text.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines[-1].startswith("```"):
                            lines = lines[:-1]
                        ssml_text = "\n".join(lines).strip()

            st.subheader("Generated SSML")
            st.code(ssml_text, language="xml")

            # Speak
            st.status("Speaking on host device...")

            backend = get_tts_backend(
                {
                    "backend": backend_choice,
                    "piper_binary": piper_binary,
                    "piper_model_path": piper_model_path,
                    "piper_speaker_id": piper_speaker_id,
                }
            )
            backend.speak(ssml_text)

        except TTSConfigError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    if st.runtime.exists():
        main()
    else:
        import sys
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
