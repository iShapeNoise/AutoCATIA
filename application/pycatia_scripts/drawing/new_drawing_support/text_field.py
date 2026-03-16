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

    # Load language files from static/lang/
    path_prefix = Path(os.path.dirname(__file__)).parent.parent.parent
    lang_file = Path(path_prefix, 'static', 'lang', f'{language.lower()}.yaml')

    # Load translations using existing read_yaml function
    from application.pycatia_scripts.settings import read_yaml
    translations = read_yaml(lang_file)

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    texts = background_view.texts

    # Add "Scale" label in top row left cell
    # Position: 1mm from left, 1mm from top of cell
    # Text field is 180mm wide x 30mm high, first horizontal line is at y=20mm
    fnt_size = 2.5
    scale_text = texts.add("Scale", text_field_x + 1, text_field_y + 27 - fnt_size)
    anchor_position = cat_text_anchor_position.index('catBottomLeft')
    scale_text.anchor_position = anchor_position

    text_props = scale_text.text_properties
    text_props.superscript = 1
    text_props.font_size = fnt_size
    text_props.update()


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
