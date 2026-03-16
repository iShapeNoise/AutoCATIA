from flask import request, render_template

from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.new_drawing import create_new_drawing_with_title


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
    result = create_new_drawing_with_title('A4-portrait', 'A4 Portrait Drawing')
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a4_landscape', methods=['POST'])
def htmx_new_drawing_a4_landscape():
    result = create_new_drawing_with_title('A4-landscape', 'A4 Landscape Drawing')
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a3', methods=['POST'])
def htmx_new_drawing_a3():
    result = create_new_drawing_with_title('A3', 'A3 Drawing')
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a2', methods=['POST'])
def htmx_new_drawing_a2():
    result = create_new_drawing_with_title('A2', 'A2 Drawing')
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a1', methods=['POST'])
def htmx_new_drawing_a1():
    result = create_new_drawing_with_title('A1', 'A1 Drawing')
    return handle_drawing_response(result)


@app.route(f'{htmx}/drawing/new/a0', methods=['POST'])
def htmx_new_drawing_a0():
    result = create_new_drawing_with_title('A0', 'A0 Drawing')
    return handle_drawing_response(result)
