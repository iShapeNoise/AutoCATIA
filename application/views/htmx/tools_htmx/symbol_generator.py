from flask import request, render_template, jsonify
from pathlib import Path
import json
import logging
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.tools.image_to_drawing import ImageToDrawingConverter

logger.info("HTMX Tools module loaded successfully")

@app.route(f'{htmx}/tools/generate_symbol_script', methods=['POST'])
def htmx_generate_symbol_script():
    logger.info("=== Generate Symbol Script Endpoint Called ===")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request files: {dict(request.files)}")
    logger.info(f"Request form: {dict(request.form)}")

    try:
        drawing_name = request.form.get('drawing_name')
        script_name = request.form.get('script_name')
        associated_name = request.form.get('associated_name')

        logger.info(f"Parameters - drawing: {drawing_name}, script: {script_name}, associated: {associated_name}")

        # Handle image upload
        if 'image_file' not in request.files:
            logger.error("No image file in request")
            return render_template('partials/errors.html',
                                 errors=['No image file selected'])

        image_file = request.files['image_file']
        if image_file.filename == '':
            logger.error("Empty filename")
            return render_template('partials/errors.html',
                                 errors=['No image file selected'])

        logger.info(f"Image file: {image_file.filename}")

        # Save uploaded image temporarily
        temp_dir = Path(__file__).parent.parent.parent.parent / 'temp'
        temp_dir.mkdir(exist_ok=True)

        filename = secure_filename(image_file.filename)
        image_path = temp_dir / filename
        image_file.save(str(image_path))

        logger.info(f"Image saved to: {image_path}")

        # Generate script
        logger.info("Starting script generation...")
        converter = ImageToDrawingConverter(scale_factor=0.1)
        symbols_dir = Path(__file__).parent.parent.parent / 'pycatia_scripts' / 'drawing' / 'symbols'
        symbols_dir.mkdir(exist_ok=True)

        script_path = symbols_dir / f'{script_name}.py'
        logger.info(f"Generating script at: {script_path}")

        converter.generate_drawing_script(str(image_path), str(script_path))

        logger.info("Script generated successfully")

        # Save metadata
        save_symbol_metadata(script_name, associated_name, str(image_path))
        logger.info("Metadata saved")

        return render_template('partials/success.html',
                             data=f'Script {script_name} generated successfully')

    except Exception as e:
        logger.error(f"Error in generate_symbol_script: {str(e)}", exc_info=True)
        return render_template('partials/errors.html',
                             errors=[f'Error generating script: {str(e)}'])

    finally:
        # Clean up temp file
        if 'image_path' in locals() and image_path.exists():
            image_path.unlink()
            logger.info("Temp file cleaned up")

def save_symbol_metadata(script_name: str, associated_name: str, image_path: str):
    """Save symbol metadata"""
    logger.info(f"Saving metadata for {script_name}")
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

    logger.info("Metadata saved successfully")

# Add debug route to check if module is loaded
@app.route(f'{htmx}/tools/debug')
def htmx_tools_debug():
    logger.info("Debug endpoint called")
    return "HTMX Tools module is working!"
