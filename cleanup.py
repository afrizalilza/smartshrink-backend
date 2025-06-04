import os
import time

STORAGE_DIR = r'd:/smart_shrink_AI/storage'

def cleanup_storage(storage_dir, max_age_days=7):
    now = time.time()
    for filename in os.listdir(storage_dir):
        filepath = os.path.join(storage_dir, filename)
        if os.path.isfile(filepath):
            if now - os.path.getmtime(filepath) > max_age_days * 86400:
                print(f"Deleting {filepath}")
                os.remove(filepath)

if __name__ == "__main__":
    cleanup_storage(STORAGE_DIR, max_age_days=7)
