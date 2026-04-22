from flask import request, jsonify
from pathlib import Path
from application import app
from application.views.url_prefixes import htmx

@app.route(f'{htmx}/check_file_exists', methods=['GET'])
def htmx_check_file_exists():
    """Check if a file exists at the given path"""
    file_path = request.args.get('file', '')

    try:
        path = Path(file_path)
        exists = path.exists() and path.is_file()
        return jsonify({'exists': exists})
    except Exception:
        return jsonify({'exists': False})
