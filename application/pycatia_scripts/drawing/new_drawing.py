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
__all__ = ['drawing_template', 'p#insert_drawing_template', 'create_new_drawing_with_info']

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


def create_new_drawing_with_info(paper_size_key, page_name, document_type, part_number):
    """
    Create a new CATIA drawing with custom information from modal
    """
    from pycatia.enumeration.enumeration_types import cat_paper_size
    from application.pycatia_scripts.com_objects import get_app_object
    from application.pycatia_scripts.settings import iso_standards
    from application.pycatia_scripts.common import get_output
    from application.pycatia_scripts.drawing.new_drawing_support.frames import create_frame_lines

    # Get CATIA application
    application = get_app_object()

    if not application:
        output = get_output()
        output['errors'].append('CATIA application is not running')
        return output

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
            sheet.orientation = 0  # 0 = catPaperPortrait
            sheet.force_update()
        except:
            pass

    # Set sheet name using page_name from modal
    sheet.name = page_name or f"{paper_size_key} Drawing"
    sheet.force_update()

    # Get sheet dimensions from ISO_216
    sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
    sheet_x, sheet_y = sheet_dimensions

    # Create frame lines
    create_frame_lines(sheet, paper_size_key)

    # Create text field with custom information
    create_text_field_with_info(sheet, sheet_x, sheet_y, paper_size_key, page_name, document_type, part_number)

    return {"success": True, "message": f"Created {paper_size_key} drawing with custom information"}


def create_text_field_with_info(sheet: DrawingSheet, sheet_x: float, sheet_y: float, paper_size_key: str, page_name: str, document_type: str, part_number: str):
    """
    Create text field with custom information from modal
    """
    from .new_drawing_support.text_field import create_text_field, add_text_field_values
    from .new_drawing_support.background_view import get_background_view_and_factory
    from pycatia.enumeration.enumeration_types import cat_text_anchor_position
    from application.pycatia_scripts.settings import load_settings, iso_standards

    # First create the standard text field with labels and default values
    create_text_field(sheet, sheet_x, sheet_y, paper_size_key)

    # Get background view for adding custom text
    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    texts = background_view.texts

    # Get text field position (same as used in create_text_field)
    sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
    sheet_x, sheet_y = sheet_dimensions

    # Calculate text field position
    if paper_size_key == 'A4-landscape':
        text_field_x = sheet_x - 10 - 180
        text_field_y = 10
    else:
        text_field_x = sheet_x - 10 - 180
        text_field_y = 10

    # Font settings
    fnt_size = 2.5

    # Override Document Type if provided
    if document_type:
        # Position matches add_text_field_values: text_field_x + 13, first_row_y
        doc_text = texts.add(document_type, text_field_x + 13, text_field_y + 21)
        doc_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
        from .new_drawing_support.text_properties import set_text_properties
        set_text_properties(doc_text, size=fnt_size)

    # Override Part Number if provided
    if part_number:
        # Position matches add_text_field_values: text_field_x + 133, second_row_y
        number_text = texts.add(part_number, text_field_x + 133, text_field_y + 12)
        number_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
        from .new_drawing_support.text_properties import set_text_properties
        set_text_properties(number_text, size=fnt_size)

    # Override Title if provided (using page_name as title)
    if page_name:
        # Position matches add_text_field_values: text_field_x + 78, second_row_y
        title_text = texts.add(page_name, text_field_x + 78, text_field_y + 12)
        title_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
        from .new_drawing_support.text_properties import set_text_properties
        set_text_properties(title_text, size=fnt_size)
