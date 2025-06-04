import re

def detect_sensitive_entities(text):
    """
    Deteksi entitas sensitif (dummy: email, nomor telepon, NIK, dsb).
    """
    entities = {}
    entities['email'] = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    entities['phone'] = re.findall(r'\b08\d{8,12}\b', text)
    entities['nik'] = re.findall(r'\b\d{16}\b', text)
    # Tambah pola lain sesuai kebutuhan
    return entities
