"""SSML to Piper converter - converts SSML tags to Piper-compatible text with prosody hints."""

import re
from typing import Optional


def ssml_to_piper(ssml_text: str) -> str:
    """
    Convert SSML markup to Piper-compatible text.
    
    Since Piper doesn't natively support SSML, we convert the markup to
    text-based prosody hints that can guide emotional expression.
    
    Supported tags:
    - <rate absspeed="X">...</rate> - speaking rate
    - <pitch absmiddle="X">...</pitch> - pitch variation
    - <emphasis>...</emphasis> - emphasis/strong
    - <break time="Xms"/> - pauses
    - <speak>...</speak> - root element (stripped)
    """
    if not ssml_text or "<" not in ssml_text:
        return ssml_text
    
    text = ssml_text
    
    # Remove speak wrapper
    text = re.sub(r'</?speak[^>]*>', '', text)
    
    # Convert rate tags to visual prosody hints
    def rate_replacer(match):
        speed = int(match.group(1))
        content = match.group(2)
        if speed > 3:
            return f"[{content}] (faster)"
        elif speed < -3:
            return f"[{content}] (slower)"
        return content
    text = re.sub(r'<rate\s+absspeed="(-?\d+)"[^/]*/?>(.*?)</rate>', rate_replacer, text, flags=re.DOTALL)
    text = re.sub(r'<rate\s+absspeed="(-?\d+)"[^/]*/?>', '', text)
    
    # Convert pitch tags
    def pitch_replacer(match):
        pitch = int(match.group(1))
        content = match.group(2)
        if pitch > 3:
            return f"^{content}^ (higher)"
        elif pitch < -3:
            return f"_{content}_ (lower)"
        return content
    text = re.sub(r'<pitch\s+absmiddle="(-?\d+)"[^/]*/?>(.*?)</pitch>', pitch_replacer, text, flags=re.DOTALL)
    text = re.sub(r'<pitch\s+absmiddle="(-?\d+)"[^/]*/?>', '', text)
    
    # Convert emphasis to caps or markers
    def emphasis_replacer(match):
        level = match.group(1) if match.group(1) else "moderate"
        content = match.group(2)
        if level in ["strong", "x-strong"]:
            return f"**{content.upper()}**"
        return f"*{content}*"
    text = re.sub(r'<emphasis(?:\s+level="([^"]+)")?>(.*?)</emphasis>', emphasis_replacer, text, flags=re.DOTALL)
    
    # Convert breaks to ... pauses
    def break_replacer(match):
        time_str = match.group(1)
        if "ms" in time_str:
            ms = int(time_str.replace("ms", ""))
            if ms < 300:
                return ", "
            elif ms < 600:
                return "... "
            else:
                return "..... "
        elif "s" in time_str:
            return "..... "
        return "... "
    text = re.sub(r'<break\s+time="([^"]+)"\s*/?>', break_replacer, text)
    
    # Clean up any remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def strip_ssml(ssml_text: str) -> str:
    """Simply strip all SSML tags, returning plain text."""
    if not ssml_text:
        return ssml_text
    text = re.sub(r'<[^>]+>', '', ssml_text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
