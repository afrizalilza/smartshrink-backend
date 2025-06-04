import os
import base64
from PIL import Image

def file_size(path):
    try:
        return os.path.getsize(path)
    except Exception:
        return None

def image_to_base64(path, max_dim=300):
    try:
        with Image.open(path) as img:
            img.thumbnail((max_dim, max_dim))
            from io import BytesIO
            buf = BytesIO()
            img.save(buf, format='PNG')
            return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception:
        return None
