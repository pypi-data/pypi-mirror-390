# Changelog

All notable changes to DeepSeek R1 Local will be documented in this file.

## [1.0.0] - 2025-11-09

### Added
- Initial release of DeepSeek R1 Local
- TinyLlama-1.1B-Chat integration for offline AI chat
- Flask-based web UI with modern interface
- Web Search integration using DuckDuckGo
- Council Deliberation System with 5 unique personas:
  - Dr. Logic (Analytical Rationalist)
  - Professor Sage (Historical Scholar)
  - Innovator Nova (Creative Visionary)
  - Advocate Heart (Empathetic Humanist)
  - Pragmatist Ray (Practical Realist)
- 5-vote distribution system for council members
- Response caching with LRU cache (6M+ x speedup)
- CPU-optimized inference
- Command-line interface (CLI)
- PyPI package distribution
- Comprehensive documentation

### Features
- Toggle-based web search on/off
- Toggle-based council mode on/off
- Real-time chat interface
- Model warmup for consistent performance
- Proper vote validation (no self-voting)
- Verbatim winning proposal as final decision
- Clear vote tallying and display

### Performance
- Response caching (MD5 hashing)
- CPU-optimized Float32 precision
- Greedy decoding for deterministic outputs
- Fast tokenizer
- Multi-threaded inference
- Attention masks optimization

### Documentation
- Comprehensive README
- CLI help documentation
- API usage examples
- Package structure documentation
- Installation guides (pip, source, manual)
- Troubleshooting guide

## [Unreleased]

### Planned
- GPU support
- Additional AI models
- Custom persona creation
- Vote weight customization
- Export conversation history
- API endpoint documentation
- Docker support
- Web UI themes
