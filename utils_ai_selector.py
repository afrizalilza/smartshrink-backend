import re

def ai_selector_ml(mime_type, file_size, filename, profile='default'):
    """
    ML sederhana (decision tree/rule-based) untuk memilih metode kompresi optimal, mendukung profile.
    """
    ext = filename.lower().split('.')[-1]
    if profile == 'web':
        if mime_type.startswith("image/"):
            return "webp" if ext in ["jpg", "jpeg", "png", "webp"] else "heic"
        if mime_type.startswith("text/"):
            return "brotli"
        return "brotli"
    if profile == 'archive':
        if mime_type.startswith("image/"):
            return "flif"
        if mime_type.startswith("text/"):
            return "lzma"
        return "lzma"
    if profile == 'network':
        if mime_type.startswith("image/"):
            return "webp"
        if mime_type.startswith("text/"):
            return "brotli"
        return "brotli"
    # Default rules
    if mime_type == "application/pdf" or filename.lower().endswith('.pdf'):
        if file_size > 2*1024*1024:
            return "pdf_optimize"
        else:
            return "gzip"
    if mime_type.startswith("image/"):
        if ext in ["jpg", "jpeg", "png", "webp"]:
            return "webp"
        elif ext in ["heic", "flif"]:
            return ext
        else:
            return "webp"
    if mime_type.startswith("text/") or filename.lower().endswith((".log", ".txt", ".csv", ".json", ".xml")):
        if file_size > 1*1024*1024:
            return "brotli"
        else:
            return "gzip"
    if filename.lower().endswith((".docx", ".xlsx", ".pptx")):
        return "gzip"
    return "brotli"
