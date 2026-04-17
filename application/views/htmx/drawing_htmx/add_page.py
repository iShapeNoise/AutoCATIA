from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.add_page import add_page_with_info


def handle_page_response(result):
    """Handle new page operation responses"""
    errors = result.get('errors', [])
    if errors:
        return render_template('partials/errors.html', errors=errors)
    data = result.get('data')
    if data:
        return render_template('partials/success.html', data=data)
    return render_template('partials/success.html', data='Page added successfully')


@app.route(f'{htmx}/drawing/add_page/a4_portrait', methods=['POST'])
def htmx_add_page_a4_portrait():
    page_name = request.form.get('page_name', 'A4 Portrait Page')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = add_page_with_info('A4-portrait', page_name, document_type, part_number)
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a4_landscape', methods=['POST'])
def htmx_add_page_a4_landscape():
    page_name = request.form.get('page_name', 'A4 Landscape Page')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = add_page_with_info('A4-landscape', page_name, document_type, part_number)
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a3', methods=['POST'])
def htmx_add_page_a3():
    page_name = request.form.get('page_name', 'A3 Page')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = add_page_with_info('A3', page_name, document_type, part_number)
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a2', methods=['POST'])
def htmx_add_page_a2():
    page_name = request.form.get('page_name', 'A2 Page')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = add_page_with_info('A2', page_name, document_type, part_number)
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a1', methods=['POST'])
def htmx_add_page_a1():
    page_name = request.form.get('page_name', 'A1 Page')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = add_page_with_info('A1', page_name, document_type, part_number)
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a0', methods=['POST'])
def htmx_add_page_a0():
    page_name = request.form.get('page_name', 'A0 Page')
    document_type = request.form.get('document_type', '')
    part_number = request.form.get('partNumber', '')
    result = add_page_with_info('A0', page_name, document_type, part_number)
    return handle_page_response(result)
