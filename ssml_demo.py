# /// script
# dependencies = [
#   "streamlit",
#   "google-generativeai",
#   "keyring",
#   "keyrings.alt",
# ]
# ///

import streamlit as st
import google.generativeai as genai
import subprocess
import os
import keyring

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

        if st.button("Check Available Models"):
            if not api_key:
                st.error("Please enter an API Key first.")
            else:
                genai.configure(api_key=api_key)
                try:
                    models = genai.list_models()
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

        genai.configure(api_key=api_key)
        
        try:
            # Generate SSML
            if emotion == "Neutral":
                ssml_text = text_input
            else:
                with st.spinner(f"Generating {emotion} SSML..."):
                    model = genai.GenerativeModel("gemini-2.0-flash")
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
                    response = model.generate_content(prompt)
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
            
            # PowerShell command to speak SSML
            # 8 is the flag for SPF_IS_XML
            ps_code = f"""
            $voice = New-Object -ComObject SAPI.SpVoice
            # Try to find an English voice
            $englishVoice = $voice.GetVoices() | Where-Object {{ $_.GetDescription() -like "*English*" }} | Select-Object -First 1
            if ($englishVoice) {{
                $voice.Voice = $englishVoice
            }}
            $voice.Speak('{ssml_text.replace("'", "''")}', 8)
            """
            
            # Run PowerShell
            subprocess.run(["powershell.exe", "-Command", ps_code], check=True)
            
        except FileNotFoundError:
            st.error("powershell.exe not found. This app expects to run in WSL with access to Windows PowerShell.")
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