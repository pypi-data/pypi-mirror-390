#!/usr/bin/env python3
"""
Download DeepSeek R1 model for offline use
"""
import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download

MODEL_NAME = "microsoft/phi-2"  # Using Microsoft Phi-2 model (2.7B parameters)
MODEL_DIR = Path("./models/deepseek-r1")

def download_model():
    """Download the DeepSeek R1 model"""
    print("=" * 60)
    print("DeepSeek R1 Model Downloader")
    print("=" * 60)
    print(f"\nModel: {MODEL_NAME}")
    print(f"Download location: {MODEL_DIR.absolute()}")
    print("\nThis may take a while depending on your internet connection...")
    print("The model is approximately 3-4GB in size.\n")
    
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
        print("\nYou can now run the application with: python app.py")
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Error downloading model: {e}")
        print("=" * 60)
        print("\nPlease check your internet connection and try again.")
        return False

if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
