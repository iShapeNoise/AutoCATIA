from pathlib import Path
import json
from flask import render_template, request, redirect, url_for, flash
from application import app
from application.views.view_wrappers import catia_v5_required
from application.pycatia_scripts.language import lang_manager
from application.views.url_prefixes import htmx
from application.pycatia_scripts.settings import load_settings
import os
from werkzeug.utils import secure_filename


@app.route('/settings', methods=['GET', 'POST'])
@catia_v5_required
def settings():
    # Get path to userdata/settings (no extension - this IS the JSON file)
    app_root = Path(__file__).parent.parent.parent
    settings_path = Path(app_root, 'userdata', 'settings')
    userdata_path = Path(app_root, 'userdata')

    # Ensure userdata directory exists
    userdata_path.mkdir(exist_ok=True)

    # Load settings using the proper function
    settings_data = load_settings()
    drawing_template = settings_data.get('drawing_template', {})

    current_logo = drawing_template.get('logo', '')
    current_projection_method = drawing_template.get('projection_method', 'PM_EU.jpg')

    # Scan for image files in userdata
    available_logos = []
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.tiff'}

    if userdata_path.exists():
        for file_path in userdata_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                available_logos.append(file_path.name)

    available_logos.sort()  # Sort alphabetically

    if request.method == 'POST':
        # Debug: Print all form data
        print(f"DEBUG: Form data received: {dict(request.form)}")

        try:
            # Handle logo selection from dropdown
            selected_logo = request.form.get('LOGO_SELECT', '')

            # Handle projection method selection
            projection_method = request.form.get('projection_method', 'PM_EU.jpg')

            # Update drawing template settings
            if 'drawing_template' not in settings_data:
                settings_data['drawing_template'] = {}

            settings_data['drawing_template']['logo'] = selected_logo
            settings_data['drawing_template']['projection_method'] = projection_method

            # Handle language setting
            language = request.form.get('LANGUAGE', '')
            if language:
                settings_data['language'] = language

            # Handle theme setting
            theme = request.form.get('THEME', 'dark')
            if theme:
                settings_data['ui_theme'] = theme

            # Handle notification settings
            notifications_enabled = request.form.get('notifications_enabled') == 'on'
            visibility_seconds = int(request.form.get('visibility_seconds', 2))

            if 'notifications' not in settings_data:
                settings_data['notifications'] = {}

            settings_data['notifications']['enabled'] = notifications_enabled
            settings_data['notifications']['visibility_seconds'] = visibility_seconds

            # Handle drawing template parameters
            if 'parameters' not in settings_data['drawing_template']:
                settings_data['drawing_template']['parameters'] = {}

            template_params = [
                'SCALE', 'DOCUMENT-TYPE', 'CREATED-BY', 'APPROVED-BY',
                'TITLE', 'EXTRA-TITLE', 'NUMBER', 'MATERIAL', 'BLANK',
                'REVISION', 'DATE', 'FORMAT', 'PAGE'
            ]

            for param in template_params:
                value = request.form.get(param, '')
                settings_data['drawing_template']['parameters'][param] = value

            # Save settings
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)

            flash(lang_manager.t('pages.settings.changes_saved', 'Changes saved in /userdata/settings'), 'success')
            return redirect(url_for('settings'))

        except Exception as e:
            print(f"DEBUG: Error saving settings: {e}")
            flash(lang_manager.t('pages.settings.save_error', f'Error saving settings: {e}'), 'danger')
            return redirect(url_for('settings'))

    # Extract parameters for the drawing template form
    parameters = drawing_template.get('parameters', {})

    return render_template('settings.html',
                         current_logo=current_logo,
                         current_projection_method=current_projection_method,
                         available_logos=available_logos,
                         drawing_template=drawing_template,
                         parameters=parameters,
                         settings=settings_data)
