# MySQL Chatbot - Ollama Setup Guide

## Using Ollama for Local AI

Ollama lets you run LLMs locally for development and low-cost deployment.

## Installation

### Windows
```bash
winget install Ollama.Ollama
```

### Linux/Mac
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Quick Start

1. Start server
```bash
ollama serve
```

2. Pull model
```bash
ollama pull llama3.1
```

3. Test model
```bash
ollama run llama3.1 "Hello"
```

## Configuration (.env)

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# Optional fallback
AI_FALLBACK_PROVIDERS=gemini
GEMINI_API_KEY=your_key_here
```

## Run Chatbot Stack

```bash
# Backend API
python main.py

# Frontend dashboard
streamlit run streamlit_app.py
```

Open:
- `http://localhost:8501` (UI)
- `http://localhost:8000/docs` (API docs)

## Troubleshooting

**Model not found?**
```bash
ollama list
ollama pull llama3.1
```

**Out of memory?**
- Use `llama3.2:3b`
- Close heavy apps

**Connection check**
```bash
curl http://localhost:11434/api/tags
```
