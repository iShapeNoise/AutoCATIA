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


@app.route('/drawing/edit_page')
@catia_v5_required
def drawing_edit_page():
    from application.pycatia_scripts.the_document import PTDrawingDocument
    from application.pycatia_scripts.com_objects import get_app_object

    # Get CATIA application
    application = get_app_object()
    if not application:
        return render_template('drawing_edit_page.html',
                             error="CATIA application is not running")

    # Get drawing document details
    try:
        pt_drawing = PTDrawingDocument()
        if not pt_drawing.is_drawing_document():
            return render_template('drawing_edit_page.html',
                                 error="No active drawing document")

        details = pt_drawing.details
        sheets = list(details.get('sheets', {}).keys())

        return render_template('drawing_edit_page.html',
                             sheets=sheets,
                             file_name=details.get('file_name', ''))

    except Exception as e:
        return render_template('drawing_edit_page.html',
                             error=f"Error getting drawing details: {str(e)}")

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
