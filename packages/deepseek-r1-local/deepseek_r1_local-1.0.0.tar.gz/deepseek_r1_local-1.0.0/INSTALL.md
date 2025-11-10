# Installation Guide

## Quick Start (Recommended)

### 1. Install via pip
```bash
pip install deepseek-r1-local
```

### 2. Download Model
```bash
deepseek-r1-local download-model
```
*This downloads ~2.2GB. Takes 5-10 minutes depending on internet speed.*

### 3. Start Server
```bash
deepseek-r1-local start
```

### 4. Open Browser
Navigate to: http://localhost:5000

---

## Detailed Installation Options

### Option A: PyPI Installation (Easiest)

```bash
# Create virtual environment (recommended)
python3 -m venv deepseek-env
source deepseek-env/bin/activate  # Windows: deepseek-env\Scripts\activate

# Install package
pip install deepseek-r1-local

# Download model
deepseek-r1-local download-model

# Start server
deepseek-r1-local start
```

### Option B: From Source (Developers)

```bash
# Clone repository
git clone https://github.com/yourusername/deepseek-r1-local.git
cd deepseek-r1-local

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .

# Download model
deepseek-r1-local download-model

# Start server
deepseek-r1-local start
```

### Option C: Manual Setup (Advanced)

```bash
# Clone and navigate
git clone https://github.com/yourusername/deepseek-r1-local.git
cd deepseek-r1-local

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download TinyLlama model
python download_fast_model.py

# Run directly
python app_fast.py
```

---

## System Requirements

### Minimum
- Python 3.9+
- 8GB RAM
- 5GB free disk space
- CPU: Any modern processor

### Recommended
- Python 3.10+
- 16GB RAM
- 10GB free disk space
- CPU: Multi-core processor

---

## Platform-Specific Instructions

### macOS
```bash
# Install Python (if needed)
brew install python@3.11

# Follow Quick Start above
pip3 install deepseek-r1-local
deepseek-r1-local download-model
deepseek-r1-local start
```

### Linux (Ubuntu/Debian)
```bash
# Install Python and pip
sudo apt update
sudo apt install python3.11 python3-pip python3-venv

# Follow Quick Start
pip3 install deepseek-r1-local
deepseek-r1-local download-model
deepseek-r1-local start
```

### Windows
```powershell
# Install Python from python.org
# Then in PowerShell or CMD:

pip install deepseek-r1-local
deepseek-r1-local download-model
deepseek-r1-local start
```

---

## Verification

### Check Installation
```bash
deepseek-r1-local version
```

### Check Model
```bash
ls -la models/tinyllama/
```

### Test Server
```bash
deepseek-r1-local start
# Open browser to http://localhost:5000
# Try: "Hello, how are you?"
```

---

## Troubleshooting

### Command Not Found
```bash
# Make sure pip bin directory is in PATH
export PATH="$HOME/.local/bin:$PATH"

# Or use python -m
python -m deepseek_r1_local.cli start
```

### Model Download Fails
```bash
# Check internet connection
# Try manual download
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('TinyLlama/TinyLlama-1.1B-Chat-v1.0').save_pretrained('models/tinyllama')"
```

### Port Already in Use
```bash
deepseek-r1-local start --port 8080
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## Next Steps

After installation:
1. Read the [README](README.md) for usage instructions
2. Try the Council Mode for complex questions
3. Enable Web Search for current information
4. Check [API docs](docs/api.md) for programmatic usage

---

## Uninstall

```bash
# Remove package
pip uninstall deepseek-r1-local

# Remove models (optional)
rm -rf models/
```
