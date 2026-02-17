import os
import platform
import re
import subprocess
import tempfile
import shutil
import importlib


class TTSConfigError(RuntimeError):
    pass


def _platform_key() -> str:
    system = platform.system().lower()
    if system.startswith("windows"):
        return "windows"
    if system == "linux":
        return "linux"
    return system


def resolve_backend(backend_choice: str) -> str:
    if backend_choice == "auto":
        system = _platform_key()
        if system == "windows":
            return "windows_sapi"
        if system == "linux":
            return "linux_piper"
        raise TTSConfigError(f"Unsupported platform: {platform.system()}")
    if backend_choice in {"windows_sapi", "linux_piper"}:
        return backend_choice
    raise TTSConfigError(f"Unknown backend: {backend_choice}")


def get_tts_backend(config: dict):
    backend = resolve_backend(config.get("backend", "auto"))
    if backend == "windows_sapi":
        return WindowsSapiTTS()
    return LinuxPiperTTS(
        piper_binary=config.get("piper_binary", "piper"),
        piper_model_path=config.get("piper_model_path", ""),
        piper_speaker_id=config.get("piper_speaker_id") or None,
    )


def _strip_ssml(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _convert_ssml_for_piper(text: str) -> str:
    if "<" not in text:
        return text
    try:
        from ssml2piper import ssml_to_piper

        converted = ssml_to_piper(text)
        if converted:
            return converted
    except Exception:
        pass
    return _strip_ssml(text)


def _module_available(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def probe_linux_playback_tools() -> list[str]:
    tools = []
    if _module_available("simpleaudio"):
        tools.append("simpleaudio")
    if shutil.which("aplay"):
        tools.append("aplay")
    if shutil.which("paplay"):
        tools.append("paplay")
    if shutil.which("ffplay"):
        tools.append("ffplay")
    return tools


def diagnose_linux_piper(piper_binary: str, piper_model_path: str) -> dict:
    piper_found = shutil.which(piper_binary) is not None or os.path.exists(piper_binary)
    model_found = bool(piper_model_path) and os.path.exists(piper_model_path)
    playback_tools = probe_linux_playback_tools()
    ssml2piper_available = _module_available("ssml2piper")
    ok = piper_found and model_found and bool(playback_tools)
    return {
        "ok": ok,
        "piper_found": piper_found,
        "piper_binary": piper_binary,
        "model_found": model_found,
        "piper_model_path": piper_model_path,
        "playback_tools": playback_tools,
        "ssml2piper_available": ssml2piper_available,
    }


def detect_snap_piper_defaults() -> tuple[str | None, str | None]:
    snap_wrapper = "/snap/bin/piper-tts.piper-cli"
    snap_model = "/snap/piper-tts/1/voices/en_US-lessac-medium.onnx"
    if os.path.exists(snap_wrapper) and os.path.exists(snap_model):
        return snap_wrapper, snap_model
    return None, None


class WindowsSapiTTS:
    def speak(self, ssml_text: str) -> None:
        escaped = ssml_text.replace("'", "''")
        ps_code = f"""
        $voice = New-Object -ComObject SAPI.SpVoice
        # Try to find an English voice
        $englishVoice = $voice.GetVoices() | Where-Object {{ $_.GetDescription() -like "*English*" }} | Select-Object -First 1
        if ($englishVoice) {{
            $voice.Voice = $englishVoice
        }}
        $voice.Speak('{escaped}', 8)
        """
        try:
            subprocess.run(["powershell.exe", "-Command", ps_code], check=True)
        except FileNotFoundError as exc:
            raise TTSConfigError(
                "powershell.exe not found. Windows SAPI backend requires PowerShell."
            ) from exc


class LinuxPiperTTS:
    def __init__(self, piper_binary: str, piper_model_path: str, piper_speaker_id: str | None):
        if not piper_model_path:
            raise TTSConfigError("PIPER_MODEL_PATH is required for the Linux Piper backend.")
        self.piper_binary = piper_binary
        self.piper_model_path = piper_model_path
        self.piper_speaker_id = piper_speaker_id

    def speak(self, ssml_text: str) -> None:
        text = _convert_ssml_for_piper(ssml_text)
        wav_path = None

        try:
            # Use local file instead of /tmp to avoid snap confinement issues
            import uuid
            wav_path = os.path.join(os.path.dirname(__file__), f"piper_output_{uuid.uuid4().hex[:8]}.wav")

            cmd = [
                self.piper_binary,
                "--model",
                self.piper_model_path,
                "--output_file",
                wav_path,
            ]
            if self.piper_speaker_id:
                cmd += ["--speaker", str(self.piper_speaker_id)]

            subprocess.run(cmd, input=text, text=True, check=True)

            if not self._play_wav(wav_path):
                raise TTSConfigError(
                    "No audio playback tool found. Install one of: "
                    "`simpleaudio`, `alsa-utils` (aplay), PulseAudio utils (paplay), "
                    "or FFmpeg (ffplay)."
                )
        except FileNotFoundError as exc:
            raise TTSConfigError(
                f"Piper binary not found: {self.piper_binary}"
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Piper synthesis failed: {exc}") from exc
        finally:
            # Cleanup the generated wav file
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except OSError:
                    pass

    def _play_wav(self, wav_path: str) -> bool:
        # Try simpleaudio first (non-blocking friendly)
        if _module_available("simpleaudio"):
            try:
                import simpleaudio as sa
                wave = sa.WaveObject.from_wave_file(wav_path)
                play_obj = wave.play()
                play_obj.wait_done()
                return True
            except Exception:
                pass

        # Use timeout and background process to avoid blocking Streamlit
        aplay = shutil.which("aplay")
        if aplay:
            try:
                # Start playback in background, don't block
                import threading
                def play():
                    subprocess.run([aplay, wav_path], timeout=30, capture_output=True)
                thread = threading.Thread(target=play)
                thread.start()
                thread.join(timeout=0.5)  # Wait briefly but don't block UI
                return True
            except Exception:
                pass

        paplay = shutil.which("paplay")
        if paplay:
            try:
                import threading
                def play():
                    subprocess.run([paplay, wav_path], timeout=30, capture_output=True)
                thread = threading.Thread(target=play)
                thread.start()
                thread.join(timeout=0.5)
                return True
            except Exception:
                pass

        ffplay = shutil.which("ffplay")
        if ffplay:
            try:
                import threading
                def play():
                    subprocess.run(
                        [ffplay, "-nodisp", "-autoexit", "-loglevel", "error", wav_path],
                        timeout=30, capture_output=True
                    )
                thread = threading.Thread(target=play)
                thread.start()
                thread.join(timeout=0.5)
                return True
            except Exception:
                pass

        return False
