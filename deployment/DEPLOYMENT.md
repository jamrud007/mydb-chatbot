# FastAPI + Streamlit Deployment Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start FastAPI Backend
```bash
# Terminal 1
uvicorn main:app --reload --port 8000
```

**API will be available at:**
- API: `http://localhost:8000`
- Swagger UI (Interactive Docs): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Start Streamlit Dashboard
```bash
# Terminal 2
streamlit run streamlit_app.py
```

**Dashboard will open at:** `http://localhost:8501`

---

## Testing

### Test FastAPI Endpoints

1. **Health Check**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Chat (Text-to-SQL)**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "Top 5 produk by revenue", "user_id": "test"}'
   ```

3. **Execute Query**
   ```bash
   curl -X POST "http://localhost:8000/api/execute/0?user_id=test"
   ```

4. **List Results**
   ```bash
   curl http://localhost:8000/api/results
   ```

### Test Streamlit

1. Open `http://localhost:8501`
2. Go to **Chat** tab
3. Enter: "Tampilkan 5 kategori produk dengan total pendapatan tertinggi"
4. Click **Generate SQL**
5. Click **Execute Query #1**
6. Go to **Visualization** tab → See Plotly chart
7. Go to **Data Table** tab → Download CSV/Excel

---

## Architecture

```
┌────────────────────────────────────────────┐
│  User Workflow                             │
├────────────────────────────────────────────┤
│                                            │
│  1. Streamlit UI (http://localhost:8501)   │
│     ↓                                      │
│  2. FastAPI Backend (http://localhost:8000)│
│     ├─ POST /api/chat                      │
│     ├─ POST /api/execute/{index}           │
│     ├─ GET  /api/results                   │
│     └─ GET  /api/results/{id}              │
│     ↓                                      │
│  3. MySQL Database                         │
│                                            │
└────────────────────────────────────────────┘
```

---

## Features

### FastAPI Backend
- ✅ Auto-generated API docs (`/docs`)
- ✅ Type validation with Pydantic
- ✅ CORS enabled for Streamlit
- ✅ Results caching (1 hour TTL)
- ✅ Rate limiting
- ✅ CSV export

### Streamlit Dashboard
- ✅ Chat interface for natural language queries
- ✅ Recent queries browser
- ✅ Interactive Plotly charts (Bar, Line, Pie, Scatter, Combo)
- ✅ Data table with column filters
- ✅ CSV & Excel export
- ✅ Real-time API status monitoring

---

## Troubleshooting

### FastAPI won't start
- Check if port 8000 is already in use
- Verify `.env` file has correct database credentials
- Check logs in `logs/chatbot.log`

### Streamlit can't connect to API
- Ensure FastAPI is running on port 8000
- Check API endpoint in Streamlit sidebar (should be `http://localhost:8000`)
- Verify CORS settings in `main.py`

### Charts not rendering
- Check browser console for errors
- Verify `visualization` object in API response
- Try a different query (some queries may not be visualizable)

---

## Production Deployment

### Deploy FastAPI
```bash
# Using gunicorn + uvicorn workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Deploy Streamlit
```bash
# Cloud (Streamlit Cloud, AWS, etc.)
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Environment Variables
Create `.env` file with:
```
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=your_db_name
DB_USER=your_user
DB_PASSWORD=your_password
GEMINI_API_KEY=your_key
```
