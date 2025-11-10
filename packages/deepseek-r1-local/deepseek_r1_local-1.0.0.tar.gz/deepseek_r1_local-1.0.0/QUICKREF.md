# 🚀 DeepSeek R1 Local - Quick Reference

## Installation Commands

```bash
# Install from PyPI
pip install deepseek-r1-local

# Install from source
git clone <repo-url>
cd deepseek-r1-local
pip install -e .
```

## CLI Commands

```bash
# Download model (first time, ~2.2GB)
deepseek-r1-local download-model

# Start server (default: localhost:5000)
deepseek-r1-local start

# Start on custom port
deepseek-r1-local start --port 8080

# Start on all interfaces
deepseek-r1-local start --host 0.0.0.0

# Show version
deepseek-r1-local version

# Show info
deepseek-r1-local info

# Debug mode
deepseek-r1-local start --debug
```

## Web UI Features

| Feature | Toggle | Description |
|---------|--------|-------------|
| AI Chat | Default | Standard chat with TinyLlama |
| Web Search | 🔍 | Real-time DuckDuckGo search |
| Council Mode | 🏛️ | 5 personas deliberate and vote |

## Council Members

| Persona | Role | Voting Style |
|---------|------|--------------|
| Dr. Logic | Analytical | Data-driven, systematic |
| Prof. Sage | Historical | Precedent-focused |
| Nova | Creative | Bold, unconventional |
| Heart | Empathetic | Compassionate, ethical |
| Ray | Practical | Action-oriented, feasible |

## Python API

```python
from deepseek_r1_local import ModelManager, Council, WebSearcher

# Initialize
model = ModelManager()
model.load_model()

# Generate response
response = model.generate_response(
    "Your question",
    max_length=100,
    temperature=0.7
)

# Council deliberation
council = Council()
results = council.deliberate("Complex question", model)
formatted = council.format_results(results)

# Web search
searcher = WebSearcher()
results = searcher.search("Query", max_results=5)
```

## File Structure

```
deepseek-r1-local/
├── deepseek_r1_local/     # Package directory
│   ├── __init__.py        # Package init
│   ├── app.py             # Flask app
│   ├── cli.py             # CLI commands
│   └── templates/         # HTML templates
├── models/                # Model storage
├── setup.py               # Setup script
├── pyproject.toml         # Modern packaging
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## Troubleshooting

```bash
# Check installation
deepseek-r1-local version

# Check model exists
ls models/tinyllama/

# Re-download model
deepseek-r1-local download-model

# Use different port
deepseek-r1-local start --port 8080

# Check server status
curl http://localhost:5000/api/status
```

## Performance Tips

- First query is slower (model warmup)
- Cached responses are instant (6M+ x faster)
- Council mode takes 15-30 seconds
- Reduce `max_length` for faster responses
- Close other apps if running out of memory

## URLs

- Web UI: http://localhost:5000
- Status API: http://localhost:5000/api/status
- Chat API: http://localhost:5000/api/chat

## Common Questions

**Q: How much RAM needed?**  
A: 8GB minimum, 16GB recommended

**Q: Can I use GPU?**  
A: Currently CPU-only, GPU support planned

**Q: How to update?**  
A: `pip install --upgrade deepseek-r1-local`

**Q: Is it really offline?**  
A: Yes, except Web Search feature (optional)

**Q: Council taking too long?**  
A: Normal - runs 5+ AI generations with voting

## Exit

Press `Ctrl+C` in terminal to stop server

---

**Quick Start**: `pip install deepseek-r1-local && deepseek-r1-local download-model && deepseek-r1-local start`
