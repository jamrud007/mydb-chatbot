# vLLM Deployment - Quick Pointer

MyDB Chatbot can run against a self-hosted vLLM server (Mistral-7B + LoRA) instead of a cloud LLM.

## Docker (recommended)

See [docker/README_VLLM.md](docker/README_VLLM.md) for the full guide (prerequisites, GPU setup, modes, troubleshooting).

```bash
cp docker/.env.docker.vllm.example .env
docker-compose --profile vllm up -d --build
```

## Bare-metal / development

1. Run a vLLM OpenAI-compatible server locally (port 8080), with the `nl2sql-json-v2-adapter-manual/` LoRA adapter loaded.
2. Copy [`.env.vllm.example`](.env.vllm.example) to `.env` and adjust `DB_*` settings.
3. Start the backend and frontend as usual:
   ```bash
   python main.py
   streamlit run streamlit_app.py
   ```

Open http://localhost:8501 once both vLLM and the backend report healthy.
