# Production Configuration Notes

## Recommended Settings

```env
DEBUG=False
READ_ONLY_MODE=True
ENABLE_DATA_ANALYSIS=False
```

## Why `DEBUG=False`
- Avoid unnecessary reload behavior in production
- Keep process startup predictable
- Reduce accidental repeated init calls to external providers

## Run Services

```bash
# Backend
python main.py

# Frontend
streamlit run streamlit_app.py
```

## Optional: Use Ollama During Development

```env
AI_PROVIDER=ollama
```

This avoids cloud API quota usage while testing frequently.
