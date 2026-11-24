# Industrial Improvement Notes

## 1. Reliability and Architecture
- Pisahkan service: `api`, `worker`, `scheduler` (jangan semua di satu proses).
- Tambah message queue (Redis/RabbitMQ) untuk task berat (analisis, report, email).
- Terapkan retry, timeout, circuit breaker per provider LLM.

## 2. Security Hardening
- Wajib RBAC (admin/analyst/viewer), bukan hanya login.
- Secrets pakai vault/secret manager, bukan `.env` di server.
- SQL guardrail lebih ketat: allowlist table/column per role + query cost limit.
- Audit log immutable untuk semua query dan export data.

## 3. LLM Governance
- Versioning prompt + model config per release.
- Tambah eval suite NL?SQL (akurasi, safety, latency, cost) di CI.
- Fallback policy jelas (OpenAI/Gemini/Ollama) dengan health-based routing.
- PII redaction sebelum kirim ke cloud LLM.

## 4. Data and Query Safety
- Query sandbox: read-only user DB, row limit, execution timeout, cancel support.
- Schema drift detection otomatis + alert kalau struktur DB berubah.
- Tambah semantic layer (metric definitions) agar jawaban konsisten bisnis.

## 5. Observability (Wajib)
- OpenTelemetry end-to-end (request -> LLM -> DB).
- Dashboard SLI/SLO: success rate, p95 latency, error rate, cost/query.
- Alerting production (PagerDuty/Slack) untuk 5xx spike, quota habis, slow query.

## 6. Testing and Quality Gate
- Contract test API, integration test DB+LLM mock, chaos test provider gagal.
- Golden test set untuk 100-500 pertanyaan bisnis real.
- CI gate: lint + type check + security scan + test coverage threshold.

## 7. Deployment and Operations
- Containerize rapi + healthcheck + graceful shutdown.
- Deploy ke Kubernetes/ECS dengan autoscaling.
- Blue/green atau canary release.
- Backup/restore + DR plan (RPO/RTO jelas).

## 8. Product Readiness
- Multi-tenant isolation (kalau untuk banyak client/perusahaan).
- Admin panel: usage, quota, model selection, export governance.
- Billing/cost center per user/team.
- Dokumentasi operasi: runbook incident, onboarding, SOP release.
