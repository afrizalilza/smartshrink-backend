import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'results.db'))

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS results (
    file_id TEXT PRIMARY KEY,
    data TEXT
)
''')
conn.commit()
conn.close()
print('Tabel results berhasil dibuat/ada di', DB_PATH)
