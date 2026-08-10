import os
import pandas as pd
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from services.session_service import UPLOAD_FOLDER, cleanup_old_sessions

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nama file kosong"}), 400

    # [KRITIKAL] Sanitasi nama file untuk mencegah Path Traversal
    safe_filename = secure_filename(file.filename)
    if not safe_filename or not safe_filename.endswith('.csv'):
        return jsonify({"error": "Hanya file CSV yang diizinkan"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
    file.save(filepath)

    # [MINOR] Hapus sesi lama setelah file baru berhasil diunggah
    cleanup_old_sessions(exclude_filename=safe_filename)

    try:
        df           = pd.read_csv(filepath)
        columns      = df.columns.tolist()
        preview_data = df.head(5).fillna("").to_dict(orient='records')

        return jsonify({
            "status":   "success",
            "filename": safe_filename,
            "columns":  columns,
            "preview":  preview_data,
            "message":  "File berhasil diunggah dan dibaca."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
