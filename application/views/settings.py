from pathlib import Path
import json
from flask import render_template, request, redirect, url_for, flash, session
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
            language = request.form.get('LANGUAGE', 'en')
            if language:
                settings_data['language'] = language
                # Clear session to force LanguageManager to read from settings
                session.pop('language', None)

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

            # Handle default attributes
            if 'default_attributes' not in settings_data:
                settings_data['default_attributes'] = {}

            default_attr_fields = [
                'part_number', 'revision', 'nomenclature', 'definition',
                'source', 'description'
            ]

            for field in default_attr_fields:
                value = request.form.get(field, '')
                settings_data['default_attributes'][field] = value

            # Handle user attributes
            if 'user_attributes' not in settings_data:
                settings_data['user_attributes'] = {}

            user_attr_fields = [
                'title', 'extra_title', 'document_type', 'created_by',
                'approved_by', 'material', 'blank', 'date', 'scale'
            ]

            for field in user_attr_fields:
                value = request.form.get(field, '')
                settings_data['user_attributes'][field] = value

            # Handle B.O.M. settings
            bom_columns = request.form.getlist('bom_columns')
            if 'bom' not in settings_data:
                settings_data['bom'] = {}

            settings_data['bom']['columns'] = {}
            all_bom_columns = [
                'title', 'created_by', 'subject', 'description',
                'keywords', 'category', 'status', 'material',
                'mass', 'part_number', 'rev', 'project',
                'custom', 'date', 'last_saved_by', 'last_modified_time',
                'checked_by', 'manager', 'company', 'hyperlink_base',
                'pos', 'part_number_2', 'quantity', 'object_quantity',
                'base_unit', 'base_quantity', 'bom_structure', 'comment'
            ]

            for column in all_bom_columns:
                settings_data['bom']['columns'][column] = column in bom_columns

            # Handle drawing options checkboxes
            text_field_enabled = request.form.get('text_field_enabled') == 'on'
            gdt_enabled = request.form.get('gdt_enabled') == 'on'

            settings_data['text_field_enabled'] = text_field_enabled
            settings_data['gdt_enabled'] = gdt_enabled

            # Handle GD&T subsection checkboxes
            gdt_options = [
                'gdt_general_abc', 'gdt_general_ab', 'gdt_welded_structure',
                'gdt_of_rz_63', 'gdt_ofz_general', 'gdt_ofz_wxy',
                'gdt_ofz_main_specs', 'gdt_ofz_main_raw', 'gdt_ofz_main',
                'gdt_edges_iso', 'gdt_thermally_cut'
            ]

            for option in gdt_options:
                settings_data[option] = request.form.get(option) == 'on'

            # Save settings
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)

            flash(lang_manager.t('pages.settings.changes_saved', 'Changes saved in /userdata/settings'), 'success')
            return redirect(url_for('settings'))

        except Exception as e:
            print(f"DEBUG: Error saving settings: {e}")
            flash(lang_manager.t('pages.settings.save_error', f'Error saving settings: {e}'), 'danger')
            return redirect(url_for('settings'))

    # Extract attributes for the form
    default_attributes = settings_data.get('default_attributes', {})
    user_attributes = settings_data.get('user_attributes', {})

    return render_template('settings.html',
                         current_logo=current_logo,
                         current_projection_method=current_projection_method,
                         available_logos=available_logos,
                         drawing_template=drawing_template,
                         default_attributes=default_attributes,
                         user_attributes=user_attributes,
                         settings=settings_data)
