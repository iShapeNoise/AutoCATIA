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
    Create trimming marks at each corner according to ISO_5457 standards.

    Pattern: l1=10mm, l2=5mm, l3=5mm, l4=5mm, l5=5mm, l6=10mm (connecting to l1)
    """
    background_view, factory_2d, _ = get_background_view_and_factory(sheet)
    selection = sheet.application.active_document.selection

    # Get sheet dimensions from ISO_216 (already loaded in settings)
    from application.pycatia_scripts.settings import iso_standards
    sheet_dimensions = iso_standards['sheet_sizes'][paper_size_key][0]
    sheet_x, sheet_y = sheet_dimensions

    # Get trimming mark dimensions from ISO_5457
    if paper_size_key not in iso_5457:
        return  # Skip if format not in ISO_5457

    trimming_marks = iso_5457[paper_size_key]['trimming_marks_mm']
    l1, l2 = trimming_marks  # l1=10mm, l2=5mm

    # Create trimming marks at each corner
    corners = [
        (0, 0),  # Bottom-left
        (sheet_x, 0),  # Bottom-right
        (sheet_x, sheet_y),  # Top-right
        (0, sheet_y)  # Top-left
    ]

    all_lines = []

    for corner_x, corner_y in corners:
        # Create L-shaped trimming mark pattern
        if corner_x == 0 and corner_y == 0:  # Bottom-left
            # Horizontal line (l1)
            line1 = factory_2d.create_line(corner_x, corner_y, corner_x + l1, corner_y)
            # Vertical line (l1)
            line2 = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y + l1)
            # Inner lines (l2 segments)
            line3 = factory_2d.create_line(corner_x + l1, corner_y, corner_x + l1 + l2, corner_y)
            line4 = factory_2d.create_line(corner_x, corner_y + l1, corner_x, corner_y + l1 + l2)

        elif corner_x == sheet_x and corner_y == 0:  # Bottom-right
            # Horizontal line (l1) going left
            line1 = factory_2d.create_line(corner_x, corner_y, corner_x - l1, corner_y)
            # Vertical line (l1)
            line2 = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y + l1)
            # Inner lines
            line3 = factory_2d.create_line(corner_x - l1, corner_y, corner_x - l1 - l2, corner_y)
            line4 = factory_2d.create_line(corner_x, corner_y + l1, corner_x, corner_y + l1 + l2)

        elif corner_x == sheet_x and corner_y == sheet_y:  # Top-right
            # Horizontal line (l1) going left
            line1 = factory_2d.create_line(corner_x, corner_y, corner_x - l1, corner_y)
            # Vertical line (l1) going down
            line2 = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y - l1)
            # Inner lines
            line3 = factory_2d.create_line(corner_x - l1, corner_y, corner_x - l1 - l2, corner_y)
            line4 = factory_2d.create_line(corner_x, corner_y - l1, corner_x, corner_y - l1 - l2)

        else:  # Top-left
            # Horizontal line (l1)
            line1 = factory_2d.create_line(corner_x, corner_y, corner_x + l1, corner_y)
            # Vertical line (l1) going down
            line2 = factory_2d.create_line(corner_x, corner_y, corner_x, corner_y - l1)
            # Inner lines
            line3 = factory_2d.create_line(corner_x + l1, corner_y, corner_x + l1 + l2, corner_y)
            line4 = factory_2d.create_line(corner_x, corner_y - l1, corner_x, corner_y - l1 - l2)

        all_lines.extend([line1, line2, line3, line4])

    # Apply line properties using existing utility
    update_line_properties(all_lines, selection, line_width=0)


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

    # Call other functions
    create_drawing_grid(sheet, sheet_x, sheet_y, paper_size_key)
    create_text_field(sheet, sheet_x, sheet_y, paper_size_key)


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
