from flask import request, render_template
from pathlib import Path
import json

from application import app
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

        # Save ALL values (not just non-empty ones)  
        for key, value in form_parameters.items():
            settings_data['drawing_template']['parameters'][key] = value

        # Write back to file
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)

        return True, "Template settings saved successfully"

    except Exception as e:
        return False, f"Error saving settings: {e}"


@app.route(f'{htmx}/drawing/template', methods=['POST'])
def htmx_drawing_template():
    """Handle template form submission - saves settings only"""
    from datetime import datetime

    # Get all form parameters with the NEW field structure
    form_parameters = {
        'SCALE': request.form.get('SCALE', type=str) or "1:1",
        'DOCUMENT-TYPE': request.form.get('DOCUMENT-TYPE', type=str) or "",
        'CREATED-BY': request.form.get('CREATED-BY', type=str) or "",
        'APPROVED-BY': request.form.get('APPROVED-BY', type=str) or "",
        'TITLE': request.form.get('TITLE', type=str) or "",
        'EXTRA-TITLE': request.form.get('EXTRA-TITLE', type=str) or "",
        'NUMBER': request.form.get('NUMBER', type=str) or "",
        'MATERIAL': request.form.get('MATERIAL', type=str) or "",
        'BLANK': request.form.get('BLANK', type=str) or "",
        'REVISION': request.form.get('REVISION', type=str) or "",
        'DATE': request.form.get('DATE', type=str) or datetime.now().strftime("%m/%Y"),
        'FORMAT': request.form.get('FORMAT', type=str) or "",
        'PAGE': request.form.get('PAGE', type=str) or "1/1"
    }

    # Only save settings - no CATIA interaction
    save_success, save_message = save_template_settings(form_parameters)

    if save_success:
        return render_template('partials/success.html', data=save_message)
    else:
        return render_template('partials/errors.html', errors=[save_message])
