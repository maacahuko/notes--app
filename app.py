from flask import Flask, request, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "notesdb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres")
    )

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    if not data.get("title") or not data.get("content"):
        return jsonify({"error": "Title and content required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING id, created_at;",
        (data["title"], data["content"])
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({
        "id": row[0],
        "title": data["title"],
        "content": data["content"],
        "created_at": row[1].isoformat()
    }), 201

@app.route("/api/notes", methods=["GET"])
def get_notes():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"id": r[0], "title": r[1], "content": r[2], "created_at": r[3].isoformat()}
        for r in rows
    ])

@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Note deleted"})

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        print(f"DB init skipped: {e}")
    app.run(host="0.0.0.0", port=5000)