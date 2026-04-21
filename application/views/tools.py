from pathlib import Path
from flask import render_template, request, jsonify
from application import app
from application.views.view_wrappers import catia_v5_required
from application.pycatia_scripts.com_objects import get_app_object
from application.pycatia_scripts.the_document import PTDrawingDocument


@app.route('/tools')
@catia_v5_required
def tools():
    return render_template('tools.html')


@app.route('/tools/symbol_from_image')
@catia_v5_required
def tools_symbol_from_image():
    # Get available drawings
    drawings = get_available_drawings()
    # Get existing symbols
    symbols = get_existing_symbols()

    return render_template('tools_symbol_from_image.html',
                         drawings=drawings,
                         symbols=symbols)

def get_available_drawings():
    """Get list of open CATIA drawings"""
    try:
        application = get_app_object()
        if not application:
            return []

        documents = application.documents
        drawings = []

        for i in range(documents.count):
            doc = documents.item(i + 1)
            if doc.name.endswith('.CATDrawing'):
                drawings.append(doc.name)

        return drawings
    except:
        return []

def get_existing_symbols():
    """Get list of existing symbol scripts"""
    symbols_path = Path(__file__).parent.parent / 'pycatia_scripts' / 'drawing' / 'symbols'
    symbols = []

    if symbols_path.exists():
        for file_path in symbols_path.glob('*.py'):
            if file_path.name != '__init__.py':
                symbols.append(file_path.stem)

    return symbols
