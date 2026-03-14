from flask import request, render_template
from pathlib import Path
import json

from application import app
from application.pycatia_scripts.drawing.new_drawing import insert_drawing_template
from application.views.url_prefixes import htmx


def save_template_settings(form_parameters):
    """Save template parameters to settings file"""
    try:
        # Get the correct path to userdata folder
        app_root = Path(__file__).parent.parent.parent.parent
        userdata_path = Path(app_root, 'userdata')
        settings_file = Path(userdata_path, 'settings')

        # Ensure userdata directory exists
        userdata_path.mkdir(exist_ok=True)

        # Read existing settings
        settings_data = {}
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)

        # Update drawing template parameters
        if 'drawing_template' not in settings_data:
            settings_data['drawing_template'] = {}
        if 'parameters' not in settings_data['drawing_template']:
            settings_data['drawing_template']['parameters'] = {}

        # Save only non-empty values
        for key, value in form_parameters.items():
            if value:  # Only save if not empty
                settings_data['drawing_template']['parameters'][key] = value

        # Write back to file
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)

        return True, "Template settings saved successfully"

    except Exception as e:
        return False, f"Error saving settings: {e}"


@app.route(f'{htmx}/drawing/template', methods=['POST'])
def htmx_drawing_template():
    """Handle template form submission - saves settings and optionally inserts template"""
    # Get all form parameters
    part_number = request.form.get('DRAWING-NUMBER', type=str) or ""
    title = request.form.get('TITLE', type=str) or ""
    created_by = request.form.get('CREATED-BY', type=str) or ""
    revision = request.form.get('REVISION', type=str) or ""

    form_parameters = {
        'DRAWING-NUMBER': part_number,
        'TITLE': title,
        'CREATED-BY': created_by,
        'REVISION': revision,
    }

    # Save settings first
    save_success, save_message = save_template_settings(form_parameters)

    # Try to insert template into CATIA (optional)
    try:
        output = insert_drawing_template(form_parameters)
        data = output['data']
        errors = output['errors']

        if errors:
            # If CATIA insertion fails but settings saved, show partial success
            if save_success:
                combined_message = f"{save_message}\nCATIA Error: {errors}"
                return render_template('partials/errors.html', errors=[combined_message])
            else:
                return render_template('partials/errors.html', errors=errors)

        if data:
            # Combine success messages
            combined_message = f"{save_message}\n{data}"
            return render_template('partials/success.html', data=combined_message)

    except Exception as e:
        # If CATIA is not available, just show settings save status
        if save_success:
            return render_template('partials/success.html', data=save_message)
        else:
            return render_template('partials/errors.html', errors=[str(e)])

    return render_template('partials/error.html')
