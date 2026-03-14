from flask import request, render_template
from pathlib import Path
import json

from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.com_objects import get_app_object


def create_new_drawing_with_title(paper_size_key, title):
    """
    Create a new CATIA drawing with specified paper size and title
    """
    from pycatia.enumeration.enumeration_types import cat_paper_size, cat_paper_orientation
    from application.pycatia_scripts.com_objects import get_app_object
    from application.pycatia_scripts.drawing.new_drawing_support.frames import create_trimming_marks  

    # Get CATIA application using the helper function
    application = get_app_object()

    if not application:
        return {"error": "CATIA is not running"}

    # Create new drawing
    documents = application.documents
    drawing_document = documents.add('Drawing')
    drawing = drawing_document.drawing_root

    # Get the active sheet
    sheet = drawing.sheets.active_sheet

    # Map paper size keys to CATIA enum values
    paper_size_mapping = {
        'A0': 2,      # catPaperA0
        'A1': 3,      # catPaperA1
        'A2': 4,      # catPaperA2
        'A3': 5,      # catPaperA3
        'A4-portrait': 6,  # catPaperA4
        'A4-landscape': 6   # catPaperA4Landscape
    }

    # Get the paper size enum value
    catia_paper_size = paper_size_mapping.get(paper_size_key, 3)  # Default to A3

    # Set the paper size
    sheet.paper_size = catia_paper_size

    # Set orientation to portrait only for A4 Portrait
    if paper_size_key == 'A4-portrait':
        try:
            # Try direct integer value for portrait orientation
            sheet.orientation = 0  # 0 = catPaperPortrait
            sheet.force_update()
        except:
            # If orientation fails, continue without it
            pass

    try:
        create_trimming_marks(sheet, paper_size_key)
    except Exception as e:
        print(f"Warning: Could not create trimming marks: {e}")

    sheet.name = title
    # Force update to apply changes
    sheet.force_update()

    return {"success": True, "data": f"Created {title} with {paper_size_key} format"}


def handle_drawing_response(result):
    """Handle drawing creation response"""
    if 'error' in result:
        return render_template('partials/error.html', error=result['error'])
    return render_template('partials/success.html', data=result['data'])


# HTMX route handlers
@app.route(f'{htmx}/drawing/new/a0', methods=['POST'])
def htmx_new_drawing_a0():
    result = create_new_drawing_with_title('A0', 'A0 Drawing')
    return handle_drawing_response(result)

@app.route(f'{htmx}/drawing/new/a1', methods=['POST'])
def htmx_new_drawing_a1():
    result = create_new_drawing_with_title('A1', 'A1 Drawing')
    return handle_drawing_response(result)

@app.route(f'{htmx}/drawing/new/a2', methods=['POST'])
def htmx_new_drawing_a2():
    result = create_new_drawing_with_title('A2', 'A2 Drawing')
    return handle_drawing_response(result)

@app.route(f'{htmx}/drawing/new/a3', methods=['POST'])
def htmx_new_drawing_a3():
    result = create_new_drawing_with_title('A3', 'A3 Drawing')
    return handle_drawing_response(result)

@app.route(f'{htmx}/drawing/new/a4_portrait', methods=['POST'])
def htmx_new_drawing_a4_portrait():
    result = create_new_drawing_with_title('A4-portrait', 'A4 Portrait Drawing')
    return handle_drawing_response(result)

@app.route(f'{htmx}/drawing/new/a4_landscape', methods=['POST'])
def htmx_new_drawing_a4_landscape():
    result = create_new_drawing_with_title('A4-landscape', 'A4 Landscape Drawing')
    return handle_drawing_response(result)
