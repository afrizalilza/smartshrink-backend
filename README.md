# SmartShrink AI Backend

SmartShrink AI adalah aplikasi web cerdas yang menggabungkan teknik kompresi data konvensional (lossless & lossy) dengan kekuatan machine learning untuk mengoptimalkan ukuran dan efisiensi file berdasarkan konteks dan tujuan penggunaan. Tidak hanya sekadar mengecilkan ukuran, SmartShrink memahami apa yang penting dari sebuah file dan menyesuaikan teknik kompresinya agar tetap efisien tanpa mengorbankan nilai informasi.

---

## Fitur Unggulan
- **Kompresi Kontekstual Berbasis AI:** Menggunakan model ML untuk mengenali jenis file, isi file, dan konteks penggunaan (misal: web, arsip, jaringan terbatas).
- **Auto Compression Profile:** Sistem otomatis memilih teknik terbaik: gzip, Brotli, WebP, HEIC, FLIF, LZMA, atau AI custom sesuai profil penggunaan.
- **Differential Compression untuk File Versi:** Menyimpan perbedaan antar versi file secara efisien (mirip git, mendukung semua tipe file).
- **Real-Time Comparison Dashboard:** Statistik & visualisasi hasil kompresi: ukuran sebelum-sesudah, waktu dekompresi, diff visual, dan efektivitas use-case.
- **Plugin & Integrasi Developer:** Python client/REST API untuk pipeline CI/CD, frontend, atau data pipeline.
- **Data Sensitivity Preserving Mode:** Kompresi dokumen sensitif (log medis/legal) dengan NLP agar informasi penting tidak hilang.
- **Penyimpanan metadata di SQLite (siap PostgreSQL).**
- **Endpoint developer-friendly, siap untuk API key/JWT.**

---

## Struktur Folder
- `main.py` - FastAPI app utama
- `utils.py` - Utilitas kompresi & AI selector
- `utils_ai_selector.py` - AI compression profile (rule/ML)
- `diff_utils.py` - Binary diff/patch
- `nlp_utils.py` - Deteksi entitas sensitif
- `db_utils.py` - DB SQLite untuk metadata
- `smartshrink_client.py` - Python REST API client

---

## Daftar Endpoint Utama

### Upload & Kompresi
- `POST /upload` — Upload file
- `POST /compress` — Kompres file
  - Parameter: `file_id`, `method` (`ai`, `gzip`, `brotli`, `webp`, `pdf_optimize`, `lzma`, `flif`, `heic`), `profile` (`web`, `archive`, `network`, `default`), `sensitive_mode` (bool)
- `GET /result/{file_id}` — Info hasil kompresi
- `GET /download/{file_id}` — Download file hasil

### Statistik & Dashboard
- `GET /compare/{file_id}` — Statistik, rasio, preview, diff, waktu dekompresi

### Batch & Differential
- `POST /batch_compress` — Kompresi banyak file sekaligus
- `POST /diff_compress` —
  - `method=patch`: hasilkan file delta antar dua file
  - `method=restore`: apply patch ke file basis

### Lainnya
- `GET /compression_methods` — Daftar metode kompresi
- `GET /health` — Healthcheck
- `GET /info` — Info build/version

---

## Quickstart Backend

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan backend:
   ```bash
   uvicorn backend.main:app --reload
   ```
3. Akses dokumentasi API otomatis di [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Autentikasi API Key

> **Mulai Mei 2025, seluruh endpoint utama backend (upload, compress, diff, compare, result, download, batch_compress) membutuhkan autentikasi API Key.**

- **Cara pakai:**
    - Sertakan header berikut pada setiap request:
      ```http
      X-API-Key: demo-key-123
      ```
    - Secara default, backend menerima key `demo-key-123` untuk demo/dev.
    - Untuk produksi, set environment variable `API_KEYS` (bisa lebih dari satu, pisahkan dengan koma):
      ```bash
      export API_KEYS="key1,key2,key3"
      ```
      atau pada Windows:
      ```powershell
      $env:API_KEYS="key1,key2,key3"
      ```
    - Jika API Key tidak valid/absen, akan mendapat response 401 Unauthorized.

- **Contoh request dengan curl:**
    ```bash
    curl -X POST http://localhost:8000/upload \
      -H "X-API-Key: demo-key-123" \
      -F "file=@/path/to/file.pdf"
    ```

---

## API Limitations

- Maksimal ukuran file upload: 5MB (bisa diubah di konfigurasi backend)
- File besar akan ditolak dengan status 400.
- Tidak ada deduplikasi file (upload duplikat tetap diterima).

---

## Testing & QA

- Jalankan backend:
  ```bash
  python -m uvicorn backend.main:app --reload
  ```
- Pengujian otomatis endpoint utama:
  ```bash
  python backend/test_api_key.py
  ```
- Pengujian edge case (file besar, file rusak, duplikat, sensitive mode):
  ```bash
  python backend/test_edge_cases.py
  ```
- Semua pengujian harus hasil status 200/202 dan "Semua tes selesai!".

### Jalankan Backend dengan Docker

1. Build image:
   ```bash
   docker build -t smartshrink-backend ./backend
   ```
2. Run container:
   ```bash
   docker run -p 8000:8000 --env-file backend/.env smartshrink-backend
   ```

---

## Contoh Alur Penggunaan

### 1. Upload File
```bash
curl -F "file=@contoh.pdf" http://localhost:8000/upload
```
Response:
```json
{
  "id": "abc123",
  "filename": "contoh.pdf",
  "mime_type": "application/pdf",
  "size": 123456
}
```

### 2. Kompresi File
```bash
curl -X POST -F "file_id=abc123" -F "method=ai" -F "profile=web" http://localhost:8000/compress
```
Response:
```json
{
  "id": "abc123",
  "size_before": 123456,
  "size_after": 67890,
  "method": "webp",
  "elapsed": 0.12
}
```

### 3. Dashboard Statistik
```bash
curl http://localhost:8000/compare/abc123
```
Response:
```json
{
  "id": "abc123",
  "original_filename": "contoh.pdf",
  "compressed_filename": "compressed_abc123_contoh.pdf",
  "size_before": 123456,
  "size_after": 67890,
  "ratio": 0.55,
  "elapsed": 0.12,
  "compression_method": "webp",
  "decompression_time_ms": 10,
  "diff_summary": "No visible difference (stub diff)",
  "preview_before": "data:image/png;base64,...",
  "preview_after": "data:image/png;base64,..."
}
```

### 4. Batch Compression
```python
from smartshrink_client import SmartShrinkClient
client = SmartShrinkClient('http://localhost:8000')
items = [
    {"file_id": "abc123", "method": "ai"},
    {"file_id": "def456", "method": "brotli"}
]
result = client.batch_compress(items)
```

### 5. Differential Compression
```python
# Buat patch delta
client.diff_compress(file_id="ver2", base_file_id="ver1", method="patch")
# Restore file dari patch
client.diff_compress(file_id="ver1", base_file_id="ver1", method="restore", patch_file_id="patch_ver1_ver2.bin")
```

### 6. Sensitive Mode (NLP)
- Jika `sensitive_mode=True` dan file teks, sistem otomatis mendeteksi email, NIK, dsb dan mencatat ke metadata.

---

## Integrasi Pipeline/CI/CD
- Gunakan `smartshrink_client.py` di pipeline Python, notebook, atau workflow automation.
- Semua endpoint siap diakses via REST API (lihat contoh di atas).
- Bisa diintegrasikan ke GitHub Actions, Airflow, dsb.

---

## Keamanan & Best Practice
- Metadata file disimpan di SQLite (siap upgrade ke PostgreSQL)
- Siap untuk penambahan autentikasi API key/JWT (tinggal aktifkan di FastAPI)
- Logging dan audit entitas sensitif otomatis

---

## Referensi & Pengembangan Lanjutan
- Untuk dokumentasi frontend dan arsitektur, lihat `../docs/README_docs.md`
- Untuk pengembangan AI/ML lebih lanjut, gunakan modul `utils_ai_selector.py`
- Untuk plugin ekstensi, gunakan REST API atau kembangkan dari `smartshrink_client.py`

---

> **SmartShrink AI Backend** — Kompresi cerdas, developer-friendly, siap enterprise.
- Form-data: `file_id` (dari upload), `method` (`ai` | `gzip` | `brotli` | `webp` | `pdf_optimize`)

**Response:**
```json
{
  "id": "...",
  "size_before": 123456,
  "size_after": 45678,
  "method": "gzip",
  "elapsed": 0.12
}
```

### 3. Lihat Hasil
**GET** `/result/{file_id}`

**Response:**
```json
{
  "id": "...",
  "original_filename": "contoh.pdf",
  "compressed_filename": "compressed_..._contoh.pdf.gz",
  "mime_type": "application/pdf",
  "size_before": 123456,
  "size_after": 45678,
  "compression_method": "gzip",
  "ratio": 0.37,
  "elapsed": 0.12,
  "download_url": "/download/..."
}
```

### 4. Download Hasil
**GET** `/download/{file_id}`
- Mengunduh file hasil kompresi.

## Tipe File yang Didukung
- Teks (`text/*`)
- PDF (`application/pdf`)
- Gambar (`image/jpeg`, `image/png`, `image/webp`)
- Dokumen (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- ZIP (`application/zip`)

## Pilihan Kompresi

- `gzip`: Kompresi gzip
- `brotli`: Kompresi brotli
- `webp`: Kompresi gambar ke WebP
- `ai`: AI selector otomatis

## Catatan
- Maksimal ukuran file upload: 10MB
- Semua metadata hasil tersimpan di database SQLite (`results_db.sqlite3`)
- Kompresi WebP membutuhkan library Pillow (`pip install pillow`)
- Kompresi Brotli membutuhkan library brotli (`pip install brotli`)

---

## Changelog
- **2023-02-20**: Menghapus metode 'auto' (rule-based) dan menggantinya dengan 'AI (Otomatis)'.
- **2023-02-15**: Menambahkan fitur kompresi batch dan differential.
- **2023-02-10**: Mengupdate dokumentasi untuk mencakup semua endpoint dan fitur.
