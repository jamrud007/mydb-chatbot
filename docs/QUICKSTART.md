# Quick Start Guide - MySQL Chatbot

## Prerequisites
- Python 3.11+
- MySQL 5.7+
- Ollama installed (optional, for local AI)

## 5-Minute Setup

### 1. Setup Project
```bash
cd mysql-chatbot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Database
```bash
mysql -u root -p < sample_db\create_sample_db.sql
mysql -u root -p ecommerce_olist -e "SHOW TABLES;"
```

### 3. Configure Environment
```bash
copy .env.example .env
```
Edit `.env`:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `AI_PROVIDER` (`ollama` / `gemini` / `openai`)

### 4. Run Application
```bash
# Terminal 1 - Backend API
python main.py

# Terminal 2 - Frontend Dashboard
streamlit run streamlit_app.py
```

### 5. Open Browser
- Streamlit UI: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`

## Troubleshooting

**Ollama not connecting?**
```bash
curl http://localhost:11434/api/tags
```

**MySQL connection error?**
- Check DB credentials in `.env`
- Verify MySQL service is running

**Dependency issues?**
```bash
pip install -r requirements.txt --upgrade
```

For detailed setup, see [README.md](README.md) and [OLLAMA_SETUP.md](OLLAMA_SETUP.md).
