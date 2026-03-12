from pathlib import Path
import yaml

from flask import render_template

from application import app
from application.views.view_wrappers import catia_v5_required
from application.pycatia_scripts.settings import drawing_template
from application.pycatia_scripts.settings import yaml_data


@app.route('/drawing')
@catia_v5_required
def drawing():
    return render_template(
        'drawing.html',
    )


@app.route('/drawing/new')
@catia_v5_required
def drawing_new():
    return render_template('drawing_new.html')


@app.route('/drawing/views')
@catia_v5_required
def drawing_views():
    return render_template(
        'drawing_views.html',
    )


@app.route('/drawing/save_as')
@catia_v5_required
def drawing_save_as():
    exclude_sheets = ', '.join(yaml_data['drawing']['pdf']['exclude_sheets'])
    return render_template(
        'drawing_save_as.html',
        exclude_sheets=exclude_sheets,
    )


@app.route('/drawing/save_as/pdf')
@catia_v5_required
def drawing_save_as_pdf():
    exclude_sheets = ', '.join(yaml_data['drawing']['pdf']['exclude_sheets'])
    return render_template(
        'drawing_save_as_pdf.html',
        exclude_sheets=exclude_sheets,
    )


@app.route('/drawing/save_as/dxf')
@catia_v5_required
def drawing_save_as_dxf():
    include_sheets = ', '.join(yaml_data['drawing']['dxf']['include_sheets'])
    return render_template(
        'drawing_save_as_dxf.html',
        include_sheets=include_sheets,
    )


@app.route('/drawing/insert_template')
@catia_v5_required
def drawing_insert_template():
    # Load default parameters
    parameters = drawing_template['parameters'].copy()

    # Try to load saved values from userdata/settings.yaml
    try:
        # Get path to userdata/settings.yaml
        app_root = Path(__file__).parent.parent.parent
        settings_path = Path(app_root, 'userdata', 'settings.yaml')

        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings_data = yaml.safe_load(f)
                if 'drawing_template' in settings_data and 'parameters' in settings_data['drawing_template']:
                    # Update with saved values
                    parameters.update(settings_data['drawing_template']['parameters'])
    except Exception:
        pass  # Use defaults if loading fails

    return render_template(
        'drawing_template.html',
        parameters=parameters
    )
