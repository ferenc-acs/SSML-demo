#!/bin/bash
# Generate and play emotional variations with Piper

PIPER="/snap/bin/piper-tts.piper-cli"
MODEL="/snap/piper-tts/1/voices/en_US-lessac-medium.onnx"

echo "=================================="
echo "EMOTIONAL SSML DEMO WITH PIPER"
echo "=================================="
echo ""

# NEUTRAL
echo "1. NEUTRAL (baseline):"
echo "   'I am not sure if this is a good idea, honestly.'"
echo -n "   Generating... "
echo "I am not sure if this is a good idea, honestly." | $PIPER --model $MODEL --output_file /tmp/neutral.wav 2>/dev/null
echo "Playing..."
aplay /tmp/neutral.wav 2>/dev/null
echo ""

# EXCITED (faster/higher simulation)
# Note: Piper doesn't do SSML rate/pitch natively
# But we can demonstrate the concept
echo "2. EXCITED (conceptual - Piper doesn't support rate/pitch tags):"
echo "   Pitch would be: +30%, Rate: +40%"
echo "   Text: 'I am not sure if this is a good idea, honestly. Really!'"
echo -n "   Generating... "
echo "I am not sure if this is a good idea, honestly. Really!" | $PIPER --model $MODEL --output_file /tmp/excited.wav 2>/dev/null
echo "Playing..."
aplay /tmp/excited.wav 2>/dev/null
echo ""

# DEPRESSED (slower/lower simulation)
echo "3. DEPRESSED (conceptual - would use SSML rate=-5, pitch=-3):"
echo "   Pitch would be: -30%, Rate: -40%, longer pauses"
echo -n "   Generating... "
echo "I am not sure if this is a good idea, honestly. Sigh..." | $PIPER --model $MODEL --output_file /tmp/depressed.wav 2>/dev/null
echo "Playing..."
aplay /tmp/depressed.wav 2>/dev/null
echo ""

echo "=================================="
echo "Demo complete!"
echo ""
echo "For full SSML support, you would need:"
echo "  - Windows SAPI (has full SSML)"
echo "  - Or: ssml2piper converter"
echo "  - Or: Gemini generating prosody markup"
echo "=================================="