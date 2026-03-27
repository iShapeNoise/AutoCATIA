from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.add_page import add_page_with_title


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
    result = add_page_with_title('A4-portrait', 'A4 Portrait Page')
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a4_landscape', methods=['POST'])
def htmx_add_page_a4_landscape():
    result = add_page_with_title('A4-landscape', 'A4 Landscape Page')
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a3', methods=['POST'])
def htmx_add_page_a3():
    result = add_page_with_title('A3', 'A3 Page')
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a2', methods=['POST'])
def htmx_add_page_a2():
    result = add_page_with_title('A2', 'A2 Page')
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a1', methods=['POST'])
def htmx_add_page_a1():
    result = add_page_with_title('A1', 'A1 Page')
    return handle_page_response(result)


@app.route(f'{htmx}/drawing/add_page/a0', methods=['POST'])
def htmx_add_page_a0():
    result = add_page_with_title('A0', 'A0 Page')
    return handle_page_response(result)
