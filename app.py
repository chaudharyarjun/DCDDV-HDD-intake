from flask import Flask, request, render_template, jsonify
import os
from extract import process_image
import sqlite3
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
DB = 'drive_data.db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS drives (
                id INTEGER PRIMARY KEY,
                filename TEXT,
                brand TEXT,
                model TEXT,
                serial TEXT,
                capacity TEXT,
                timestamp TEXT
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    if file:
        filename = file.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        with open(path, 'rb') as f:
            meta = process_image(f.read())

        model = meta['model'][0] if meta['model'] else None
        serial = meta['serial'][0] if meta['serial'] else None
        capacity = meta['capacity'][0] if meta['capacity'] else None
        brand = meta['brand']

        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO drives (filename, brand, model, serial, capacity, timestamp) VALUES (?, ?, ?, ?, ?, ?)", 
                      (filename, brand, model, serial, capacity, datetime.now()))
            conn.commit()

        return jsonify(meta)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
