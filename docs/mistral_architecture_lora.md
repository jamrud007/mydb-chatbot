# Arsitektur Mistral, Ollama, dan LoRA Adapters

Dokumen ini menjelaskan struktur model Mistral yang kita gunakan, mengapa kita menggunakan Ollama, dan bagaimana skenarionya jika menggunakan GPU dengan LoRA Adapters.

## 1. Mengapa Mistral disatukan dengan Ollama?

### Struktur Model Saat Ini
Kita menggunakan model **Mistral 7B** dalam format **GGUF** (`nl2sql-mistral7b-v2.f16.Q4_K_M.gguf`).

- **Mistral 7B**: Ini adalah "otak" dasarnya. Model open-source yang sangat efisien namun powerful.
- **GGUF (GPT-Generated Unified Format)**: Ini adalah format file khusus yang didesain untuk inferensi yang cepat dan efisien, terutama pada CPU atau hardware consumer-grade (seperti laptop biasa).

### Peran Ollama
Ollama berfungsi sebagai **Inference Engine** (Mesin Eksekusi).

1.  **Abstraksi C++**: Di balik layar, menjalankan LLM itu rumit (butuh library C++ seperti `llama.cpp`). Ollama membungkus kerumitan ini menjadi API yang mudah digunakan (`http://localhost:11434`).
2.  **Manajemen Memori**: Ollama otomatis mengatur loading model ke RAM, atau VRAM (jika ada GPU).
3.  **Kompabilitas GGUF**: Ollama sangat optimal untuk menjalankan file GGUF, yang memungkinkan kita menjalankan model 7 Miliar parameter di laptop tanpa GPU server yang mahal.

**Analogi:**
- **Mistral** adalah file film (video).
- **Ollama** adalah Video Player (VLC/Media Player).
- Kita butuh Ollama untuk "memutar" file Mistral agar bisa berinteraksi.

---

## 2. Bagaimana dengan GPU dan Lora Adapters?

User bertanya mengenai **LoRA** (Low-Rank Adaptation) dan penggunaan **GPU**. Ini adalah level optimasi selanjutnya.

### Apa itu LoRA?
Biasanya, fine-tuning model (melatih ulang model agar pintar di domain tertentu, misal SQL) membutuhkan update pada **SEMUA** parameter model (7 Miliar angka). Ini sangat berat dan butuh GPU super mahal.

**LoRA** adalah teknik "pintar":
1.  Model dasar (Base Model, 7B) dibekukan (frozen), tidak diubah.
2.  Kita hanya melatih layer "tambahan" yang sangat kecil (Adapter) di atasnya.
3.  Adapter ini ukurannya kecil (misal hanya 100MB), tapi bisa mengubah perilaku model secara drastis.

### Skenario Deployment dengan GPU + LoRA

Jika Anda memiliki GPU (NVIDIA RTX) dan ingin model yang sangat spesifik (misal sangat jago dialek SQL perusahaan Anda), arsitekturnya akan sedikit berubah tetapi tetap bisa pakai Ollama.

#### Cara Kerja di Ollama:
Ollama mendukung loading Base Model + Adapter secara on-the-fly.

**Di `Modelfile`:**
```dockerfile
# 1. Load Base Model (Mistral 7B standard)
FROM mistral

# 2. Load Adapter LoRA (file .gguf adapter kecil)
ADAPTER ./adapters/my-custom-sql-lora.gguf

# 3. Set Parameter
PARAMETER temperature 0.1
SYSTEM "Anda adalah asisten SQL expert."
```

#### Keuntungan Menggunakan GPU:
Saat ini kita pakai CPU, durasi sekitar **~19 detik**.
Dengan GPU (misal RTX 3060 atau 4090):

1.  **Offloading**: Ollama akan memindahkan layer model dari RAM (CPU) ke VRAM (GPU).
2.  **Kecepatan**: Operasi matriks di GPU jauh lebih cepat.
    -   **CPU**: ~19 detik
    -   **GPU**: Bisa turun ke **< 1 detik** atau **2-3 detik**.
3.  **LoRA Efficiency**: GPU sangat cepat dalam menggabungkan kalkulasi Base Model + LoRA Adapter secara real-time.

### Kesimpulan Perbandingan

| Fitur | Setup Sekarang (CPU Only) | Setup Masa Depan (GPU + LoRA) |
| :--- | :--- | :--- |
| **Model File** | 1 File GGUF Besar (Model yang sudah di-merge) | Base Model GGUF + File Adapter Kecil |
| **Kecepatan** | Lambat (~20s) | Sangat Cepat (< 3s) |
| **Fleksibilitas** | Kaku (harus download model full baru jika ada update) | Fleksibel (cukup ganti file adapter kecil untuk ganti "keahlian") |
| **Cost** | Murah/Gratis (jalan di laptop biasa) | Mahal (butuh kartu grafis NVIDIA dedicated) |

**Rekomendasi:**
Jika latency 19 detik dirasa terlalu lambat untuk production, opsi upgrade paling logis adalah menambahkan GPU dan menggunakan Ollama yang otomatis akan memanfaatkannya. Penerapan LoRA opsional, hanya jika kita ingin melatih ulang model dengan data spesifik perusahaan sendiri.
