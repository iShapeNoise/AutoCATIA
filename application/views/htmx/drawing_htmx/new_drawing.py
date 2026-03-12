from flask import request, render_template
from pathlib import Path

from application import app
from application.pycatia_scripts.drawing.drawing_template import insert_drawing_template
from application.views.view_wrappers import catia_v5_required
from application.views.url_prefixes import htmx
from pycatia import catia
from pycatia.drafting_interfaces.drawing_document import DrawingDocument
from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from pycatia.drafting_interfaces.drawing_texts import DrawingTexts
from pycatia.enumeration.enumeration_types import cat_paper_size
from pycatia.enumeration.enumeration_types import cat_text_anchor_position
from pycatia.knowledge_interfaces.parameters import Parameters

# Import utility functions from drawing_template_support
from application.pycatia_scripts.drawing.drawing_template_support.background_view import get_background_view_and_factory
from application.pycatia_scripts.drawing.drawing_template_support.text_properties import set_text_properties
from application.pycatia_scripts.drawing.drawing_template_support.title_block import add_title_block_text, add_param_text

def create_new_drawing_with_title(paper_size_key, title):
    """
    Create a new CATIA drawing with specified paper size and title
    """
    from pycatia.enumeration.enumeration_types import cat_paper_size
    from application.pycatia_scripts.settings import drawing_template
    from application.pycatia_scripts.drawing.drawing_template_support.parameters import create_parameters

    # Fixed paper size mapping - A4-portrait should be 4, not 0
    size_mapping = {
        'A4-portrait': 4,    # catPaperA4 (fixed)
        'A4-landscape': 5,   # catPaperA4Landscape
        'A3': 3,             # catPaperA3
        'A2': 2,             # catPaperA2
        'A1': 1              # catPaperA1
    }

    try:
        # Get CATIA application and create new drawing
        catia_instance = catia()
        documents = catia_instance.documents
        new_drawing = documents.add('Drawing')

        # Set paper size immediately after creation
        sheets = new_drawing.sheets
        sheet = sheets.item(1)
        sheet.paper_size = size_mapping[paper_size_key]

        # Rename the sheet
        sheet.name = title

        # Get background view and factory
        background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
        texts = background_view.texts

        # Create parameters FIRST before trying to link text
        form_parameters = {
            'TITLE': title,
            'DRAWING-NUMBER': 'DN-001',
            'CREATED-ON': '01.01.2024',
            'AUTHOR': 'User',
            'MANAGER': 'Manager',
            'PART-NUMBER': 'PN-001',
            'MATERIAL': 'Material',
            'COMMENTS': 'Comments',
            'DOCUMENT-TYPE': 'Type'
        }

        # Use the existing create_parameters function
        parameters = create_parameters(new_drawing, form_parameters)

        # Draw text field boundaries with fixed coordinates
        text_positions = {
            'title': {'x': 20, 'y': 200, 'width': 150, 'height': 10},
            'drawing_number': {'x': 20, 'y': 180, 'width': 100, 'height': 8},
            'created_on': {'x': 20, 'y': 160, 'width': 80, 'height': 8},
            'author': {'x': 20, 'y': 140, 'width': 80, 'height': 8},
            'manager': {'x': 20, 'y': 120, 'width': 80, 'height': 8},
            'part_number': {'x': 20, 'y': 100, 'width': 80, 'height': 8},
            'material': {'x': 20, 'y': 80, 'width': 80, 'height': 8},
            'comments': {'x': 20, 'y': 60, 'width': 150, 'height': 8},
            'document_type': {'x': 20, 'y': 40, 'width': 80, 'height': 8}
        }

        # Draw boundary lines
        for field_name, pos in text_positions.items():
            try:
                # Bottom line
                factory_2d.create_line(pos['x'], pos['y'], pos['x'] + pos['width'], pos['y'])
                # Top line
                factory_2d.create_line(pos['x'], pos['y'] + pos['height'], pos['x'] + pos['width'], pos['y'] + pos['height'])
                # Left line
                factory_2d.create_line(pos['x'], pos['y'], pos['x'], pos['y'] + pos['height'])
                # Right line
                factory_2d.create_line(pos['x'] + pos['width'], pos['y'], pos['x'] + pos['width'], pos['y'] + pos['height'])
            except Exception as e:
                print(f"Error drawing boundary for {field_name}: {e}")

        # Create parameter-linked text fields
        param_mapping = {
            'title': 'TITLE',
            'drawing_number': 'DRAWING-NUMBER',
            'created_on': 'CREATED-ON',
            'author': 'AUTHOR',
            'manager': 'MANAGER',
            'part_number': 'PART-NUMBER',
            'material': 'MATERIAL',
            'comments': 'COMMENTS',
            'document_type': 'DOCUMENT-TYPE'
        }

        for field_name, param_name in param_mapping.items():
            try:
                pos = text_positions[field_name]
                add_param_text(texts, parameters, param_name, pos['x'] + 2, pos['y'] + 2)
            except Exception as e:
                print(f"Error creating parameter text for {field_name}: {e}")
                # Fallback to static text
                pos = text_positions[field_name]
                add_title_block_text(texts, form_parameters[param_name], pos['x'] + 2, pos['y'] + 2)

        # Reframe the view
        viewer = new_drawing.application.active_window
        viewer.active_viewer.reframe()

        return {'success': True, 'message': f'Created new drawing: {title}'}

    except Exception as e:
        return {'success': False, 'error': str(e)}


# HTMX route handlers for each paper size
@app.route(f'{htmx}/drawing/new/a4_portrait', methods=['POST'])
@catia_v5_required
def create_new_drawing_a4_portrait():
    return create_new_drawing_with_title('A4-portrait', 'A4 Portrait Drawing')

@app.route(f'{htmx}/drawing/new/a4_landscape', methods=['POST'])
@catia_v5_required
def create_new_drawing_a4_landscape():
    return create_new_drawing_with_title('A4-landscape', 'A4 Landscape Drawing')

@app.route(f'{htmx}/drawing/new/a3', methods=['POST'])
@catia_v5_required
def create_new_drawing_a3():
    return create_new_drawing_with_title('A3', 'A3 Drawing')

@app.route(f'{htmx}/drawing/new/a2', methods=['POST'])
@catia_v5_required
def create_new_drawing_a2():
    return create_new_drawing_with_title('A2', 'A2 Drawing')
