import requests
import os

BASE_URL = "http://localhost:8000"
API_KEY = "demo-key-123"
headers = {"X-API-Key": API_KEY}

def test_large_file():
    # Buat file besar (~10MB)
    fname = "large_testfile.bin"
    with open(fname, "wb") as f:
        f.write(os.urandom(10 * 1024 * 1024))
    with open(fname, "rb") as f:
        files = {"file": f}
        r = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
        print("[LARGE UPLOAD]", r.status_code)
    os.remove(fname)

def test_corrupt_file():
    # Upload file yang isinya random (tidak valid untuk format apapun)
    fname = "corrupt_testfile.txt"
    with open(fname, "wb") as f:
        f.write(os.urandom(2048))
    with open(fname, "rb") as f:
        files = {"file": f}
        r = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
        print("[CORRUPT UPLOAD]", r.status_code)
    os.remove(fname)

def test_duplicate_upload():
    fname = "dupe_testfile.txt"
    with open(fname, "w") as f:
        f.write("duplikat test")
    with open(fname, "rb") as f:
        files = {"file": f}
        r1 = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
    with open(fname, "rb") as f:
        files = {"file": f}
        r2 = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
    print("[DUPLICATE UPLOAD]", r1.status_code, r2.status_code)
    os.remove(fname)

def test_sensitive_mode():
    fname = "sensitive_test.txt"
    with open(fname, "w") as f:
        f.write("Nama: Budi, Email: budi@mail.com, NIK: 1234567890123456")
    with open(fname, "rb") as f:
        files = {"file": f}
        r = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
    if r.status_code == 200:
        file_id = r.json()["id"]
        data = {"file_id": file_id, "method": "gzip", "sensitive_mode": True}
        r2 = requests.post(f"{BASE_URL}/compress", data=data, headers=headers)
        print("[SENSITIVE COMPRESS]", r2.status_code)
    os.remove(fname)

if __name__ == "__main__":
    test_large_file()
    test_corrupt_file()
    test_duplicate_upload()
    test_sensitive_mode()
    print("Edge case tests done.")
