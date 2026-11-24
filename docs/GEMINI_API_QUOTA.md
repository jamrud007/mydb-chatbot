# 📋 Gemini API Quota Reference

Dokumentasi batas quota untuk Google Gemini API berdasarkan tier yang digunakan.

---

## 1. 🆓 Paket Gratis (Free Tier)

Cocok untuk eksperimen atau aplikasi skala kecil.

| Metric | Limit | Deskripsi |
|--------|-------|-----------|
| **RPM** | 15 RPM | Requests Per Minute (Request per menit) |
| **TPM** | 1 Juta TPM | Tokens Per Minute (Token per menit) |
| **RPD** | 1,500 RPD | Requests Per Day (Request per hari) |

### ⚠️ Catatan Penting:

- Kuota harian (RPD) sering kali **dibagi (shared)** dengan model ringan lainnya seperti `Flash-Lite`
- **Privasi**: Data input/output **dapat digunakan oleh Google untuk melatih model**
- Cocok untuk development dan testing
- Tidak memerlukan billing/kartu kredit

---

## 2. 💳 Paket Berbayar (Pay-as-you-go)

Menggunakan Google Cloud Billing via **Vertex AI** atau **AI Studio dengan billing aktif**.

| Metric | Limit | Deskripsi |
|--------|-------|-----------|
| **RPM** | 1,000+ RPM | Requests Per Minute (bisa ditingkatkan dengan request) |
| **TPM** | 4 Juta+ TPM | Tokens Per Minute |
| **RPD** | Unlimited ♾️ | Tidak dibatasi |

### ✅ Keuntungan:

- **Privasi**: Data Anda **TIDAK digunakan untuk pelatihan model**
- Enterprise-grade security
- Quota lebih besar dan bisa di-scale up
- Cocok untuk production applications
- Dedicated support

---

## 📊 Perbandingan Cepat

| Feature | Free Tier | Paid Tier |
|---------|-----------|-----------|
| RPM | 15 | 1,000+ |
| TPM | 1M | 4M+ |
| RPD | 1,500 | ♾️ Unlimited |
| Data Privacy | ❌ Bisa digunakan | ✅ Private |
| Cost | $0 | Pay per use |
| Best For | Development | Production |

---

## 🔍 Cara Cek Usage Anda

1. Buka: https://aistudio.google.com/
2. Login dengan akun Google yang memiliki API key
3. Lihat dashboard untuk melihat current usage
4. Monitor quota remaining untuk menghindari limit

---

## 💡 Tips Menggunakan Free Tier

1. **Cache responses** untuk mengurangi request berulang
2. **Batch requests** jika memungkinkan
3. **Gunakan model yang sesuai**:
   - `gemini-2.5-flash` atau `gemini-flash-latest` untuk task ringan
   - `gemini-pro-latest` untuk task kompleks (tapi konsumsi quota lebih besar)
4. **Monitor usage** secara berkala
5. **Implement rate limiting** di aplikasi Anda

---

## 🚀 Upgrade ke Paid Tier

Jika Anda butuh quota lebih besar:

1. Visit: https://console.cloud.google.com/
2. Enable billing untuk project Anda
3. Set up Vertex AI atau upgrade AI Studio
4. Configure budget alerts untuk kontrol biaya

---

**Last Updated**: 2026-01-13
