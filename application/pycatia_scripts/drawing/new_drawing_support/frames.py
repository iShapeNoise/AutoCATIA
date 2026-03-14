from pathlib import Path

from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from pycatia.in_interfaces.selection import Selection
from pycatia.sketcher_interfaces.line_2D import Line2D

from application.pycatia_scripts.settings import iso_5457
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
