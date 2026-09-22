# Ensure the table exists before the first request.
# This works whether the app runs via `python app.py` or via gunicorn.
_table_initialized = False

@app.before_request
def ensure_table_exists():
    global _table_initialized
    if not _table_initialized:
        try:
            init_db()
            _table_initialized = True
        except Exception as e:
            print(f"DB init failed: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)