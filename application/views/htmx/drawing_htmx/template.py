from flask import request, render_template
from pathlib import Path
import yaml

from application import app
from application.pycatia_scripts.drawing.drawing_template import insert_drawing_template
from application.views.url_prefixes import htmx


@app.route(f'{htmx}/drawing/template', methods=['POST'])
def htmx_drawing_template():
    """Handle template form submission - saves settings and optionally inserts template"""
    # Get all form parameters
    part_number = request.form.get('DRAWING-NUMBER', type=str) or ""
    title = request.form.get('TITLE', type=str) or ""
    created_by = request.form.get('CREATED-BY', type=str) or ""
    revision = request.form.get('REVISION', type=str) or ""

    # Save to settings.yaml
    try:
        # Get path to userdata/settings.yaml
        app_root = Path(__file__).parent.parent.parent
        settings_path = Path(app_root, 'userdata', 'settings.yaml')

        # Read existing settings
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = yaml.safe_load(f) or {}
        else:
            settings = {}

        # Ensure drawing_template section exists
        if 'drawing_template' not in settings:
            settings['drawing_template'] = {}
        if 'parameters' not in settings['drawing_template']:
            settings['drawing_template']['parameters'] = {}

        # Update parameters with form values (only if not empty)
        if part_number:
            settings['drawing_template']['parameters']['DRAWING-NUMBER'] = part_number
        if title:
            settings['drawing_template']['parameters']['TITLE'] = title
        if created_by:
            settings['drawing_template']['parameters']['CREATED-BY'] = created_by
        if revision:
            settings['drawing_template']['parameters']['REVISION'] = revision

        # Save settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)

        save_message = "Template settings saved successfully!"

    except Exception as e:
        save_message = f"Error saving settings: {str(e)}"

    # Try to insert template in CATIA (may fail if no active document)
    try:
        form_parameters = {
            'DRAWING-NUMBER': part_number,
            'TITLE': title,
            'CREATED-BY': created_by,
            'REVISION': revision,
        }

        output = insert_drawing_template(form_parameters)
        data = output['data']
        errors = output['errors']

        if errors:
            # If CATIA errors but settings saved, show partial success
            combined_message = f"{save_message}\n\nCATIA Error: {'; '.join(errors)}"
            return render_template('partials/errors.html', errors=[combined_message])

        if data:
            # Success in both saving and CATIA insertion
            combined_message = f"{save_message}\n\n{data}"
            return render_template('partials/success.html', data=combined_message)

    except Exception as e:
        # CATIA operation failed, but settings might have saved
        combined_message = f"{save_message}\n\nCATIA Error: {str(e)}"
        return render_template('partials/errors.html', errors=[combined_message])

    # Fallback
    return render_template('partials/error.html')


@app.route(f'{htmx}/drawing/template/save', methods=['POST'])
def htmx_drawing_template_save():
    """Save template settings without requiring CATIA"""
    # Get all form parameters
    part_number = request.form.get('DRAWING-NUMBER', type=str) or ""
    title = request.form.get('TITLE', type=str) or ""
    created_by = request.form.get('CREATED-BY', type=str) or ""
    revision = request.form.get('REVISION', type=str) or ""

    try:
        # Get path to userdata/settings.yaml
        settings_path = Path(__file__).parent.parent.parent.parent.parent / 'userdata' / 'settings.yaml'
        print(settings_path)

        # Read existing settings
        if settings_path.exists():
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = yaml.safe_load(f) or {}
        else:
            settings = {}

        # Ensure drawing_template section exists
        if 'drawing_template' not in settings:
            settings['drawing_template'] = {}
        if 'parameters' not in settings['drawing_template']:
            settings['drawing_template']['parameters'] = {}

        # Update parameters with form values (only if not empty)
        if part_number:
            settings['drawing_template']['parameters']['DRAWING-NUMBER'] = part_number
        if title:
            settings['drawing_template']['parameters']['TITLE'] = title
        if created_by:
            settings['drawing_template']['parameters']['CREATED-BY'] = created_by
        if revision:
            settings['drawing_template']['parameters']['REVISION'] = revision

        # Save settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)

        return render_template('partials/success.html', data="Template settings saved successfully!")

    except Exception as e:
        return render_template('partials/errors.html', errors=[f"Error saving settings: {str(e)}"])
