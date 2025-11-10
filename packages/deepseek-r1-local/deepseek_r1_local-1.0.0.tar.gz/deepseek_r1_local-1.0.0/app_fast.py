#!/usr/bin/env python3
"""
Fast version using TinyLlama - optimized for CPU
"""
import os
import sys
from pathlib import Path

# Get the script directory for relative paths
SCRIPT_DIR = Path(__file__).parent.absolute()

# Update to use the fast model
MODEL_DIR = SCRIPT_DIR / "models" / "tinyllama"

# Import and patch the app
import app
app.MODEL_DIR = MODEL_DIR

# Update model manager initialization message
original_load = app.ModelManager.load_model

def patched_load(self):
    print("=" * 60)
    print("Loading TinyLlama (Fast CPU Model)")
    print("=" * 60)
    original_load(self)

app.ModelManager.load_model = patched_load

if __name__ == '__main__':
    app.main()
