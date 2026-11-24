# 📊 API Usage Analysis - Gemini API Calls Today

## 🔍 Breakdown Penggunaan API

### API Key #1: `AIzaSyAmX-REDACTED_API_KEY_1` (EXPIRED)
**Status**: Quota exceeded (20/20)

### API Key #2: `AIzaSyDm2-REDACTED_API_KEY_2` (EXPIRED)
**Status**: Quota exceeded (20/20)

---

## 📝 Estimasi Penggunaan API Calls

### 1. **Testing & Development** (~15 calls)

#### a. Test API Connection (3-5 calls)
- `test_gemini_api.py` dijalankan beberapa kali: **~3 calls**
- `list_gemini_models.py` untuk cek model: **~1 call**
- `test_api_config.py` verification: **~1 call**

#### b. Server Initialization (5-10 calls)
Setiap kali server start/restart, ada test connection:
- Initial start: **1 call**
- Debug mode restart (auto-reload): **1 call per restart**
- Manual restart karena troubleshooting: **~5-8 calls**

**Estimasi**: FastAPI/uvicorn reload mode dengan auto-reload bisa trigger banyak restart!

#### c. Failed Attempts & Retries (2-3 calls)
- Connection timeout retries
- Model availability checks

### 2. **User Testing di Browser** (~5 calls)

Dari browser subagent logs:
- Page load & health check: **multiple calls**
- User mencoba send message: **~3-5 calls** (semua gagal karena quota)

---

## 🎯 Penyebab Utama: **Debug Mode + Multiple Restarts**

### FastAPI/uvicorn reload mode Issue:
```python
# main.py
DEBUG=True  # ← Ini yang bikin masalah!
```

**Efek**:
- Setiap file save → **auto restart**
- Setiap restart → **test connection (1 API call)**
- Kita edit banyak file → **banyak restart**

**Estimasi restart hari ini**: ~15-20x
- Edit `visualization_helper.py`: +1 restart
- Edit `csv_exporter.py`: +1 restart  
- Edit `chatbot_handler.py`: +1 restart
- Edit `main.py`: +1 restart
- Edit `chat.js`: +1 restart (server detect change)
- Manual restart: +10x

---

## 📊 Breakdown Calls per Aktivitas

| Aktivitas | Calls | Timestamp (approx) |
|-----------|-------|-------------------|
| Test API pertama kali | 3-5 | ~09:00 |
| Server initial start | 1 | ~09:15 |
| Debug restarts (auto) | 10-15 | ~09:15-09:40 |
| Browser testing | 3-5 | ~09:19, 09:24, 09:35 |
| Manual troubleshooting | 5-8 | ~09:30-09:50 |
| **TOTAL** | **~25-35** | |

**Quota**: 20 per day per API key

---

## ⚠️ Kesalahan Kita:

### 1. **DEBUG=True di Production**
Seharusnya:
```env
DEBUG=False  # Disable auto-reload
```

### 2. **Tidak Ada Rate Limiter di Test Connection**
File `llm_factory.py` test connection tanpa rate limit check:
```python
# Setiap start server:
client.models.generate_content(...)  # 1 API call!
```

### 3. **Multiple Server Instances**
Sempat ada 3 proses Python running → 3x initialization calls

---

## 💡 Solusi untuk Menghindari Quota Habis:

### 1. **Disable Debug Mode for Production**
```env
# .env
DEBUG=False
```

### 2. **Cache Connection Test**
Jangan test connection setiap restart:
```python
# Cek cache dulu
if os.path.exists('.connection_ok'):
    # Skip test
else:
    # Test & create cache
```

### 3. **Use Ollama for Development**
```env
AI_PROVIDER=ollama  # No quota!
```

### 4. **Rate Limiter di Init**
```python
if not rate_limiter.can_make_request():
    # Use cached/skip test
```

---

## 📈 Quota Info

**Free Tier**:
- **20 RPD** (Requests Per Day) ← kita exceed ini
- 5 RPM (Requests Per Minute)
- 250K TPM (Tokens Per Minute)

**Reset**: Setiap 24 jam (midnight UTC atau regional)

---

## 🎯 Kesimpulan

**Total API calls hari ini**: ~25-35 calls (estimate)
**Quota limit**: 20 calls per day
**Excess**: ~5-15 calls over limit

**Penyebab utama**:
1. 🔴 FastAPI/uvicorn reload mode auto-reload (10-15 calls)
2. 🔴 Manual restarts saat troubleshooting (5-8 calls)
3. 🔴 Test scripts (3-5 calls)
4. 🟡 Browser testing (3-5 calls)

**Lesson learned**: 
- Disable DEBUG mode saat development
- Use Ollama untuk unlimited testing
- Implement connection cache
- Monitor rate limit before each call

---

**Next Steps**:
1. Set `DEBUG=False` di `.env`
2. Wait 24h untuk quota reset
3. Atau gunakan Ollama (unlimited)

Mau saya set DEBUG=False sekarang?

