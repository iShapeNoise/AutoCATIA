from pathlib import Path
from pycatia import catia
from pycatia.drafting_interfaces.drawing_document import DrawingDocument
from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from pycatia.enumeration.enumeration_types import cat_paper_size

from application.pycatia_scripts.common import get_output
from application.support.documents import get_drawing_document
from application.pycatia_scripts.settings import iso_standards, load_settings
from application.pycatia_scripts.com_objects import get_app_object

# Import support functions
from .new_drawing_support.frames import create_frame_lines
from .new_drawing_support.text_field import create_text_field


def check_open_drawings():
    """Check for open drawing documents and return their names"""
    try:
        application = get_app_object()
        if not application:
            print("DEBUG: CATIA application not found")
            return []

        documents = application.documents
        print(f"DEBUG: Found {documents.count} total documents")

        drawing_names = []

        for i in range(documents.count):
            doc = documents.item(i + 1)
            doc_name = doc.name
            print(f"DEBUG: Document {i+1}: {doc_name}")

            # Check if it's a drawing document
            if doc_name.lower().endswith('.catdrawing'):
                # Get the drawing name without extension for display
                display_name = doc_name.replace('.CATDrawing', '').replace('.catdrawing', '')
                drawing_names.append(display_name)
                print(f"DEBUG: Added drawing: {display_name}")

        print(f"DEBUG: Total drawings found: {drawing_names}")
        return drawing_names

    except Exception as e:
        print(f"DEBUG: Error in check_open_drawings: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def add_page_with_info(paper_size_key, page_name, document_type, part_number):
    """
    Add a new page with custom information from modal
    """
    try:
        # Check for multiple open drawings first
        open_drawings = check_open_drawings()

        if len(open_drawings) > 1:
            return {
                'success': False,
                'errors': [f"Multiple drawings detected: {', '.join(open_drawings)}. Please close extra drawings before adding a new page."]
            }

        if len(open_drawings) == 0:
            return {
                'success': False,
                'errors': ["No drawing document is currently open. Please open a drawing first."]
            }

        # Add the new page to the existing drawing
        result = add_page_to_drawing_with_info(paper_size_key, page_name, document_type, part_number)
        return result

    except Exception as e:
        return {
            'success': False,
            'errors': [f"Error adding new page: {str(e)}"]
        }


def add_page_to_drawing_with_info(paper_size_key, page_name, document_type, part_number):
    """Add a new page to an existing CATIA drawing with custom info"""
    try:
        # Get the active drawing document
        pt_drawing_document, errors = get_drawing_document()
        if errors:
            return {'success': False, 'errors': errors}

        drawing_document = pt_drawing_document.drawing_document
        drawing = drawing_document.drawing_root

        # Create new sheet
        sheets = drawing.sheets
        new_sheet = sheets.add(page_name or f"{paper_size_key} Page")

        # Set paper size and orientation
        paper_size_mapping = {
            'A0': 2, 'A1': 3, 'A2': 4, 'A3': 5, 'A4-portrait': 6, 'A4-landscape': 6
        }
        catia_paper_size = paper_size_mapping.get(paper_size_key, 3)
        new_sheet.paper_size = catia_paper_size

        if paper_size_key == 'A4-portrait':
            new_sheet.orientation = 0
        elif paper_size_key in ['A3', 'A2', 'A1', 'A4-landscape', 'A0']:
            new_sheet.orientation = 1

        new_sheet.force_update()

        # Get sheet dimensions and create elements
        sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
        sheet_x, sheet_y = sheet_dimensions

        # Create frame lines
        create_frame_lines(new_sheet, paper_size_key)

        # Create text field with custom info
        create_text_field_with_info(new_sheet, sheet_x, sheet_y, paper_size_key, page_name, document_type, part_number)

        return {"success": True, "message": f"Added {paper_size_key} page with custom info"}

    except Exception as e:
        return {'success': False, 'errors': [f"Failed to add page: {str(e)}"]}


def add_page_with_info(paper_size_key, page_name, document_type, part_number):
    """
    Add a new page with custom information from modal
    """
    try:
        # Check for multiple open drawings first
        open_drawings = check_open_drawings()

        if len(open_drawings) > 1:
            return {
                'success': False,
                'errors': [f"Multiple drawings detected: {', '.join(open_drawings)}. Please close extra drawings before adding a new page."]
            }

        if len(open_drawings) == 0:
            return {
                'success': False,
                'errors': ["No drawing document is currently open. Please open a drawing first."]
            }

        # Add the new page to the existing drawing
        result = add_page_to_drawing_with_info(paper_size_key, page_name, document_type, part_number)
        return result

    except Exception as e:
        return {
            'success': False,
            'errors': [f"Error adding new page: {str(e)}"]
        }


def create_text_field_with_info(sheet: DrawingSheet, sheet_x: float, sheet_y: float, paper_size_key: str, page_name: str, document_type: str, part_number: str):
    """
    Create text field with custom information from modal for add_page
    """
    from .new_drawing_support.text_field import create_text_field, add_text_field_values
    from .new_drawing_support.background_view import get_background_view_and_factory
    from pycatia.enumeration.enumeration_types import cat_text_anchor_position
    from application.pycatia_scripts.settings import load_settings, iso_standards

    # Update FORMAT in settings before creating text field
    format_value = paper_size_key.replace('-portrait', '').replace('-landscape', '').upper()

    # Load existing settings and update with FORMAT parameter
    settings_data = load_settings()
    if 'drawing_template' not in settings_data:
        settings_data['drawing_template'] = {}
    if 'parameters' not in settings_data['drawing_template']:
        settings_data['drawing_template']['parameters'] = {}

    settings_data['drawing_template']['parameters']['FORMAT'] = format_value

    # Save settings to file
    import json
    from flask import current_app
    app_root = current_app.root_path
    userdata_path = Path(app_root, 'userdata')
    settings_file = Path(userdata_path, 'settings')

    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings_data, f, indent=2, ensure_ascii=False)

    # Create the standard text field first
    create_text_field(sheet, sheet_x, sheet_y, paper_size_key)

    # Get background view and factory for adding custom text
    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    texts = background_view.texts

    # Get text field position
    if paper_size_key == 'A4-landscape':
        text_field_x = sheet_x - 10 - 180
        text_field_y = 10
    else:
        text_field_x = sheet_x - 10 - 180
        text_field_y = 10

    # Set font properties
    fnt_size = 2.5  # 2.5mm font height

    # Override Document Type if provided
    if document_type:
        doc_text = texts.add(document_type, text_field_x + 13, text_field_y + 20)
        doc_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
        doc_props = doc_text.text_properties
        doc_props.font_size = fnt_size
        doc_props.update()

    # Override Part Number if provided
    if part_number:
        number_text = texts.add(part_number, text_field_x + 133, text_field_y + 10)
        number_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
        number_props = number_text.text_properties
        number_props.font_size = fnt_size
        number_props.update()

    # Override Title if provided (using page_name as title)
    if page_name:
        title_text = texts.add(page_name, text_field_x + 78, text_field_y + 12)
        title_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
        title_props = title_text.text_properties
        title_props.font_size = fnt_size
        title_props.update()


def get_sheets_for_drawing(drawing_name):
    """Get sheets for a specific drawing document"""
    try:
        application = get_app_object()
        if not application:
            print("DEBUG: No CATIA application")
            return []

        documents = application.documents
        target_drawing = None

        # Find the drawing by name
        for i in range(documents.count):
            doc = documents.item(i + 1)
            # Compare with display name (without extension)
            display_name = doc.name.replace('.CATDrawing', '').replace('.catdrawing', '')
            print(f"DEBUG: Checking document: {doc.name} -> display_name: {display_name}")
            if display_name == drawing_name:
                target_drawing = doc
                print(f"DEBUG: Found target drawing: {doc.name}")
                break

        if not target_drawing:
            print(f"DEBUG: Target drawing '{drawing_name}' not found")
            return []

        # Convert to DrawingDocument and get sheets
        from pycatia.drafting_interfaces.drawing_document import DrawingDocument
        drawing_doc = DrawingDocument(target_drawing.com_object)
        sheets = drawing_doc.sheets
        print(f"DEBUG: Sheets collection count: {sheets.count}")

        sheet_names = []
        for i in range(sheets.count):
            sheet = sheets.item(i + 1)
            sheet_name = sheet.name
            sheet_names.append(sheet_name)
            print(f"DEBUG: Found sheet: {sheet_name}")

        print(f"DEBUG: Returning {len(sheet_names)} sheet names: {sheet_names}")
        return sheet_names

    except Exception as e:
        print(f"Error getting sheets for {drawing_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
