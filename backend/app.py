import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from services.db_service import init_db
from routes.upload import upload_bp
from routes.preprocess import preprocess_bp
from routes.analysis import analysis_bp
from routes.history import history_bp

# ==========================================
# INISIALISASI FLASK
# ==========================================
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='/')

# [KRITIKAL] CORS dibatasi hanya ke origin frontend yang dikenal (untuk mode dev & deploy)
frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173").rstrip("/")
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:7860",
    "http://127.0.0.1:7860",
]
if frontend_url and frontend_url not in origins:
    origins.append(frontend_url)

CORS(app, origins=origins)

# [KEAMANAN] Batasi ukuran upload maksimal 50 MB
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({"error": "Ukuran file terlalu besar. Maksimal 50 MB yang diizinkan."}), 413

# Inisialisasi Database
init_db()

# Register Blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(preprocess_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(history_bp)

# ==========================================
# CATCH-ALL ROUTE: Serve React SPA
# ==========================================
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    index_path = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(app.static_folder, 'index.html')
    return jsonify({
        "message": "Frontend belum di-build. Jalankan: cd frontend && npm run build",
        "status": "no_frontend"
    }), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, use_reloader=False, host='0.0.0.0', port=port, threaded=True)
