import os
import json

UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_session_filepath(filename):
    if not filename:
        return os.path.join(UPLOAD_FOLDER, 'session_default.json')
    safe_name = str(filename).replace('.csv', '')
    return os.path.join(UPLOAD_FOLDER, f'session_{safe_name}.json')

def save_session(filename, data):
    with open(get_session_filepath(filename), 'w') as f:
        json.dump(data, f)

def load_session(filename):
    filepath = get_session_filepath(filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def cleanup_old_sessions(exclude_filename=None):
    """Hapus file session lama kecuali yang sedang aktif."""
    try:
        for fname in os.listdir(UPLOAD_FOLDER):
            if fname.startswith('session_') and fname.endswith('.json'):
                if exclude_filename:
                    safe = exclude_filename.replace('.csv', '')
                    if fname == f'session_{safe}.json':
                        continue
                os.remove(os.path.join(UPLOAD_FOLDER, fname))
    except Exception:
        pass
