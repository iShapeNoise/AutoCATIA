from flask import request, render_template
from application import app
from application.pycatia_scripts.com_objects import get_app_object
from application.pycatia_scripts.drawing.bom import (
    check_drawing_bom,
    create_drawing_bom,
    save_drawing_bom_changes,
    get_related_product_bom_data
)
from application.views.url_prefixes import htmx


def extract_bom_data_from_form(form_data):
    """Extract B.O.M. data from form submission"""
    bom_data = []

    # Find all B.O.M. data entries from the form
    row_keys = {}
    for key in form_data.keys():
        if key.startswith('bom_data_'):
            parts = key.split('_')
            if len(parts) >= 4:
                row_index = int(parts[2])
                column = '_'.join(parts[3:])

                if row_index not in row_keys:
                    row_keys[row_index] = {}
                row_keys[row_index][column] = form_data[key]

    # Convert to list of rows
    for row_index in sorted(row_keys.keys()):
        bom_data.append(row_keys[row_index])

    return bom_data


@app.route(f'{htmx}/drawing/bom/drawings', methods=['GET'])
def htmx_drawing_bom_drawings():
    """Get list of open CATIA drawings"""
    application = get_app_object()
    if not application:
        return '<option value="">No Drawing found. Please open a Drawing in Catia to proceed!</option>'

    drawings = []
    documents = application.documents

    for i in range(documents.count):
        doc = documents.item(i + 1)
        if doc.name.endswith('.CATDrawing'):
            drawings.append({
                'name': doc.name,
                'part_number': doc.name.replace('.CATDrawing', '')
            })

    if not drawings:
        return '<option value="">No Drawing found. Please open a Drawing in Catia to proceed!</option>'

    options = []
    if len(drawings) == 1:
        # Auto-select the single drawing
        options.append(f'<option value="{drawings[0]["part_number"]}" selected>{drawings[0]["name"]}</option>')
    else:
        # Multiple drawings - show "Select Drawing" placeholder
        options.append('<option value="" selected>Select Drawing</option>')
        for drawing in drawings:
            options.append(f'<option value="{drawing["part_number"]}">{drawing["name"]}</option>')

    return '\n'.join(options)


@app.route(f'{htmx}/drawing/bom/check', methods=['GET'])
def htmx_drawing_bom_check():
    """Check if B.O.M. exists for selected drawing"""
    drawing_name = request.args.get('drawing')
    if not drawing_name:
        return ''

    try:
        has_bom = check_drawing_bom(drawing_name)
    except:
        has_bom = False

    return render_template('partials/bom_actions.html',
                         drawing_name=drawing_name,
                         has_bom=has_bom)


@app.route(f'{htmx}/drawing/bom/create', methods=['POST'])
def htmx_drawing_bom_create():
    """Create new B.O.M. for drawing"""
    drawing_name = request.form.get('drawing')
    selected_columns = request.form.getlist('columns')

    if not drawing_name:
        return '<div class="alert alert-danger">No drawing selected</div>'

    # Get B.O.M. data from related product
    product_bom_data = get_related_product_bom_data(drawing_name)

    # Create B.O.M. in drawing
    result = create_drawing_bom(drawing_name, selected_columns, product_bom_data)

    if result['errors']:
        error_html = '<div class="alert alert-danger">'
        for error in result['errors']:
            error_html += f'{error}<br>'
        error_html += '</div>'
        return error_html

    # Render B.O.M. table with data
    return render_template('partials/bom_table.html',
                         drawing_name=drawing_name,
                         bom_data=result.get('bom_data', []),
                         selected_columns=selected_columns)


@app.route(f'{htmx}/drawing/bom/edit', methods=['POST'])
def htmx_bom_edit():
    """Edit existing B.O.M. in drawing"""
    drawing_name = request.form.get('drawing')

    if not drawing_name:
        return '<div class="alert alert-danger">No drawing selected</div>'

    try:
        # Get existing B.O.M. data from drawing
        bom_data = get_drawing_bom_data(drawing_name)

        if not bom_data:
            return '<div class="alert alert-warning">No B.O.M. data found</div>'

        # Get selected columns from settings
        from application.pycatia_scripts.settings import load_settings
        settings = load_settings()
        selected_columns = [col for col, enabled in settings['bom']['columns'].items() if enabled]

        return render_template(
            'partials/bom_table.html',
            bom_data=bom_data,
            columns=selected_columns,
            drawing_name=drawing_name
        )

    except Exception as e:
        return f'<div class="alert alert-danger">Error loading B.O.M.: {str(e)}</div>'


@app.route(f'{htmx}/drawing/bom/save', methods=['POST'])
def htmx_drawing_bom_save():
    """Save B.O.M. changes to CATIA drawing"""
    drawing_name = request.form.get('drawing')
    bom_data = extract_bom_data_from_form(request.form)

    if not drawing_name:
        return '<div class="alert alert-danger">No drawing selected</div>'

    # Save B.O.M. changes to CATIA
    result = save_drawing_bom_changes(drawing_name, bom_data)

    if result['errors']:
        error_html = '<div class="alert alert-danger">'
        for error in result['errors']:
            error_html += f'{error}<br>'
        error_html += '</div>'
        return error_html

    return '<div class="alert alert-success">B.O.M. saved successfully to CATIA</div>'
