import sqlite3
import json
DB_PATH = 'results_db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        file_id TEXT PRIMARY KEY,
        data TEXT
    )''')
    conn.commit()
    conn.close()

def save_result(file_id, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('REPLACE INTO results (file_id, data) VALUES (?, ?)', (file_id, json.dumps(data)))
    conn.commit()
    conn.close()

def load_result(file_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT data FROM results WHERE file_id=?', (file_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def update_result_field(file_id, field, value):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT data FROM results WHERE file_id=?', (file_id,))
    row = c.fetchone()
    if row:
        data = json.loads(row[0])
        data[field] = value
        c.execute('REPLACE INTO results (file_id, data) VALUES (?, ?)', (file_id, json.dumps(data)))
        conn.commit()
    conn.close()

def load_all_results():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT file_id, data FROM results')
    rows = c.fetchall()
    conn.close()
    return {fid: json.loads(data) for fid, data in rows}

def delete_result(file_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM results WHERE file_id=?', (file_id,))
    conn.commit()
    conn.close()
