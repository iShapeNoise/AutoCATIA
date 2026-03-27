from pathlib import Path

from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from pycatia.in_interfaces.selection import Selection
from pycatia.sketcher_interfaces.line_2D import Line2D

from application.pycatia_scripts.settings import iso_5457
from application.pycatia_scripts.settings import iso_standards
from .background_view import get_background_view_and_factory
from .lines import update_line_properties


def create_trimming_marks(sheet: DrawingSheet, paper_size_key: str):
    """
    Create trimming marks: 6 lines at each corner.
    - 2 lines: 10mm from corner (0,0 offset)
    - 2 lines: 5mm parallel to long lines with 10mm offset
    - 2 lines: 5mm completing rectangle pattern at specific positions
    One horizontal and one vertical for each set.
    """
    from .background_view import get_background_view_and_factory
    from application.pycatia_scripts.settings import iso_standards

    background_view, factory_2d, _ = get_background_view_and_factory(sheet)
    selection = sheet.application.active_document.selection

    # Get sheet dimensions from ISO_216 (page size)
    sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
    sheet_x, sheet_y = sheet_dimensions

    # Line lengths
    long_line_length = 10.0
    short_line_length = 5.0
    offset = 10.0  # 10mm offset for short lines

    all_lines = []

    # Define corners and create lines
    corners = [
        (0, 0),  # Bottom-left
        (sheet_x, 0),  # Bottom-right
        (sheet_x, sheet_y),  # Top-right
        (0, sheet_y)  # Top-left
    ]

    for corner_x, corner_y in corners:
        if corner_x == 0 and corner_y == 0:  # Bottom-left
            # Long lines (10mm from corner) - keep as is
            long_h = factory_2d.create_line(corner_x, corner_y, corner_x + long_line_length, corner_y)
            long_v = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y + long_line_length)

            # Short parallel lines (10mm offset from corner) - keep as is
            short_h = factory_2d.create_line(corner_x, corner_y + offset, corner_x + short_line_length, corner_y + offset)
            short_v = factory_2d.create_line(corner_x + offset, corner_y, corner_x + offset, corner_y + short_line_length)

            # Rectangle completing lines - position at (5, 5)
            start_x = 5.0
            start_y = 5.0
            rect_h = factory_2d.create_line(start_x, start_y, start_x + short_line_length, start_y)
            rect_v = factory_2d.create_line(start_x, start_y, start_x, start_y + short_line_length)

        elif corner_x == sheet_x and corner_y == 0:  # Bottom-right
            # Long lines (10mm from corner) - keep as is
            long_h = factory_2d.create_line(corner_x, corner_y, corner_x - long_line_length, corner_y)
            long_v = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y + long_line_length)

            # Short parallel lines (10mm offset from corner) - keep as is
            short_h = factory_2d.create_line(corner_x, corner_y + offset, corner_x - short_line_length, corner_y + offset)
            short_v = factory_2d.create_line(corner_x - offset, corner_y, corner_x - offset, corner_y + short_line_length)

            # Rectangle completing lines - position at (sheet_x - 5, 5)
            start_x = sheet_x - 5.0
            start_y = 5.0
            rect_h = factory_2d.create_line(start_x, start_y, start_x - short_line_length, start_y)
            rect_v = factory_2d.create_line(start_x, start_y, start_x, start_y + short_line_length)

        elif corner_x == sheet_x and corner_y == sheet_y:  # Top-right
            # Long lines (10mm from corner) - keep as is
            long_h = factory_2d.create_line(corner_x, corner_y, corner_x - long_line_length, corner_y)
            long_v = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y - long_line_length)

            # Short parallel lines (10mm offset from corner) - keep as is
            short_h = factory_2d.create_line(corner_x, corner_y - offset, corner_x - short_line_length, corner_y - offset)
            short_v = factory_2d.create_line(corner_x - offset, corner_y, corner_x - offset, corner_y - short_line_length)

            # Rectangle completing lines - position at (sheet_x - 5, sheet_y - 5)
            start_x = sheet_x - 5.0
            start_y = sheet_y - 5.0
            rect_h = factory_2d.create_line(start_x, start_y, start_x - short_line_length, start_y)
            rect_v = factory_2d.create_line(start_x, start_y, start_x, start_y - short_line_length)

        else:  # Top-left
            # Long lines (10mm from corner) - keep as is
            long_h = factory_2d.create_line(corner_x, corner_y, corner_x + long_line_length, corner_y)
            long_v = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y - long_line_length)

            # Short parallel lines (10mm offset from corner) - keep as is
            short_h = factory_2d.create_line(corner_x, corner_y - offset, corner_x + short_line_length, corner_y - offset)
            short_v = factory_2d.create_line(corner_x + offset, corner_y, corner_x + offset, corner_y - short_line_length)

            # Rectangle completing lines - position at (5, 292)
            start_x = 5.0
            start_y = sheet_y - 5.0
            rect_h = factory_2d.create_line(start_x, start_y, start_x + short_line_length, start_y)
            rect_v = factory_2d.create_line(start_x, start_y, start_x, start_y - short_line_length)

        all_lines.extend([long_h, long_v, short_h, short_v, rect_h, rect_v])

    # Apply inner frame line thickness (0.7mm = value 3)
    selection.clear()
    for line in all_lines:
        selection.add(line)
    vp = selection.vis_properties
    vp.set_real_width(1, 0)  # 0.7mm thickness (same as inner frame) [1](#26-0)


def create_frame_lines(sheet: DrawingSheet, paper_size_key: str):
    """
    Create 4 border lines with 0.7mm thickness and marker lines
    """
    from .background_view import get_background_view_and_factory

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    selection = sheet.application.active_document.selection

    # Get sheet dimensions from ISO_216
    sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
    sheet_x, sheet_y = sheet_dimensions

    # Create outer frame (0.35mm thickness = value 2)
    if paper_size_key == 'A4-landscape':
        # A4 landscape special coordinates: 5mm left/right, 15mm top, 5mm bottom
        outer_x1 = 5
        outer_x2 = sheet_x - 5
        outer_y1 = sheet_y - 15  # top
        outer_y2 = 5             # bottom

        # Inner frame: 10mm left/right, 20mm top, 10mm bottom
        inner_x1 = 10
        inner_x2 = sheet_x - 10
        inner_y1 = sheet_y - 20  # top
        inner_y2 = 10            # bottom
    else:
        # Standard coordinates: 15mm left, 5mm right/top/bottom
        outer_x1 = 15
        outer_x2 = sheet_x - 5
        outer_y1 = sheet_y - 5   # top
        outer_y2 = 5             # bottom

        # Inner frame: 20mm left, 10mm right/top/bottom
        inner_x1 = 20
        inner_x2 = sheet_x - 10
        inner_y1 = sheet_y - 10  # top
        inner_y2 = 10            # bottom

    # Create outer frame lines
    lines = []
    line_outer_bottom = factory_2d.create_line(outer_x1, outer_y2, outer_x2, outer_y2)
    line_outer_right = factory_2d.create_line(outer_x2, outer_y2, outer_x2, outer_y1)
    line_outer_top = factory_2d.create_line(outer_x2, outer_y1, outer_x1, outer_y1)
    line_outer_left = factory_2d.create_line(outer_x1, outer_y1, outer_x1, outer_y2)
    lines.extend([line_outer_bottom, line_outer_right, line_outer_top, line_outer_left])

    # Set outer frame properties (0.35mm thickness)
    selection.clear()
    for line in lines:
        selection.add(line)
    vp = selection.vis_properties
    vp.set_real_width(2, 0)  # 0.35mm thickness

    # Create inner frame lines (0.7mm thickness = value 3)
    lines = []
    line_inner_bottom = factory_2d.create_line(inner_x1, inner_y2, inner_x2, inner_y2)
    line_inner_right = factory_2d.create_line(inner_x2, inner_y2, inner_x2, inner_y1)
    line_inner_top = factory_2d.create_line(inner_x2, inner_y1, inner_x1, inner_y1)
    line_inner_left = factory_2d.create_line(inner_x1, inner_y1, inner_x1, inner_y2)
    lines.extend([line_inner_bottom, line_inner_right, line_inner_top, line_inner_left])

    # Set inner frame properties (0.7mm thickness)
    selection.clear()
    for line in lines:
        selection.add(line)
    vp = selection.vis_properties
    vp.set_real_width(3, 0)  # 0.7mm thickness

    # Create marker lines
    lines = []

    if paper_size_key == 'A4-landscape':
        # A4 landscape: horizontal line at y=0, x=width/2
        marker_line = factory_2d.create_line(sheet_x/2, sheet_y, sheet_x/2, sheet_y - 10)
        lines.append(marker_line)
    elif paper_size_key in ['A2', 'A1']:
        # A2 and A1: lower marker line at A4/2 from bottom (148.5mm)
        lower_marker = factory_2d.create_line(0, 148.5, 10, 148.5)
        lines.append(lower_marker)

        # Upper marker line at A4 Portrait height from bottom (297mm)
        upper_marker = factory_2d.create_line(0, 297, 10, 297)
        lines.append(upper_marker)
    else:
        # All other formats: line at center of paper
        center_marker = factory_2d.create_line(0, sheet_y/2, 10, sheet_y/2)
        lines.append(center_marker)

    # Set marker line properties (0.35mm thickness)
    if lines:
        selection.clear()
        for line in lines:
            selection.add(line)
        vp = selection.vis_properties
        vp.set_real_width(2, 0)  # 0.35mm thickness

    # Create the reference grid
    create_drawing_grid(sheet, sheet_x, sheet_y, paper_size_key)

    # Add grid reference letters and numbers
    add_grid_references(sheet, sheet_x, sheet_y, paper_size_key)

    # Create trimming marks on each corner
    create_trimming_marks(sheet, paper_size_key)


def create_drawing_grid(sheet: DrawingSheet, sheet_x: float, sheet_y: float, paper_size_key: str):
    """
    Create inner frame lines with 0.7mm thickness and section lines
    connecting outer frame (0.35mm) to inner frame (0.7mm)
    """
    from .background_view import get_background_view_and_factory
    from application.pycatia_scripts.settings import iso_5457

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    selection = sheet.application.active_document.selection

    # Get grid spacing from ISO_5457
    grid_spacing = iso_5457['grid_spacing_mm'].get(paper_size_key, {'x': 50, 'y': 47.833})
    spacing_x = grid_spacing['x']
    spacing_y = grid_spacing['y']

    # Check if this is A4 landscape for different coordinates
    is_a4_landscape = paper_size_key == 'A4-landscape'

    if is_a4_landscape:
        # A4 landscape coordinates
        outer_x1 = 5
        outer_x2 = sheet_x - 5
        outer_y1 = sheet_y - 15
        outer_y2 = 5

        inner_x1 = 10
        inner_x2 = sheet_x - 10
        inner_y1 = sheet_y - 20
        inner_y2 = 10
    else:
        # Standard format coordinates
        outer_x1 = 15
        outer_x2 = sheet_x - 5
        outer_y1 = sheet_y - 5
        outer_y2 = 5

        inner_x1 = 20
        inner_x2 = sheet_x - 10
        inner_y1 = sheet_y - 10
        inner_y2 = 10

    # Create section lines connecting outer to inner frame
    lines_section = []

    # Horizontal section lines (top and bottom)
    x = outer_x1
    while x < outer_x2:
        # Top section line (going inward from outer to inner)
        line_top = factory_2d.create_line(x, outer_y1, x, inner_y1)
        # Bottom section line (going inward from outer to inner)
        line_bottom = factory_2d.create_line(x, outer_y2, x, inner_y2)
        lines_section.extend([line_top, line_bottom])
        x += spacing_x

    # Vertical section lines (left and right)
    y = outer_y2
    while y < outer_y1:
        # Left section line (going inward from outer to inner)
        line_left = factory_2d.create_line(outer_x1, y, inner_x1, y)
        # Right section line (going inward from outer to inner)
        line_right = factory_2d.create_line(outer_x2, y, inner_x2, y)
        lines_section.extend([line_left, line_right])
        y += spacing_y

    # Apply 0.35mm thickness to section lines
    selection.clear()
    for line in lines_section:
        selection.add(line)
    vp = selection.vis_properties
    vp.set_real_width(2, 0)  # 0.35mm thickness


def add_grid_references(sheet: DrawingSheet, sheet_x: float, sheet_y: float, paper_size_key: str):
    """
    Add alphanumeric grid references (letters and numbers) to the cells
    between inner and outer frame borders according to ISO 5457
    """
    from .background_view import get_background_view_and_factory
    from pycatia.enumeration.enumeration_types import cat_text_anchor_position
    from application.pycatia_scripts.settings import iso_5457

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    texts = background_view.texts

    # Get grid reference configuration
    grid_config = iso_5457[paper_size_key]['grid_reference']
    fields_x, fields_y = grid_config['fields']

    # Get the SAME grid spacing that create_drawing_grid() uses
    grid_spacing = iso_5457['grid_spacing_mm'].get(paper_size_key, {'x': 50, 'y': 47.833})
    spacing_x = grid_spacing['x']
    spacing_y = grid_spacing['y']

    # Get frame coordinates (same logic as create_drawing_grid)
    is_a4_landscape = paper_size_key == 'A4-landscape'

    if is_a4_landscape:
        outer_x1 = 5
        outer_x2 = sheet_x - 5
        outer_y1 = sheet_y - 15
        outer_y2 = 5
        inner_x1 = 10
        inner_x2 = sheet_x - 10
        inner_y1 = sheet_y - 20
        inner_y2 = 10
    else:
        outer_x1 = 15
        outer_x2 = sheet_x - 5
        outer_y1 = sheet_y - 5
        outer_y2 = 5
        inner_x1 = 20
        inner_x2 = sheet_x - 10
        inner_y1 = sheet_y - 10
        inner_y2 = 10

    # Font settings
    fnt_size = 2.5
    center_anchor = cat_text_anchor_position.index('catMiddleCenter')

    # Generate letters (excluding I, O)
    letters = []
    for i in range(fields_x):
        char_code = ord('A') + i
        if char_code >= ord('I'):
            char_code += 1  # Skip I
        if char_code >= ord('O'):
            char_code += 1  # Skip O
        letters.append(chr(char_code))

    # Add letters to top and bottom horizontal bands
    # Use the SAME positioning logic as the grid lines
    x = outer_x1
    for i, letter in enumerate(letters):
        if x >= outer_x2:
            break

        # Position at center of each grid cell
        x_pos = x + (spacing_x / 2)

        # Top band
        y_top = (outer_y1 + inner_y1) / 2
        text_top = texts.add(letter, x_pos, y_top)
        text_top.anchor_position = center_anchor
        text_top.text_properties.font_size = fnt_size
        text_top.text_properties.update()

        # Bottom band
        y_bottom = (outer_y2 + inner_y2) / 2
        text_bottom = texts.add(letter, x_pos, y_bottom)
        text_bottom.anchor_position = center_anchor
        text_bottom.text_properties.font_size = fnt_size
        text_bottom.text_properties.update()

        x += spacing_x

    # Add numbers to left and right vertical bands
    # Start from TOP and align with actual grid cells
    y = outer_y1 - (spacing_y / 2)  # Start at center of first cell
    for i in range(1, fields_y + 1):
        if y < outer_y2 + (spacing_y / 2):
            break

        # Left band
        x_left = (outer_x1 + inner_x1) / 2
        text_left = texts.add(str(i), x_left, y)
        text_left.anchor_position = center_anchor
        text_left.text_properties.font_size = fnt_size
        text_left.text_properties.update()

        # Right band
        x_right = (outer_x2 + inner_x2) / 2
        text_right = texts.add(str(i), x_right, y)
        text_right.anchor_position = center_anchor
        text_right.text_properties.font_size = fnt_size
        text_right.text_properties.update()

        y -= spacing_y  # Move to next cell center
