from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Header, Depends, Body
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import PlainTextResponse
import logging
from typing import Optional
from enum import Enum
import os

# API Key Auth
API_KEYS = os.environ.get('API_KEYS', 'demo-key-123').split(',')
def api_key_auth(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")

class CompressionMethod(str, Enum):
    ai = "ai"

    gzip = "gzip"
    brotli = "brotli"
    webp = "webp"
    pdf_optimize = "pdf_optimize"
import os
import shutil
import uuid
import mimetypes
import time
from backend import utils
from backend import db_utils

db_utils.init_db()

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../storage'))
RESULTS_DIR = os.path.join(STORAGE_DIR, 'results')

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Logging ke file
logging.basicConfig(
    filename="backend.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Rate limiter (slowapi)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="SmartShrink AI Backend")
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request, exc):
    return PlainTextResponse("Rate limit exceeded", status_code=429)

# CORS: hanya izinkan frontend production (bisa diatur via env)
FRONTEND_ORIGINS = os.environ.get('FRONTEND_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import json









@app.post("/upload")
def upload_file(file: UploadFile = File(...), x_api_key: str = Depends(api_key_auth)):
    # Generate unique ID
    file_id = str(uuid.uuid4())
    file_path = os.path.join(STORAGE_DIR, file_id + '_' + file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Validasi ukuran file maksimal 500MB
    MAX_SIZE_MB = 500
    if os.path.getsize(file_path) > MAX_SIZE_MB * 1024 * 1024:
        os.remove(file_path)
        raise HTTPException(status_code=413, detail=f"File terlalu besar (maksimal {MAX_SIZE_MB}MB)")
    # Detect MIME type
    mime_type = mimetypes.guess_type(file.filename)[0] or file.content_type
    ext = file.filename.lower()
    # Fallback deteksi MIME berbasis ekstensi
    if ext.endswith('.rar'):
        mime_type = 'application/x-rar-compressed'
    elif ext.endswith('.7z'):
        mime_type = 'application/x-7z-compressed'
    elif ext.endswith('.tar'):
        mime_type = 'application/x-tar'
    elif ext.endswith('.gz'):
        mime_type = 'application/gzip'
    elif ext.endswith('.doc'):
        mime_type = 'application/msword'
    elif ext.endswith('.xls'):
        mime_type = 'application/vnd.ms-excel'
    elif ext.endswith('.ppt'):
        mime_type = 'application/vnd.ms-powerpoint'
    elif ext.endswith('.xlsx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif ext.endswith('.pptx'):
        mime_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    elif ext.endswith('.gif'):
        mime_type = 'image/gif'
    elif ext.endswith('.tiff'):
        mime_type = 'image/tiff'
    elif ext.endswith('.bmp'):
        mime_type = 'image/bmp'
    elif ext.endswith('.csv'):
        mime_type = 'text/csv'
    elif ext.endswith('.json'):
        mime_type = 'application/json'
    elif ext.endswith('.xml'):
        mime_type = 'application/xml'
    elif ext.endswith('.html'):
        mime_type = 'text/html'
    # Simpan metadata ke SQLite
    db_utils.save_result(file_id, {
        "file_path": file_path,
        "original_filename": file.filename,
        "mime_type": mime_type,
        "status": "uploaded",
        "size_before": os.path.getsize(file_path)
    })
    return {
        "file_id": file_id,
        "filename": file.filename,
        "mime_type": mime_type
    }

@app.post("/compress")
@limiter.limit("30/minute")
def compress_file(request: Request, file_id: str = Form(...), method: CompressionMethod = Form(...), sensitive_mode: bool = Form(False), profile: str = Form('default'), x_api_key: str = Depends(api_key_auth)):
    """
    Kompres file yang sudah diupload dengan metode tertentu.
    Pilihan method: ai, auto, gzip, brotli, webp, pdf_optimize, lzma, flif, heic
    Optional: sensitive_mode (True/False) untuk lossless compression dokumen sensitif.
    Optional: profile (web, archive, network, default) untuk auto profile kompresi.
    """

    # Validate file_id
    entry = db_utils.load_result(file_id)
    if not entry:
        raise HTTPException(status_code=404, detail="File not found")
    input_path = entry["file_path"]
    mime_type = entry.get("mime_type")
    file_size = entry.get("size_before")
    # Pilih metode kompresi (AI selector stub jika method==ai, auto_select_compression jika auto)
    chosen_method = method.value
    # Use global import for utils
    if method.value == "ai":
        chosen_method = utils.ai_selector_stub(mime_type, file_size, entry['original_filename'], profile)
    elif method.value == "auto":
        chosen_method = utils.auto_select_compression(mime_type)
    # Dukungan stub algoritma baru
    if chosen_method == "lzma":
        # TODO: Implementasi LZMA kompresi
        raise HTTPException(status_code=501, detail="LZMA compression not implemented yet.")
    if chosen_method == "flif":
        # TODO: Implementasi FLIF kompresi
        raise HTTPException(status_code=501, detail="FLIF compression not implemented yet.")
    if chosen_method == "heic":
        # TODO: Implementasi HEIC kompresi
        raise HTTPException(status_code=501, detail="HEIC compression not implemented yet.")
    # Output file: gunakan ekstensi asli
    original_ext = os.path.splitext(entry['original_filename'])[1]
    output_filename = f"compressed_{file_id}_{entry['original_filename']}"
    output_path = os.path.join(RESULTS_DIR, output_filename)

    # Analisis NLP jika sensitive_mode dan file teks
    sensitive_entities = None
    if sensitive_mode and (mime_type.startswith("text/") or original_ext.lower() in [".txt", ".csv", ".json", ".xml", ".html"]):
        from backend import nlp_utils
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read(100000)
            sensitive_entities = nlp_utils.detect_sensitive_entities(text)
        except Exception:
            sensitive_entities = None
    # Kompresi sesuai format asli
    # PDF: use pdf_optimize (now with real optimization)
    if mime_type == "application/pdf" or original_ext.lower() == ".pdf":
        from backend import pdf_optimize
        if not output_path.lower().endswith('.pdf'):
            output_path += '.pdf'
        method_used = pdf_optimize.compress_pdf(input_path, output_path)
        chosen_method = method_used
    elif mime_type.startswith("image/"):
        if not output_path.lower().endswith('.webp'):
            output_path += '.webp'
        utils.compress_webp(input_path, output_path, quality=80)
        chosen_method = "webp"
    elif mime_type == "video/mp4" or original_ext.lower() == ".mp4":
        try:
            import subprocess
            # Pastikan output_path unik dan tidak overwrite
            if not output_path.lower().endswith('_compressed.mp4'):
                output_path = output_path.replace('.mp4', '_compressed.mp4')
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-b:v", "1000k",
                "-b:a", "128k",
                output_path
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            chosen_method = "ffmpeg"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kompresi MP4 gagal: {e}")
    elif original_ext.lower() in [".txt", ".csv", ".json", ".xml", ".html"] or mime_type in ["text/plain", "text/csv", "application/json", "application/xml", "text/html"] or mime_type.startswith("text/"):
        try:
            if not output_path.lower().endswith('.gz'):
                output_path += '.gz'
            utils.compress_gzip(input_path, output_path)
            chosen_method = "gzip"
            logging.info(f"Kompresi file text/markup ({entry['original_filename']}) sukses: {output_path}")
        except Exception as e:
            logging.error(f"Kompresi file text/markup gagal: {entry['original_filename']} | Error: {e}")
            raise HTTPException(status_code=500, detail=f"Kompresi file text/markup gagal: {e}")
    # Images: compress to WebP
    elif mime_type.startswith("image/"):
        if not output_path.lower().endswith('.webp'):
            output_path += '.webp'
        utils.compress_webp(input_path, output_path, quality=80)
        chosen_method = "webp"
    # Office files: compress with brotli
    elif original_ext.lower() in [".pptx", ".docx", ".xlsx"]:
        try:
            from backend.office_optimize import optimize_office_images
            optimized = optimize_office_images(input_path, output_path, quality=75)
            chosen_method = "office_optimize"
            logging.info(f"Optimized Office file: {entry['original_filename']} -> {output_path} (images compressed: {optimized})")
        except Exception as e:
            import shutil
            shutil.copyfile(input_path, output_path)
            chosen_method = "copy"
            logging.warning(f"Failed to optimize Office file, fallback to copy: {entry['original_filename']} | Error: {e}")
    # Archive files: skip recompression, add warning
    elif original_ext.lower() in [".zip", ".rar", ".7z", ".tar"]:
        import shutil
        shutil.copyfile(input_path, output_path)
        chosen_method = "copy"
        archive_warning = "File arsip seperti ZIP, RAR, 7z, dan TAR biasanya sudah terkompresi optimal. Tidak dilakukan kompresi ulang."
        logging.info(f"SKIP recompress archive: {entry['original_filename']} -> {output_path}")
    # Unsupported file types: return error
    else:
        raise HTTPException(status_code=415, detail="Tipe file ini belum didukung untuk kompresi. Hanya gambar, dokumen teks, PDF, dan Office.")
    # Simpan hasil analisis entitas sensitif ke metadata
    if sensitive_entities is not None:
        entry['sensitive_entities'] = sensitive_entities
        db_utils.save_result(file_id, entry)

    # Proses kompresi
    start_time = time.time()
    # Analisis AI selector untuk metadata
    entropy = None
    pdf_pages = None
    img_res = None
    try:
        from utils import file_entropy, pdf_page_count, image_resolution
        entropy = file_entropy(input_path)
        if mime_type == "application/pdf":
            pdf_pages = pdf_page_count(input_path)
        if mime_type and mime_type.startswith("image/"):
            img_res = image_resolution(input_path)
    except Exception as e:
        print(f"[WARN] Gagal analisis AI selector: {e}")
    # Kompresi optimal berbasis tipe file
    if mime_type == "application/pdf":
        try:
            import subprocess
            import sys
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "pdf_optimize.py"), input_path, output_path], check=True)
            chosen_method = "pdf_optimize"
        except Exception as e:
            print(f"[WARN] Gagal optimasi PDF, fallback ke gzip: {e}")
            utils.compress_gzip(input_path, output_path)
            chosen_method = "gzip"
    elif mime_type and mime_type.startswith("image/"):
        try:
            utils.compress_webp(input_path, output_path)
            chosen_method = "webp"
        except Exception as e:
            print(f"[WARN] Gagal kompres gambar ke WebP, fallback ke brotli: {e}")
            utils.compress_brotli(input_path, output_path)
            chosen_method = "brotli"
    # Update hasil kompresi ke DB
    size_after = os.path.getsize(output_path)
    entry['output_path'] = output_path
    entry['size_after'] = size_after
    entry['compression_method'] = chosen_method
    entry['status'] = 'compressed'
    db_utils.save_result(file_id, entry)
    elapsed = round(time.time() - start_time, 4)
    entry["elapsed"] = elapsed
    db_utils.save_result(file_id, entry)

    # Return hasil kompresi
    return {
        "status": "ok",
        "file_id": file_id,
        "original_filename": entry.get("original_filename"),
        "compressed_filename": os.path.basename(entry.get("output_path", "")),
        "mime_type": entry.get("mime_type"),
        "size_before": entry.get("size_before"),
        "size_after": entry.get("size_after"),
        "compression_method": entry.get("compression_method"),
        "ratio": round(entry["size_after"] / entry["size_before"], 4) if entry.get("size_before") and entry.get("size_after") else None,
        "elapsed": entry.get("elapsed")
    }

    entry["elapsed"] = elapsed
    # Simpan hasil analisis AI selector ke metadata
    entry["ai_analysis"] = {
        "entropy": entropy,
        "pdf_pages": pdf_pages,
        "img_res": img_res
    }


@app.get("/result/{file_id}")
@limiter.limit("30/minute")
def get_result(request: Request, file_id: str, x_api_key: str = Depends(api_key_auth)):
    entry = db_utils.load_result(file_id)
    if not entry:
        logging.warning(f"RESULT FAIL: file_id={file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    if entry.get("status") != "compressed":
        logging.info(f"RESULT PENDING: file_id={file_id}, status={entry.get('status')}")
        return JSONResponse(status_code=202, content={"status": entry.get("status", "pending")})
    ratio = round(entry["size_after"] / entry["size_before"], 4) if entry["size_before"] else None
    output_filename = os.path.basename(entry["output_path"])
    logging.info(f"RESULT OK: file_id={file_id}, size_before={entry['size_before']}, size_after={entry['size_after']}")
    return {
        "id": file_id,
        "original_filename": entry["original_filename"],
        "compressed_filename": output_filename,
        "mime_type": entry["mime_type"],
        "size_before": entry["size_before"],
        "size_after": entry["size_after"],
        "compression_method": entry["compression_method"],
        "ratio": ratio,
        "elapsed": entry.get("elapsed"),
        "download_url": f"/download/{file_id}"
    }

from typing import Optional, Union
import os




@app.get("/health")
def healthcheck():
    return {"status": "ok"}

def info():
    return {
        "app": "SmartShrink AI Backend",
        "version": "1.0.0",
        "features": ["ai compression", "auto profile", "batch", "diff", "dashboard", "sensitive mode"]
    }


def compress_file_internal(file_id, method, sensitive_mode=False, profile='default', convert_to=None):
    """
    Kompres file yang sudah diupload dengan metode tertentu, tanpa membutuhkan FastAPI Request object.
    Digunakan oleh endpoint /compress dan /batch_compress.
    """
    entry = db_utils.load_result(file_id)
    if not entry:
        raise HTTPException(status_code=404, detail="File not found")
    input_path = entry["file_path"]
    mime_type = entry.get("mime_type")
    file_size = entry.get("size_before")
    chosen_method = method.value if hasattr(method, 'value') else method
    profile = profile or 'default'
    if chosen_method == "ai":
        chosen_method = utils.ai_selector_stub(mime_type, file_size, entry['original_filename'], profile)
    elif chosen_method == "auto":
        chosen_method = utils.auto_select_compression(mime_type)
    if chosen_method == "lzma":
        raise HTTPException(status_code=501, detail="LZMA compression not implemented yet.")
    if chosen_method == "flif":
        raise HTTPException(status_code=501, detail="FLIF compression not implemented yet.")
    if chosen_method == "heic":
        raise HTTPException(status_code=501, detail="HEIC compression not implemented yet.")
    original_ext = os.path.splitext(entry['original_filename'])[1]
    output_filename = f"compressed_{file_id}_{entry['original_filename']}"
    output_path = os.path.join(RESULTS_DIR, output_filename)
    sensitive_entities = None
    if sensitive_mode and (mime_type.startswith("text/") or original_ext.lower() in [".txt", ".csv", ".json", ".xml", ".html"]):
        from backend import nlp_utils
        try:
            with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read(100000)
            sensitive_entities = nlp_utils.detect_sensitive_entities(text)
        except Exception:
            sensitive_entities = None
    # Kompresi sesuai format asli
    if mime_type == "application/pdf" or original_ext.lower() == ".pdf":
        from backend import pdf_optimize
        if not output_path.lower().endswith('.pdf'):
            output_path += '.pdf'
        method_used = pdf_optimize.compress_pdf(input_path, output_path)
        chosen_method = method_used
    elif mime_type.startswith("image/"):
        if not output_path.lower().endswith('.webp'):
            output_path += '.webp'
        utils.compress_webp(input_path, output_path, quality=80)
        chosen_method = "webp"
    elif mime_type == "video/mp4" or original_ext.lower() == ".mp4":
        try:
            import subprocess
            if not output_path.lower().endswith('_compressed.mp4'):
                output_path = output_path.replace('.mp4', '_compressed.mp4')
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", input_path,
                "-b:v", "1000k",
                "-b:a", "128k",
                output_path
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            chosen_method = "ffmpeg"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Kompresi MP4 gagal: {e}")
    elif original_ext.lower() in [".txt", ".csv", ".json", ".xml", ".html"] or mime_type in ["text/plain", "text/csv", "application/json", "application/xml", "text/html"] or mime_type.startswith("text/"):
        try:
            if not output_path.lower().endswith('.gz'):
                output_path += '.gz'
            utils.compress_gzip(input_path, output_path)
            chosen_method = "gzip"
            logging.info(f"Kompresi file text/markup ({entry['original_filename']}) sukses: {output_path}")
        except Exception as e:
            logging.error(f"Kompresi file text/markup gagal: {entry['original_filename']} | Error: {e}")
            raise HTTPException(status_code=500, detail=f"Kompresi file text/markup gagal: {e}")
    elif mime_type.startswith("image/"):
        if not output_path.lower().endswith('.webp'):
            output_path += '.webp'
        utils.compress_webp(input_path, output_path, quality=80)
        chosen_method = "webp"
    elif original_ext.lower() in [".pptx", ".docx", ".xlsx"]:
        try:
            from backend.office_optimize import optimize_office_images
            optimized = optimize_office_images(input_path, output_path, quality=75)
            chosen_method = "office_optimize"
            logging.info(f"Optimized Office file: {entry['original_filename']} -> {output_path} (images compressed: {optimized})")
        except Exception as e:
            import shutil
            shutil.copyfile(input_path, output_path)
            chosen_method = "copy"
            logging.warning(f"Failed to optimize Office file, fallback to copy: {entry['original_filename']} | Error: {e}")
    elif original_ext.lower() in [".zip", ".rar", ".7z", ".tar"]:
        import shutil
        shutil.copyfile(input_path, output_path)
        chosen_method = "copy"
        archive_warning = "File arsip seperti ZIP, RAR, 7z, dan TAR biasanya sudah terkompresi optimal. Tidak dilakukan kompresi ulang."
        logging.info(f"SKIP recompress archive: {entry['original_filename']} -> {output_path}")
    else:
        raise HTTPException(status_code=415, detail="Tipe file ini belum didukung untuk kompresi. Hanya gambar, dokumen teks, PDF, dan Office.")
    # Simpan hasil analisis entitas sensitif ke metadata
    if sensitive_entities is not None:
        entry['sensitive_entities'] = sensitive_entities
        db_utils.save_result(file_id, entry)
    # Analisis AI selector untuk metadata
    entropy = None
    pdf_pages = None
    img_res = None
    try:
        from utils import file_entropy, pdf_page_count, image_resolution
        entropy = file_entropy(input_path)
        if mime_type == "application/pdf":
            pdf_pages = pdf_page_count(input_path)
        if mime_type and mime_type.startswith("image/"):
            img_res = image_resolution(input_path)
    except Exception as e:
        print(f"[WARN] Gagal analisis AI selector: {e}")
    # Update hasil kompresi ke DB
    size_after = os.path.getsize(output_path)
    entry['output_path'] = output_path
    entry['size_after'] = size_after
    entry['compression_method'] = chosen_method
    entry['status'] = 'compressed'
    db_utils.save_result(file_id, entry)
    ratio = round(size_after / entry['size_before'], 3) if entry['size_before'] else None
    elapsed = None
    return {
        "file_id": file_id,
        "original_filename": entry["original_filename"],
        "compressed_filename": output_filename,
        "mime_type": mime_type,
        "size_before": entry["size_before"],
        "size_after": size_after,
        "compression_method": chosen_method,
        "ratio": ratio,
        "elapsed": elapsed,
        "download_url": f"/download/{file_id}"
    }

@app.post("/batch_compress")
@limiter.limit("30/minute")
def batch_compress(request: Request, batch: dict = Body(...), x_api_key: str = Depends(api_key_auth)):
    """
    Kompresi banyak file sekaligus. Body: {"items": [{"file_id":..., "method":..., "convert_to":...}]}
    """
    results = []
    for item in batch.get("items", []):
        try:
            resp = compress_file_internal(
                file_id=item["file_id"],
                method=CompressionMethod(item["method"]),
                sensitive_mode=item.get("sensitive_mode", False),
                profile=item.get("profile", 'default'),
                convert_to=item.get("convert_to")
            )
            results.append({"file_id": item["file_id"], "result": resp})
        except Exception as e:
            logging.error(f"BATCH_COMPRESS ERROR: file_id={item.get('file_id')}, error={str(e)}")
    return results

@app.post("/compress")
@limiter.limit("30/minute")
def compress_file(request: Request, file_id: str = Form(...), method: CompressionMethod = Form(...), sensitive_mode: bool = Form(False), profile: str = Form('default'), x_api_key: str = Depends(api_key_auth)):
    """
    Kompres file yang sudah diupload dengan metode tertentu.
    Pilihan method: ai, auto, gzip, brotli, webp, pdf_optimize, lzma, flif, heic
    Optional: sensitive_mode (True/False) untuk lossless compression dokumen sensitif.
    Optional: profile (web, archive, network, default) untuk auto profile kompresi.
    """
    return compress_file_internal(file_id, method, sensitive_mode, profile)



@app.post("/diff_compress")
@limiter.limit("30/minute")
def diff_compress(request: Request,
    file_id: str = Form(...),
    base_file_id: str = Form(...),
    method: str = Form('patch'),
    patch_file_id: str = Form(None),
    x_api_key: str = Depends(api_key_auth)
):
    """
    Differential compression advanced:
    - method=patch: hasilkan file patch (delta) antara base_file_id dan file_id
    - method=restore: hasilkan file baru dengan menerapkan patch_file_id ke base_file_id
    """
    import hashlib
    from backend import diff_utils
    entry = db_utils.load_result(file_id)
    base_entry = db_utils.load_result(base_file_id)
    if not entry or not base_entry:
        logging.warning(f"DIFF_COMPRESS FAIL: file_id={file_id} or base_file_id={base_file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    base_path = base_entry["file_path"]
    input_path = entry["file_path"]
    if method == 'patch':
        patch_name = f"patch_{base_file_id}_{file_id}"
        patch_path = os.path.join(RESULTS_DIR, patch_name)
        diff_utils.create_binary_patch(base_path, input_path, patch_path)
        logging.info(f"DIFF_COMPRESS PATCH OK: base={base_file_id}, file={file_id}, patch={patch_name}")
        return {"patch_file": patch_name, "patch_path": patch_path}
    elif method == 'restore':
        if not patch_file_id:
            logging.warning(f"DIFF_COMPRESS RESTORE FAIL: patch_file_id missing for base={base_file_id}")
            raise HTTPException(status_code=400, detail="patch_file_id is required for restore method")
        patch_path = os.path.join(RESULTS_DIR, patch_file_id)
        restored_name = f"restored_{base_file_id}_{patch_file_id}"
        restored_path = os.path.join(RESULTS_DIR, restored_name)
        diff_utils.apply_binary_patch(base_path, patch_path, restored_path)
        logging.info(f"DIFF_COMPRESS RESTORE OK: base={base_file_id}, patch={patch_file_id}, restored={restored_name}")
        return {"restored_file": restored_name, "restored_path": restored_path}
    else:
        logging.warning(f"DIFF_COMPRESS FAIL: unknown method {method}")
        raise HTTPException(status_code=400, detail="Unknown diff_compress method")


@app.get("/compression_methods")
def get_compression_methods():
    """
    Endpoint untuk mendapatkan daftar metode kompresi beserta keterangan singkat.
    """
    return [
        {"value": "ai", "label": "AI (Otomatis)", "desc": "Pilih metode kompresi terbaik secara otomatis dengan analisis cerdas."},

        {"value": "gzip", "label": "Gzip (Text/PDF)", "desc": "Kompresi lossless umum, sangat efektif untuk file teks dan PDF sederhana."},
        {"value": "brotli", "label": "Brotli (Universal)", "desc": "Kompresi lossless modern, cocok untuk berbagai tipe file (text, arsip, dsb)."},
        {"value": "webp", "label": "WebP (Gambar)", "desc": "Kompresi gambar ke format WebP, sangat efektif untuk JPEG/PNG/WebP."},
        {"value": "pdf_optimize", "label": "PDF Optimizer (PDF)", "desc": "Optimasi khusus PDF, mengurangi ukuran dengan kompresi konten internal."}
    ]

from typing import Optional, Union

@app.get("/download/{file_id}")
@limiter.limit("30/minute")
def download_file(request: Request, file_id: str, x_api_key: str = Depends(api_key_auth)):
    # PATCH FINAL: Ambil mode langsung dari request.query_params untuk menghindari error 422 apapun inputnya
    raw_mode = request.query_params.getlist("mode") if "mode" in request.query_params else None
    if raw_mode:
        mode_val = raw_mode[0] if isinstance(raw_mode, list) and raw_mode else raw_mode
        if isinstance(mode_val, list):
            mode_val = mode_val[0] if mode_val else "compressed"
        if mode_val not in ("original", "compressed"):
            mode_val = "compressed"
    else:
        mode_val = "compressed"
    logging.info(f"DOWNLOAD DEBUG: file_id={file_id}, raw_mode={raw_mode}, mode_val={mode_val}, type={type(raw_mode)}")
    entry = db_utils.load_result(file_id)
    if not entry:
        logging.warning(f"DOWNLOAD FAIL: file_id={file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    if mode_val == "original":
        orig_path = entry.get("file_path")
        if not orig_path or not os.path.exists(orig_path):
            logging.warning(f"DOWNLOAD FAIL: original file_id={file_id} not found")
            raise HTTPException(status_code=404, detail="Original file not found")
        orig_filename = entry.get("original_filename")
        logging.info(f"DOWNLOAD OK: original file_id={file_id}, filename={orig_filename}")
        return FileResponse(orig_path, filename=orig_filename)
    else:
        output_path = entry.get("output_path")
        if not output_path or not os.path.exists(output_path):
            logging.warning(f"DOWNLOAD FAIL: compressed file_id={file_id} not found")
            raise HTTPException(status_code=404, detail="File not compressed yet")
        compressed_filename = os.path.basename(output_path)
        logging.info(f"DOWNLOAD OK: compressed file_id={file_id}, filename={compressed_filename}")
        return FileResponse(output_path, filename=compressed_filename)


