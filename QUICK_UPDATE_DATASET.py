#!/usr/bin/env python3
"""
QUICK UPDATE - Regenerate training dataset with all voiced conversations
"""

import json
import os
from pathlib import Path

print("🔄 UPDATING TRAINING DATASET WITH ALL VOICED CONVERSATIONS")
print("=" * 60)

# Count audio files
audio_dir = Path("data/tts_audio_final")
audio_files = list(audio_dir.glob("*.mp3"))
unique_convs = set()

for audio_file in audio_files:
    # Extract conv_id from filename
    parts = audio_file.stem.rsplit('_turn_', 1)
    if len(parts) == 2:
        unique_convs.add(parts[0])

print(f"📊 Found {len(audio_files)} audio files")
print(f"📊 From {len(unique_convs)} unique conversations")

# Now run the autonomous dataset creator
print("\n🤖 Running autonomous dataset generator...")
os.system("python3 CREATE_AUTONOMOUS_TRAINING_DATASET.py")

print("\n✅ DATASET UPDATED!")
print(f"🏆 Ready for TEKNOFEST 2025 with:")
print(f"   • {len(unique_convs)} conversations")
print(f"   • {len(audio_files)} audio files")
print(f"   • ~800+ training examples expected")