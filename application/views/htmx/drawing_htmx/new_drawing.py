from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.new_drawing import create_new_drawing_with_info


def handle_drawing_response(result):
    """Handle drawing operation responses"""
    errors = result.get('errors', [])
    if errors:
        return render_template('partials/errors.html', errors=errors)
    data = result.get('data')
    if data:
        return render_template('partials/success.html', data=data)
    return render_template('partials/success.html', data='Drawing created successfully')


@app.route(f'{htmx}/drawing/new/a4_portrait', methods=['POST'])
def htmx_new_drawing_a4_portrait():
    page_name = request.form.get('page_name', 'A4 Portrait Drawing')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = create_new_drawing_with_info('A4-portrait', page_name, document_type, part_number)
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a4_landscape', methods=['POST'])
def htmx_new_drawing_a4_landscape():
    page_name = request.form.get('page_name', 'A4 Landscape Drawing')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = create_new_drawing_with_info('A4-landscape', page_name, document_type, part_number)
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a3', methods=['POST'])
def htmx_new_drawing_a3():
    page_name = request.form.get('page_name', 'A3 Drawing')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = create_new_drawing_with_info('A3', page_name, document_type, part_number)
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a2', methods=['POST'])
def htmx_new_drawing_a2():
    page_name = request.form.get('page_name', 'A2 Drawing')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = create_new_drawing_with_info('A2', page_name, document_type, part_number)
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a1', methods=['POST'])
def htmx_new_drawing_a1():
    page_name = request.form.get('page_name', 'A1 Drawing')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = create_new_drawing_with_info('A1', page_name, document_type, part_number)
    return handle_drawing_response(result)

@app.route(f'{htmx}/drawing/new/a0', methods=['POST'])
def htmx_new_drawing_a0():
    page_name = request.form.get('page_name', 'A0 Drawing')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = create_new_drawing_with_info('A0', page_name, document_type, part_number)
    return handle_drawing_response(result)
