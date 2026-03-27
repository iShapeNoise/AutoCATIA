from pathlib import Path
from pycatia import catia
from pycatia.drafting_interfaces.drawing_document import DrawingDocument
from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from pycatia.enumeration.enumeration_types import cat_paper_size

from application.pycatia_scripts.common import get_output
from application.support.documents import get_drawing_document
from application.pycatia_scripts.settings import iso_standards
from application.pycatia_scripts.com_objects import get_app_object

# Import support functions
from .new_drawing_support.frames import create_frame_lines
from .new_drawing_support.text_field import create_text_field


def check_open_drawings():
    """Check for open drawing documents and return their names"""
    try:
        application = get_app_object()
        if not application:
            return []

        documents = application.documents
        drawing_names = []

        for i in range(documents.count):
            doc = documents.item(i + 1)
            if doc.name.endswith('.CATDrawing'):
                drawing_names.append(doc.name)

        return drawing_names
    except:
        return []


def add_page_to_drawing(paper_size_key, title):
    """Add a new page to an existing CATIA drawing"""
    try:
        # Get the active drawing document
        pt_drawing_document, errors = get_drawing_document()
        if errors:
            return {'success': False, 'errors': errors}

        drawing_document = pt_drawing_document.drawing_document
        drawing = drawing_document.drawing_root

        # Create new sheet
        sheets = drawing.sheets
        new_sheet = sheets.add(title)

        # Set paper size
        paper_size_mapping = {
            'A0': 2,      # catPaperA0
            'A1': 3,      # catPaperA1
            'A2': 4,      # catPaperA2
            'A3': 5,      # catPaperA3
            'A4-portrait': 6,  # catPaperA4
            'A4-landscape': 6   # catPaperA4Landscape
        }

        catia_paper_size = paper_size_mapping.get(paper_size_key, 3)  # Default to A3
        new_sheet.paper_size = catia_paper_size

        # Explicitly set orientation for all formats
        if paper_size_key == 'A4-portrait':
            new_sheet.orientation = 0  # Portrait
        elif paper_size_key in ['A3', 'A2', 'A1', 'A4-landscape']:
            new_sheet.orientation = 1  # Landscape
        elif paper_size_key == 'A0':
            new_sheet.orientation = 1  # Landscape

        new_sheet.force_update()

        # Get sheet dimensions and create elements
        sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
        sheet_x, sheet_y = sheet_dimensions

        # Create frame lines
        create_frame_lines(new_sheet, paper_size_key)

        # Create text field
        create_text_field(new_sheet, sheet_x, sheet_y, paper_size_key)

        return {"success": True, "message": f"Added {paper_size_key} page with title: {title}"}

    except Exception as e:
        return {'success': False, 'errors': [f"Failed to add page: {str(e)}"]}


def add_page_with_title(paper_size_key, title):
    """
    Wrapper function with error handling for adding a new page to existing drawing
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
        result = add_page_to_drawing(paper_size_key, title)
        return result

    except Exception as e:
        return {
            'success': False,
            'errors': [f"Error adding new page: {str(e)}"]
        }
