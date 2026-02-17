#!/usr/bin/env python3
"""Quick emotional SSML test for Piper."""

import os
import sys

# Text to test
text = "I am not sure if this is a good idea, honestly."

# Manual SSML variations for different emotions
neutral = text

excited = f'''<speak>
<rate absspeed="5"/>
<pitch absmiddle="3"/>
{text}
<break time="200ms"/>
Really!
</speak>'''

depressed = f'''<speak>
<rate absspeed="-5"/>
<pitch absmiddle="-3"/>
<break time="500ms"/>
{text}
<break time="800ms"/>
Sigh.
</speak>'''

worried = f'''<speak>
<rate absspeed="2"/>
<pitch absmiddle="1"/>
<emphasis level="moderate">{text}</emphasis>
<break time="300ms"/>
What do you think?
</speak>'''

print("EMOTIONAL SSML TEST")
print("=" * 50)
print(f"\nBase text: '{text}'\n")

print("1. NEUTRAL (no SSML)")
print(f"   {neutral[:60]}...")
print(f"\n   Plain text - no emotional coloring\n")

print("2. EXCITED")
print(f"   {excited[:60]}...")
print(f"   Faster rate (+5), higher pitch (+3)\n")

print("3. DEPRESSED")
print(f"   {depressed[:60]}...")
print(f"   Slower rate (-5), lower pitch (-3), longer pauses\n")

print("4. WORRIED")
print(f"   {worried[:60]}...")
print(f"   Moderate emphasis, questioning tone\n")

# Note: Piper doesn't support full SSML, so we'll strip tags for now
# But we can simulate emotion with prosody variations

print("=" * 50)
print("\nNote: Piper has limited SSML support.")
print("Full SSML conversion would use ssml2piper or similar.")
