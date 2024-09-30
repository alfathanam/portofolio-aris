from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Koneksi ke database PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DATABASE_NAME"),  # Nama database
            user=os.getenv("DATABASE_USER"),      # Nama pengguna database
            password=os.getenv("DATABASE_PASSWORD"),  # Password pengguna database
            host=os.getenv("DATABASE_HOST"),      # Host database
            port=os.getenv("DATABASE_PORT", "5432")  # Port database, default ke 5432 jika tidak diset
        )
        return conn
    except Exception as e:
        print("Gagal terhubung ke database:", e)
        return None

# Membuat tabel mahasiswa
def create_table():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mahasiswa (
                id SERIAL PRIMARY KEY,
                nama VARCHAR(100),
                umur INT,
                jurusan VARCHAR(50)
            );
        ''')
        conn.commit()
        conn.close()

create_table()

@app.route('/mahasiswa', methods=['GET'])
def get_mahasiswa():
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mahasiswa;")
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)
    return jsonify({'error': 'Gagal terhubung ke database'}), 500

@app.route('/mahasiswa/<int:id>', methods=['GET'])
def get_mahasiswa_by_id(id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mahasiswa WHERE id = %s;", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify(row)
        return jsonify({'error': 'Mahasiswa tidak ditemukan'}), 404
    return jsonify({'error': 'Gagal terhubung ke database'}), 500

@app.route('/mahasiswa', methods=['POST'])
def add_mahasiswa():
    data = request.json
    nama = data.get('nama')
    umur = data.get('umur')
    jurusan = data.get('jurusan')

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO mahasiswa (nama, umur, jurusan)
            VALUES (%s, %s, %s)
            RETURNING id;
        ''', (nama, umur, jurusan))
        mahasiswa_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        # Logging the successful POST request to a file in the Docker volume
        log_message = f"Added mahasiswa: {nama}, {umur}, {jurusan} with ID: {mahasiswa_id}\n"
        with open('/app/logs/mahasiswa_log.txt', 'a') as f:
            f.write(log_message)

        return jsonify({'id': mahasiswa_id}), 201
    return jsonify({'error': 'Gagal terhubung ke database'}), 500

@app.route('/mahasiswa/<int:id>', methods=['PUT'])
def update_mahasiswa(id):
    data = request.json
    nama = data.get('nama')
    umur = data.get('umur')
    jurusan = data.get('jurusan')

    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE mahasiswa
            SET nama = %s, umur = %s, jurusan = %s
            WHERE id = %s;
        ''', (nama, umur, jurusan, id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data mahasiswa berhasil diperbarui.'})
    return jsonify({'error': 'Gagal terhubung ke database'}), 500

@app.route('/mahasiswa/<int:id>', methods=['DELETE'])
def delete_mahasiswa(id):
    conn = connect_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM mahasiswa WHERE id = %s;
        ''', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Data mahasiswa berhasil dihapus.'})
    return jsonify({'error': 'Gagal terhubung ke database'}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010)
