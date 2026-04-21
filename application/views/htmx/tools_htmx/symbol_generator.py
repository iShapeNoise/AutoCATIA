from flask import request, render_template, jsonify
from pathlib import Path
import json
from werkzeug.utils import secure_filename

from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.utils.image_to_drawing import ImageToDrawingConverter

@app.route(f'{htmx}/tools/generate_symbol_script', methods=['POST'])
def htmx_generate_symbol_script():
    drawing_name = request.form.get('drawing_name')
    script_name = request.form.get('script_name')
    associated_name = request.form.get('associated_name')

    # Handle image upload
    if 'image_file' not in request.files:
        return render_template('partials/errors.html',
                             errors=['No image file selected'])

    image_file = request.files['image_file']
    if image_file.filename == '':
        return render_template('partials/errors.html',
                             errors=['No image file selected'])

    # Save uploaded image temporarily
    temp_dir = Path(__file__).parent.parent.parent.parent / 'temp'
    temp_dir.mkdir(exist_ok=True)

    filename = secure_filename(image_file.filename)
    image_path = temp_dir / filename
    image_file.save(str(image_path))

    try:
        # Generate script
        converter = ImageToDrawingConverter(scale_factor=0.1)
        symbols_dir = Path(__file__).parent.parent.parent / 'pycatia_scripts' / 'drawing' / 'symbols'
        symbols_dir.mkdir(exist_ok=True)

        script_path = symbols_dir / f'{script_name}.py'
        converter.generate_drawing_script(str(image_path), str(script_path))

        # Add symbol to drawing if specified
        if drawing_name:
            add_symbol_to_drawing(drawing_name, script_name)

        # Save metadata
        save_symbol_metadata(script_name, associated_name, str(image_path))

        return render_template('partials/success.html',
                             data=f'Script {script_name} generated successfully')

    except Exception as e:
        return render_template('partials/errors.html',
                             errors=[f'Error generating script: {str(e)}'])

    finally:
        # Clean up temp file
        if image_path.exists():
            image_path.unlink()

@app.route(f'{htmx}/tools/load_symbol_script', methods=['POST'])
def htmx_load_symbol_script():
    script_name = request.form.get('script_name')

    try:
        # Load script data
        script_data = load_symbol_data(script_name)
        return render_template('partials/symbol_editor.html',
                             script_data=script_data)

    except Exception as e:
        return render_template('partials/errors.html',
                             errors=[f'Error loading script: {str(e)}'])

@app.route(f'{htmx}/tools/update_symbol_script', methods=['POST'])
def htmx_update_symbol_script():
    script_name = request.form.get('script_name')
    updated_data = request.form.get('updated_data')

    try:
        # Parse updated data and update script
        update_symbol_script(script_name, updated_data)
        return render_template('partials/success.html',
                             data=f'Script {script_name} updated successfully')

    except Exception as e:
        return render_template('partials/errors.html',
                             errors=[f'Error updating script: {str(e)}'])

def add_symbol_to_drawing(drawing_name: str, script_name: str):
    """Add generated symbol to specified drawing"""
    # Implementation to add symbol to active drawing
    pass

def save_symbol_metadata(script_name: str, associated_name: str, image_path: str):
    """Save symbol metadata"""
    metadata_path = Path(__file__).parent.parent.parent / 'pycatia_scripts' / 'drawing' / 'symbols' / 'metadata.json'

    metadata = {}
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

    metadata[script_name] = {
        'associated_name': associated_name,
        'source_image': image_path,
        'created_at': str(Path().resolve())
    }

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def load_symbol_data(script_name: str):
    """Load symbol script data for editing"""
    script_path = Path(__file__).parent.parent.parent / 'pycatia_scripts' / 'drawing' / 'symbols' / f'{script_name}.py'

    # Parse script to extract lines, text, positions
    # This is a simplified version - you'd need proper parsing
    with open(script_path, 'r') as f:
        content = f.read()

    return {
        'script_name': script_name,
        'content': content,
        'lines': [],  # Extracted line data
        'texts': []   # Extracted text data
    }

def update_symbol_script(script_name: str, updated_data: str):
    """Update symbol script with new data"""
    script_path = Path(__file__).parent.parent.parent / 'pycatia_scripts' / 'drawing' / 'symbols' / f'{script_name}.py'

    with open(script_path, 'w') as f:
        f.write(updated_data)
