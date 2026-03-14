from pathlib import Path
from pycatia import catia
from pycatia.drafting_interfaces.drawing_document import DrawingDocument
from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from pycatia.drafting_interfaces.drawing_texts import DrawingTexts
from pycatia.enumeration.enumeration_types import cat_paper_size
from pycatia.enumeration.enumeration_types import cat_text_anchor_position

from application.pycatia_scripts.common import get_output
from application.support.documents import get_drawing_document
from application.pycatia_scripts.settings import drawing_template
from application.pycatia_scripts.settings import path_prefix

# Import all the support functions
from .new_drawing_support.background_view import get_background_view_and_factory
from .new_drawing_support.border import create_border
from .new_drawing_support.copyright_box import create_copyright_box
from .new_drawing_support.title_block import create_title_block, add_title_block_text, add_param_text
from .new_drawing_support.template_name import create_template_name
from .new_drawing_support.parameters import create_parameters
from .new_drawing_support.purge import purge_background_view
from .new_drawing_support.paper_size import get_sheet_size_info

# Export drawing_template for support files that need it
__all__ = ['drawing_template', 'path_prefix', 'insert_drawing_template', 'create_new_drawing_with_title']

def insert_drawing_template(form_parameters):
    """Legacy function for backward compatibility"""
    pt_drawing_document, errors = get_drawing_document()
    output = get_output()

    output['errors'] = output['errors'] + errors

    if output['errors']:
        return output

    drawing: DrawingDocument = pt_drawing_document.drawing_document
    application = drawing.application

    application.refresh_display = False
    sheets = drawing.sheets
    parameters = create_parameters(drawing, form_parameters)
    sheet_number = 1

    for sheet in sheets:
        size_info = get_sheet_size_info(sheet)
        purge_background_view(drawing, sheet)
        create_border(sheet, size_info)
        create_copyright_box(sheet, parameters)
        create_title_block(sheet, size_info, parameters, sheet_number)
        create_template_name(sheet, size_info)
        sheet.force_update()
        sheet_number += 1

    for sheet in sheets:
        sheet.activate()
        main_view = sheet.views.get_item_by_name('Main View')
        main_view.activate()
        viewer = application.active_window
        viewer.active_viewer.reframe()
    sheets[0].activate()

    output['data'] = 'Drawing template inserted.'
    application.refresh_display = True

    return output

def create_new_drawing_with_title(paper_size_key, title):
    """
    Create a new CATIA drawing with specified paper size and title
    """
    from pycatia.enumeration.enumeration_types import cat_paper_size
    from application.pycatia_scripts.settings import drawing_template

    # Map size keys to CATIA enum values
    size_mapping = {
        'A4-portrait': 4,    # catPaperA4
        'A4-landscape': 5,   # catPaperA4Landscape
        'A3': 3,             # catPaperA3
        'A2': 2,             # catPaperA2
        'A1': 1              # catPaperA1
    }

    # Create new drawing
    documents = catia.documents
    new_drawing = documents.add('Drawing')
    sheets = new_drawing.sheets
    sheet = sheets.item(1)

    # Set paper size
    sheet.paper_size = size_mapping[paper_size_key]
    sheet.name = title

    # Get sheet size info
    from application.pycatia_scripts.drawing.new_drawing_support.paper_size import get_sheet_size_info
    size_info = get_sheet_size_info(sheet)

    # Create parameters
    from application.pycatia_scripts.drawing.new_drawing_support.parameters import create_parameters
    parameters = create_parameters(new_drawing, {})

    # Create template elements - PASS CONFIGURATION AS PARAMETER
    from application.pycatia_scripts.drawing.new_drawing_support.border import create_border
    create_border(sheet, size_info, drawing_template)

    from application.pycatia_scripts.drawing.new_drawing_support.title_block import create_title_block
    create_title_block(sheet, size_info, parameters, 1, drawing_template)

    return {"success": True, "message": f"Created {paper_size_key} drawing: {title}"}
