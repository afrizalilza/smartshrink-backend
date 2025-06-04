# Placeholder for utility/helper functions (deteksi MIME, kompresi, dsb) untuk pengembangan berikutnya.

import gzip
import brotli
import shutil
import mimetypes
from PIL import Image
import os

# Kompresi file menggunakan gzip
# Keluaran: file .gz

def compress_gzip(input_path, output_path):
    with open(input_path, 'rb') as f_in, gzip.open(output_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

# Kompresi file menggunakan brotli
# Keluaran: file .br

def compress_brotli(input_path, output_path):
    with open(input_path, 'rb') as f_in:
        data = f_in.read()
    compressed = brotli.compress(data)
    with open(output_path, 'wb') as f_out:
        f_out.write(compressed)

# Kompresi gambar ke WebP
# Keluaran: file .webp

def compress_webp(input_path, output_path, quality=80):
    with Image.open(input_path) as img:
        img.save(output_path, 'webp', quality=quality)

# Rule-based auto selection: text/pdf pakai gzip, gambar pakai webp, lainnya brotli

def auto_select_compression(mime_type):
    if mime_type and (mime_type.startswith('text/') or mime_type == 'application/pdf'):
        return 'gzip'
    if mime_type and mime_type.startswith('image/'):
        return 'webp'
    return 'brotli'

# AI selector stub (rule-based, bisa diganti ML model nanti)
import math
from PIL import Image
import pikepdf

def file_entropy(path, max_bytes=1024*1024):
    # Hitung entropi byte file (randomness)
    with open(path, 'rb') as f:
        data = f.read(max_bytes)
    if not data:
        return 0
    freq = [0]*256
    for b in data:
        freq[b] += 1
    entropy = 0
    for c in freq:
        if c:
            p = c/len(data)
            entropy -= p*math.log2(p)
    return entropy

def pdf_page_count(path):
    try:
        pdf = pikepdf.open(path)
        n = len(pdf.pages)
        pdf.close()
        return n
    except Exception:
        return None

def image_resolution(path):
    try:
        with Image.open(path) as img:
            return img.size
    except Exception:
        return None

def ai_selector_stub(mime_type, file_size, filename, profile='default'):
    """
    Wrapper ke ai_selector_ml (ML sederhana) agar tetap backward compatible.
    """
    try:
        from backend.utils_ai_selector import ai_selector_ml
        return ai_selector_ml(mime_type, file_size, filename, profile)
    except Exception as e:
        # Fallback rule jika modul gagal
        if profile == 'web':
            if mime_type.startswith("image/"):
                return "webp"
            return "brotli"
        if profile == 'archive':
            return "lzma"
        if profile == 'network':
            return "brotli"
        # Default
        if mime_type == "application/pdf" or filename.lower().endswith('.pdf'):
            return "pdf_optimize"
        if mime_type.startswith("image/"):
            return "webp"
        if mime_type.startswith("text/") or filename.lower().endswith(('.log','.txt','.csv','.json','.xml')):
            return "brotli"
        if filename.lower().endswith(('.docx','.xlsx','.pptx')):
            return "gzip"
        return "brotli"
    if entropy and entropy < 3.5:
        print("[AI SELECTOR] Chosen: gzip (low entropy)")
        return 'gzip'
    print("[AI SELECTOR] Chosen: brotli (default)")
    return 'brotli'


