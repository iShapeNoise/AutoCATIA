from flask import request, jsonify
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.com_objects import get_app_object
from pycatia.drafting_interfaces.drawing_document import DrawingDocument

@app.route(f'{htmx}/drawing/get_pages', methods=['POST'])
def htmx_get_pages():
    """Get pages for a specific drawing"""
    drawing_name = request.form.get('drawing_name')

    try:
        application = get_app_object()
        if not application:
            return '<option value="">Error: CATIA not found</option>'

        documents = application.documents
        target_drawing = None

        # Find the drawing by name (with .CATDrawing extension)
        for i in range(documents.count):
            doc = documents.item(i + 1)
            if doc.name == drawing_name or doc.name == f"{drawing_name}.CATDrawing":
                target_drawing = doc
                break

        if not target_drawing:
            return f'<option value="">Error: Drawing "{drawing_name}" not found</option>'

        # Get sheets from the drawing
        drawing_doc = DrawingDocument(target_drawing.com_object)
        sheets = drawing_doc.sheets

        # Build HTML options
        options = []
        for sheet in sheets:
            options.append(f'<option value="{sheet.name}">{sheet.name}</option>')

        if not options:
            return '<option value="">No pages found</option>'

        return ''.join(options)

    except Exception as e:
        return f'<option value="">Error: {str(e)}</option>'
