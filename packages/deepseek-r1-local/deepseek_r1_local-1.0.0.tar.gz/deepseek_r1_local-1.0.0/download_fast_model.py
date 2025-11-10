#!/usr/bin/env python3
"""
Download a small, fast model for offline use
"""
import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download

# TinyLlama is ~600MB and runs well on CPU (10-50 tokens/s)
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
MODEL_DIR = Path("./models/tinyllama")

def download_model():
    """Download a small, fast model"""
    print("=" * 60)
    print("Fast Model Downloader")
    print("=" * 60)
    print(f"\nModel: {MODEL_NAME}")
    print(f"Download location: {MODEL_DIR.absolute()}")
    print("\nThis is a small model optimized for CPU inference!")
    print("Size: ~600MB")
    print("Expected speed: 10-50 tokens/second on CPU\n")
    
    # Create models directory
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        print("Starting download...\n")
        snapshot_download(
            repo_id=MODEL_NAME,
            local_dir=str(MODEL_DIR),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print("\n" + "=" * 60)
        print("✓ Model downloaded successfully!")
        print("=" * 60)
        print("\nYou can now run: python app_fast.py")
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Error downloading model: {e}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
