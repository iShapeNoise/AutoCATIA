from pathlib import Path
from flask import render_template
from application import app
from application.views.view_wrappers import catia_v5_required
from application.pycatia_scripts.settings import drawing_template
from application.pycatia_scripts.drawing.add_page import check_open_drawings, get_sheets_for_drawing
from application.pycatia_scripts.settings import settings_data


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
    from application.pycatia_scripts.settings import load_settings

    # Load settings for checkbox states
    settings_data = load_settings()

    return render_template('drawing_new.html', settings=settings_data)


@app.route('/drawing/edit_page')
@catia_v5_required
def drawing_edit_page():
    from application.pycatia_scripts.the_document import PTDrawingDocument
    from application.pycatia_scripts.com_objects import get_app_object
    from application.pycatia_scripts.drawing.add_page import check_open_drawings, get_sheets_for_drawing
    from application.pycatia_scripts.settings import load_settings

    # Get open drawings
    open_drawings = check_open_drawings()

    # Get sheets for the first available drawing
    sheets = []
    selected_drawing = None

    if open_drawings:
        selected_drawing = open_drawings[0]
        sheets = get_sheets_for_drawing(selected_drawing)

    # Load settings for GD&T checkboxes
    settings_data = load_settings()

    return render_template('drawing_edit_page.html',
                         open_drawings=open_drawings,
                         sheets=sheets,
                         selected_drawing=selected_drawing,
                         settings=settings_data)


@app.route('/drawing/views')
@catia_v5_required
def drawing_views():
    return render_template(
        'drawing_views.html',
    )


@app.route('/drawing/bom')
@catia_v5_required
def drawing_bom():
    return render_template('drawing_bom.html')


@app.route('/drawing/save_as')
@catia_v5_required
def drawing_save_as():
    from application.views.htmx.drawing_htmx import save_as
    exclude_sheets = ', '.join(settings_data['drawing']['pdf']['exclude_sheets'])
    return render_template(
        'drawing_save_as.html',
        exclude_sheets=exclude_sheets,
    )


@catia_v5_required
def drawing_save_as_pdf():
    from application.views.htmx.drawing_htmx import save_as
    exclude_sheets = ', '.join(settings_data['drawing']['pdf']['exclude_sheets'])
    return render_template(
        'drawing_save_as_pdf.html',
        exclude_sheets=exclude_sheets,
    )

@app.route('/drawing/save_as/dxf')
@catia_v5_required
def drawing_save_as_dxf():
    from application.views.htmx.drawing_htmx import save_as
    include_sheets = ', '.join(settings_data['drawing']['dxf']['include_sheets'])
    return render_template(
        'drawing_save_as_dxf.html',
        include_sheets=include_sheets,
    )


@app.route('/drawing/insert_template')
@catia_v5_required
def drawing_insert_template():
    """Redirect to Settings page for template editing"""
    return redirect(url_for('settings') + '#drawing')
