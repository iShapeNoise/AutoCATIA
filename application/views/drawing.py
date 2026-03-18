from pathlib import Path

from flask import render_template

from application import app
from application.views.view_wrappers import catia_v5_required
from application.pycatia_scripts.settings import drawing_template


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
    """Load and display the Edit Template form with saved values"""
    from application.pycatia_scripts.settings import load_settings

    # Load settings using JSON
    settings_data = load_settings()
    parameters = settings_data.get('drawing_template', {}).get('parameters', {})

    return render_template(
        'drawing_template.html',
        parameters=parameters
    )
