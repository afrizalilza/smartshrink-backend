import os
import bsdiff4

def create_binary_diff(old_path, new_path, patch_path):
    """Buat file patch (delta) antara old_path dan new_path."""
    with open(old_path, 'rb') as f1, open(new_path, 'rb') as f2:
        old_bytes = f1.read()
        new_bytes = f2.read()
    patch = bsdiff4.diff(old_bytes, new_bytes)
    with open(patch_path, 'wb') as f:
        f.write(patch)
    return patch_path

def apply_binary_patch(old_path, patch_path, out_path):
    """Terapkan patch ke old_path untuk menghasilkan out_path."""
    with open(old_path, 'rb') as f1, open(patch_path, 'rb') as f2:
        old_bytes = f1.read()
        patch_bytes = f2.read()
    new_bytes = bsdiff4.patch(old_bytes, patch_bytes)
    with open(out_path, 'wb') as f:
        f.write(new_bytes)
    return out_path
