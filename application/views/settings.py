from pathlib import Path
import yaml
from flask import render_template, request, redirect, url_for, flash
from application import app
from application.views.view_wrappers import catia_v5_required
from application.pycatia_scripts.language import lang_manager


@app.route('/settings', methods=['GET', 'POST'])
@catia_v5_required
def settings():
    # Get path to userdata/settings.yaml
    app_root = Path(__file__).parent.parent.parent
    settings_path = Path(app_root, 'userdata', 'settings.yaml')

    if request.method == 'POST':
        # Load existing settings or create new dict
        try:
            with open(settings_path, 'r') as f:
                settings_data = yaml.safe_load(f) or {}
        except:
            settings_data = {}

        # Update language
        if 'language' in request.form:
            settings_data['language'] = request.form['language']
            lang_manager.set_language(request.form['language'])

        # Update logo path
        if 'logo_path' in request.form:
            settings_data['logo_path'] = request.form['logo_path']

        # Save settings
        with open(settings_path, 'w') as f:
            yaml.dump(settings_data, f, default_flow_style=False)

        flash('Settings saved successfully!')
        return redirect(url_for('settings'))

    # Load current settings for display
    current_language = lang_manager.current_lang
    logo_path = ''

    if settings_path.exists():
        try:
            with open(settings_path, 'r') as f:
                settings_data = yaml.safe_load(f) or {}
                logo_path = settings_data.get('logo_path', '')
        except:
            pass

    return render_template(
        'settings.html',
        current_language=current_language,
        logo_path=logo_path
    )
