import requests

BASE_URL = "http://localhost:8000"
API_KEY = "demo-key-123"  # Ganti sesuai API key yang aktif

headers = {"X-API-Key": API_KEY}


def safe_print_response(r, label):
    try:
        print(f"[{label}]", r.status_code, r.json())
    except Exception:
        print(f"[{label}]", r.status_code, r.text)

def test_upload():
    files = {"file": open("testfile.txt", "rb")}
    r = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
    safe_print_response(r, "UPLOAD")
    assert r.status_code == 200
    file_id = r.json()["id"]
    return file_id

def test_compress(file_id):
    data = {"file_id": file_id, "method": "gzip"}
    r = requests.post(f"{BASE_URL}/compress", data=data, headers=headers)
    safe_print_response(r, "COMPRESS")
    assert r.status_code == 200
    return r.json()

def test_get_result(file_id):
    r = requests.get(f"{BASE_URL}/result/{file_id}", headers=headers)
    safe_print_response(r, "RESULT")
    assert r.status_code == 200 or r.status_code == 202
    return r.json()

def test_download(file_id):
    r = requests.get(f"{BASE_URL}/download/{file_id}", headers=headers)
    safe_print_response(r, "DOWNLOAD")
    assert r.status_code == 200 or r.status_code == 404

if __name__ == "__main__":
    # Siapkan file dummy
    with open("testfile.txt", "w") as f:
        f.write("Ini file dummy untuk testing SmartShrink API.")
    file_id = test_upload()
    test_compress(file_id)
    test_get_result(file_id)
    test_download(file_id)
    print("Semua tes selesai!")
