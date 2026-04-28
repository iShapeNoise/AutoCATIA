from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.add_page import get_sheets_for_drawing


@app.route(f'{htmx}/drawing/load_pages', methods=['POST'])
def htmx_load_pages():
    """Load pages for selected drawing and return table"""
    selected_drawing = request.form.get('selected_drawing')

    if not selected_drawing:
        return render_template(
            'partials/error.html',
            error='No drawing selected'
        )

    try:
        sheets = get_sheets_for_drawing(selected_drawing)

        if not sheets:
            return render_template(
                'partials/error.html',
                error='No pages found in drawing'
            )

        return render_template(
            'partials/drawing_pages_table.html',
            sheets=sheets,
            selected_drawing=selected_drawing
        )

    except Exception as e:
        return render_template(
            'partials/error.html',
            error=f'Error loading pages: {str(e)}'
        )
