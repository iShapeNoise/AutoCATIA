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

@app.route('/drawing/new_drawing')
@catia_v5_required
def drawing_new():
    from application.views.htmx.drawing_htmx import new_drawing
    return render_template('drawing_new.html')


@app.route('/drawing/add_page')
@catia_v5_required
def drawing_add_page():
    from application.views.htmx.drawing_htmx import add_page
    return render_template('drawing_add_page.html')


@app.route('/drawing/views')
@catia_v5_required
def drawing_views():
    return render_template(
        'drawing_views.html',
    )


@app.route('/drawing/save_as')
@catia_v5_required
def drawing_save_as():
    from application.views.htmx.drawing_htmx import save_as
    exclude_sheets = ', '.join(yaml_data['drawing']['pdf']['exclude_sheets'])
    return render_template(
        'drawing_save_as.html',
        exclude_sheets=exclude_sheets,
    )


@app.route('/drawing/save_as/pdf')
@catia_v5_required
def drawing_save_as_pdf():
    from application.views.htmx.drawing_htmx import save_as
    exclude_sheets = ', '.join(yaml_data['drawing']['pdf']['exclude_sheets'])
    return render_template(
        'drawing_save_as_pdf.html',
        exclude_sheets=exclude_sheets,
    )


@app.route('/drawing/save_as/dxf')
@catia_v5_required
def drawing_save_as_dxf():
    from application.views.htmx.drawing_htmx import save_as
    include_sheets = ', '.join(yaml_data['drawing']['dxf']['include_sheets'])
    return render_template(
        'drawing_save_as_dxf.html',
        include_sheets=include_sheets,
    )


@app.route('/drawing/insert_template')
@catia_v5_required
def drawing_insert_template():
    """Redirect to Settings page for template editing"""
    return redirect(url_for('settings') + '#drawing')
