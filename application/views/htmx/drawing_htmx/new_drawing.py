from flask import request, render_template
from pathlib import Path
import json

from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.com_objects import get_app_object
from application.pycatia_scripts.drawing.new_drawing_support.frames import create_frame_lines
from application.pycatia_scripts.drawing.new_drawing_support.text_field import create_text_field



def create_new_drawing_with_title(paper_size_key, title):
    """
    Create a new CATIA drawing with specified paper size and title
    """
    from pycatia.enumeration.enumeration_types import cat_paper_size
    from application.pycatia_scripts.common import get_output
    from application.pycatia_scripts.settings import iso_standards
    from application.pycatia_scripts.common import get_output

    # Get CATIA application using the helper function
    application = get_app_object()

    if not application:
        return {"error": "CATIA is not running"}

    # Initialize standardized output
    output = get_output()

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

    create_frame_lines(sheet, paper_size_key)

    # try:
    #     create_trimming_marks(sheet, paper_size_key)
    # except Exception as e:
    #     print(f"Warning: Could not create trimming marks: {e}")

    sheet.name = title
    # Force update to apply changes
    sheet.force_update()

    # Get sheet dimensions from ISO_216
    sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
    sheet_x, sheet_y = sheet_dimensions

    # Create frame lines
    create_frame_lines(sheet, paper_size_key)

    # Create text field with labels (after frames)
    #create_text_field(sheet, sheet_x, sheet_y, paper_size_key)

    return {"success": True, "message": f"Created {paper_size_key} drawing with title: {title}"}


def handle_drawing_response(result):
    """Handle drawing operation responses with defensive error checking"""
    errors = result.get('errors', [])

    if errors:
        return render_template('partials/errors.html', errors=errors)

    # Check if data exists, provide fallback if missing
    data = result.get('data')
    if data:
        return render_template('partials/success.html', data=data)
    else:
        # Fallback for missing data - could be a simple success message
        return render_template('partials/success.html', data="Operation completed successfully")


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
