from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from application.pycatia_scripts.settings import iso_standards
from .background_view import get_background_view_and_factory
from .text_properties import set_text_properties


def add_text_field_labels(sheet: DrawingSheet, text_field_x: float, text_field_y: float, language: str = 'EN'):
    """
    Add text labels to the text field cells with multilingual support
    """
    from .background_view import get_background_view_and_factory
    from pycatia.enumeration.enumeration_types import cat_text_anchor_position, cat_text_property
    from pathlib import Path
    import os
    import json

    # Load language files from static/lang/
    path_prefix = Path(os.path.dirname(__file__)).parent.parent.parent
    lang_file = Path(path_prefix, 'static', 'lang', f'{language.lower()}')  # No extension

    # Load translations using JSON
    with open(lang_file, 'r', encoding='utf-8') as f:
        translations = json.load(f)

    # Load settings for logo
    from application.pycatia_scripts.settings import drawing_template
    logo_path = drawing_template.get('logo', '')

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    texts = background_view.texts
    pictures = background_view.pictures

    # Font settings
    fnt_size = 2.5
    anchor_position = cat_text_anchor_position.index('catBottomLeft')

    # First row labels (using upper region vertical lines: 12, 64, 100, 163)
    y_position_row1 = text_field_y + 27 - fnt_size

    # Cell 1: Scale (0-12mm)
    scale_text = texts.add(translations.get('labels', {}).get('scale', 'Scale'), text_field_x + 1, y_position_row1)
    scale_text.anchor_position = anchor_position
    scale_props = scale_text.text_properties
    scale_props.superscript = 1
    scale_props.font_size = fnt_size
    scale_props.update()

    # Cell 2: Document Type (12-64mm)
    doc_type_text = texts.add(translations.get('labels', {}).get('document_type', 'Document Type'), text_field_x + 13, y_position_row1)
    doc_type_text.anchor_position = anchor_position
    doc_type_props = doc_type_text.text_properties
    doc_type_props.superscript = 1
    doc_type_props.font_size = fnt_size
    doc_type_props.update()

    # Cell 3: Material (64-100mm)
    material_text = texts.add(translations.get('labels', {}).get('material', 'Material'), text_field_x + 65, y_position_row1)
    material_text.anchor_position = anchor_position
    material_props = material_text.text_properties
    material_props.superscript = 1
    material_props.font_size = fnt_size
    material_props.update()

    # Cell 4: Blank (100-163mm)
    blank_text = texts.add(translations.get('labels', {}).get('blank', 'Blank'), text_field_x + 101, y_position_row1)
    blank_text.anchor_position = anchor_position
    blank_props = blank_text.text_properties
    blank_props.superscript = 1
    blank_props.font_size = fnt_size
    blank_props.update()

    # Second row labels (using lower region vertical lines: 34, 77, 132)
    y_position_row2 = text_field_y + 17 - fnt_size  # Middle of upper row

    # Cell 1: Logo (merged rows 2-3, 0-12mm) - Add logo if available
    if logo_path:
        try:
            logo_file = Path(path_prefix, 'application', 'static', 'images', logo_path)
            if logo_file.exists():
                # Position logo in merged cell (0-12mm width, 20mm height)
                pictures.add(str(logo_file), text_field_x + 1, text_field_y + 10)
        except:
            pass  # Fail silently if logo can't be loaded

    # Cell 2: Created by (12-34mm in upper part)
    created_by_text = texts.add(translations.get('labels', {}).get('created_by', 'Created by'), text_field_x + 35, y_position_row2)
    created_by_text.anchor_position = anchor_position
    created_by_props = created_by_text.text_properties
    created_by_props.superscript = 1
    created_by_props.font_size = fnt_size
    created_by_props.update()

    # Cell 3: Title, Extra title (merged rows 2-3, 77-132mm)
    title_text = texts.add(translations.get('labels', {}).get('title_extra', 'Title, Extra title'), text_field_x + 78, y_position_row2)
    title_text.anchor_position = anchor_position
    title_props = title_text.text_properties
    title_props.superscript = 1
    title_props.font_size = fnt_size
    title_props.update()

    # Cell 4: Number (132-180mm, but split by horizontal lines)
    number_text = texts.add(translations.get('labels', {}).get('number', 'Number'), text_field_x + 133, y_position_row2)
    number_text.anchor_position = anchor_position
    number_props = number_text.text_properties
    number_props.superscript = 1
    number_props.font_size = fnt_size
    number_props.update()

    # Third row labels (lower row)
    y_position_row3 = text_field_y + 7 - fnt_size  # Middle of lower row

    # Cell 2: Approved by (34-77mm) - MOVED TO THE RIGHT
    approved_by_text = texts.add(translations.get('labels', {}).get('approved_by', 'Approved by'), text_field_x + 35, y_position_row3)
    approved_by_text.anchor_position = anchor_position
    approved_by_props = approved_by_text.text_properties
    approved_by_props.superscript = 1
    approved_by_props.font_size = fnt_size
    approved_by_props.update()

    # Cell 4: Multiple labels in lower cells (using final vertical positions: 138, 158, 167)
    # Rev. (132-138mm)
    rev_text = texts.add(translations.get('labels', {}).get('revision', 'Rev.'), text_field_x + 133, y_position_row3)
    rev_text.anchor_position = anchor_position
    rev_props = rev_text.text_properties
    rev_props.superscript = 1
    rev_props.font_size = fnt_size
    rev_props.update()

    # Release date (138-158mm)
    release_date_text = texts.add(translations.get('labels', {}).get('release_date', 'Release date'), text_field_x + 139, y_position_row3)
    release_date_text.anchor_position = anchor_position
    release_date_props = release_date_text.text_properties
    release_date_props.superscript = 1
    release_date_props.font_size = fnt_size
    release_date_props.update()

    # Format (158-167mm)
    format_text = texts.add(translations.get('labels', {}).get('format', 'Format'), text_field_x + 159, y_position_row3)
    format_text.anchor_position = anchor_position
    format_props = format_text.text_properties
    format_props.superscript = 1
    format_props.font_size = fnt_size
    format_props.update()

    # Page (167-180mm)
    page_text = texts.add(translations.get('labels', {}).get('page', 'Page'), text_field_x + 168, y_position_row3)
    page_text.anchor_position = anchor_position
    page_props = page_text.text_properties
    page_props.superscript = 1
    page_props.font_size = fnt_size
    page_props.update()

def create_text_field(sheet: DrawingSheet, sheet_x: float, sheet_y: float, paper_size_key: str):
    """
    Create text field outer box (180mm width x 30mm height) with 0.7mm lines
    positioned at lower right corner of inner frame, plus internal lines
    """
    from .background_view import get_background_view_and_factory

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    selection = sheet.application.active_document.selection

    # Get sheet dimensions from ISO_216
    sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
    sheet_x, sheet_y = sheet_dimensions

    # Calculate text field position based on inner frame coordinates
    if paper_size_key == 'A4-landscape':
        # A4 landscape special case: inner frame at 10mm/20mm offsets
        text_field_x = sheet_x - 10 - 180  # 10mm from right edge
        text_field_y = 10  # 10mm from bottom
    else:
        # Standard formats: inner frame at 20mm/10mm offsets
        text_field_x = sheet_x - 10 - 180  # 20mm from right edge
        text_field_y = 10  # 10mm from bottom

    text_field_width = 180
    text_field_height = 30

    # Create outer box lines
    lines = []

    # Bottom line
    line_bottom = factory_2d.create_line(text_field_x, text_field_y,
                                        text_field_x + text_field_width, text_field_y)
    # Right line
    line_right = factory_2d.create_line(text_field_x + text_field_width, text_field_y,
                                       text_field_x + text_field_width, text_field_y + text_field_height)
    # Top line
    line_top = factory_2d.create_line(text_field_x + text_field_width, text_field_y + text_field_height,
                                     text_field_x, text_field_y + text_field_height)
    # Left line
    line_left = factory_2d.create_line(text_field_x, text_field_y + text_field_height,
                                      text_field_x, text_field_y)

    lines.extend([line_bottom, line_right, line_top, line_left])

    # Add horizontal line 10mm from top (existing)
    h_line_10mm = factory_2d.create_line(text_field_x, text_field_y + text_field_height - 10,
                                        text_field_x + text_field_width, text_field_y + text_field_height - 10)
    lines.append(h_line_10mm)

    # Add 4 vertical lines in upper region (existing)
    vertical_positions = [12, 64, 100, 163]
    for x_pos in vertical_positions:
        v_line = factory_2d.create_line(text_field_x + x_pos, text_field_y + text_field_height - 10,
                                       text_field_x + x_pos, text_field_y + text_field_height)
        lines.append(v_line)

    # Add 3 vertical lines underneath (existing)
    vertical_positions_under = [34, 77, 132]
    for x_pos in vertical_positions_under:
        v_line = factory_2d.create_line(text_field_x + x_pos, text_field_y,
                                       text_field_x + x_pos, text_field_y + 20)
        lines.append(v_line)

    # Add 2 horizontal lines 20mm from top (existing)
    # First line: between 34mm and 77mm
    h_line_20mm_1 = factory_2d.create_line(text_field_x + 34, text_field_y + 10,
                                          text_field_x + 77, text_field_y + 10)
    lines.append(h_line_20mm_1)

    # Second line: between 132mm and 180mm
    h_line_20mm_2 = factory_2d.create_line(text_field_x + 132, text_field_y + 10,
                                          text_field_x + 180, text_field_y + 10)
    lines.append(h_line_20mm_2)

    # Add 3 vertical lines in lower part between x=132 and x=180 (NEW)
    final_vertical_positions = [138, 158, 167]
    for x_pos in final_vertical_positions:
        v_line = factory_2d.create_line(text_field_x + x_pos, text_field_y,
                                       text_field_x + x_pos, text_field_y + 10)
        lines.append(v_line)

    # Apply 0.7mm thickness to all lines
    selection.clear()
    for line in lines:
        selection.add(line)
    vp = selection.vis_properties
    vp.set_real_width(3, 0)  # 0.7mm thickness

    # Add text labels
    add_text_field_labels(sheet, text_field_x, text_field_y)
