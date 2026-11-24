# Ringkasan Singkat — Progress 2–8 Juni 2026 (Day 8–14, Scalability Sprint)

> Versi padat: 1 slide = 1 hari, maks 3 poin. Untuk versi lengkap dengan tabel & detail teknis, lihat `RINGKASAN_WORKLOG_2-8_JUNI_PPTX.md`.

---

## Slide 1 — 2 Juni: Audit Proses Berat (Day 8)

- Identifikasi 7 proses backend yang berjalan sinkron dan memblokir user — yang paling berat: **auto-analysis LLM** (10–60 detik, padahal data sudah siap).
- Hasil audit jadi peta jalan untuk Day 9–10: mana yang bisa dipindah ke background, mana yang butuh streaming.
- **Kenapa penting:** tanpa audit ini, perbaikan berikutnya cuma tebak-tebakan — sekarang ada prioritas yang jelas dan terukur.

---

## Slide 2 — 3 Juni: Background Task untuk Auto-Analysis (Day 9)

- Pindahkan proses analysis LLM ke background task + buat endpoint polling hasil.
- **Response `/api/execute/` turun dari ~62 detik → ~2 detik.**
- **Kenapa penting:** user langsung lihat data dalam 2 detik, tanpa nunggu LLM — dan tanpa nambah infrastruktur baru.

---

## Slide 3 — 4 Juni: Pagination Konsisten + Optimasi Query Executor (Day 12)

- Samakan aturan limit/pagination di semua endpoint daftar (maks data per request tervalidasi).
- Precompile pola regex validasi SQL — hilangkan overhead "compile ulang" di setiap request.
- **Kenapa penting:** API jadi konsisten dan lebih cepat tanpa mengubah perilaku yang sudah ada.

---

## Slide 4 — 5 Juni: Hidupkan MetricsCollector + Latency Baseline (Day 14)

- Temuan: sistem monitoring (`MetricsCollector`) sudah lengkap dibangun, tapi **tidak pernah menerima data** — `/api/metrics` selalu menunjukkan angka 0.
- Sambungkan ke jalur eksekusi query & LLM — sekarang `/api/metrics` menampilkan data nyata.
- **Kenapa penting:** sekarang kita bisa benar-benar mengukur performa sistem, bukan cuma menebak.

---

## Slide 5 — 8 Juni: Slow Query Guard + Uji Beban Ringan (Day 13)

- Verifikasi guard query lambat (>5 detik) — sudah aktif dan menerima data nyata.
- Uji beban ringan dengan request bersamaan — temuan: di atas ~20 user bersamaan, latency naik **~10x** karena antrean di server (bukan di database).
- **Kenapa penting:** ini sinyal awal yang perlu diantisipasi sebelum demo — jumlah user bersamaan bisa memengaruhi kecepatan respons.

---

## Slide 6 — Ringkasan Dampak

- **Response time turun drastis:** `/api/execute/` dari 62 detik → 2 detik.
- **Visibility penuh:** monitoring performa & deteksi query lambat sekarang aktif dan berfungsi.
- **Temuan untuk ditindaklanjuti:** kapasitas server perlu ditingkatkan agar siap menampung beberapa user bersamaan saat demo.
