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
        # Handle logo selection from dropdown
        selected_logo = request.form.get('LOGO_SELECT', '')

        # Handle projection method selection
        projection_method = request.form.get('projection_method', 'PM_EU.jpg')

        # Update drawing template settings
        if 'drawing_template' not in settings_data:
            settings_data['drawing_template'] = {}

        settings_data['drawing_template']['logo'] = selected_logo
        settings_data['drawing_template']['projection_method'] = projection_method

        # Handle other form fields (language, etc.)
        language = request.form.get('LANGUAGE', '')
        if language:
            settings_data['language'] = language

        # Save settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings_data, f, indent=2, ensure_ascii=False)

        flash(lang_manager.t('pages.settings.saved_successfully', 'Settings saved successfully!'), 'success')
        return redirect(url_for('settings'))

    return render_template('settings.html',
                         current_logo=current_logo,
                         current_projection_method=current_projection_method,
                         available_logos=available_logos,
                         drawing_template=drawing_template)
