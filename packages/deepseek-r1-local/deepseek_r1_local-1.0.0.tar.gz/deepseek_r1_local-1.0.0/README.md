# 🚀 DeepSeek R1 Local Web UI

An offline, privacy-focused AI chat application with TinyLlama model, Web Search Integration, and Council Deliberation System optimized for CPU performance.

## Features
- 🤖 Offline AI Chat (TinyLlama-1.1B, CPU-optimized)
- 🔍 Web Search Integration (DuckDuckGo)
- 🏛️ Council Deliberation System (5 AI personas, voting)
- ⚡ Performance Optimizations (response caching, fast inference)
- 🔒 100% Privacy (all processing local)

## Council Members
- 🧠 Dr. Logic (Analytical Rationalist)
- 📚 Professor Sage (Historical Scholar)
- 💡 Innovator Nova (Creative Visionary)
- ❤️ Advocate Heart (Empathetic Humanist)
- 🎯 Pragmatist Ray (Practical Realist)

## Installation

### 1. Install via pip (when published)
```bash
pip install deepseek-r1-local
```

### 2. Download Model
```bash
deepseek-r1-local download-model
```

### 3. Start Server
```bash
deepseek-r1-local start
```

### 4. Open Browser
Go to: http://localhost:5000

## Usage
- Use toggles for Web Search and Council Mode in the UI
- Ask questions, get AI and council responses
- Council mode: 5 personas deliberate, vote, and select a winning proposal

## Python API Example
```python
from deepseek_r1_local import ModelManager, Council, WebSearcher

model = ModelManager()
model.load_model()
response = model.generate_response("Hello!", max_length=50)

council = Council()
results = council.deliberate("Should I learn Rust or Go?", model)
print(council.format_results(results))

searcher = WebSearcher()
results = searcher.search("Python tutorials", max_results=5)
print(searcher.format_search_results(results))
```

## File Structure
```
deepseek_r1-local/
├── deepseek_r1_local/
│   ├── __init__.py
│   ├── app.py
│   ├── cli.py
│   └── templates/
│       └── index.html
├── models/           # Model files (downloaded)
├── setup.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
├── MANIFEST.in
├── CHANGELOG.md
├── INSTALL.md
├── QUICKREF.md
├── PACKAGE_GUIDE.md
├── build.sh
├── test_package.py
```

## Troubleshooting
- If model fails to load, re-run `download-model`
- Use `deepseek-r1-local start --port 8080` for a different port
- For help: `deepseek-r1-local --help`

## License
MIT License

## Links
- PyPI: https://pypi.org/project/deepseek-r1-local/
- GitHub: https://github.com/yourusername/deepseek-r1-local
