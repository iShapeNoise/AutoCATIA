from pycatia.drafting_interfaces.drawing_sheet import DrawingSheet
from application.pycatia_scripts.settings import iso_standards
from .background_view import get_background_view_and_factory
from .text_properties import set_text_properties
from datetime import datetime


def add_logo_to_cell(sheet: DrawingSheet, text_field_x: float, text_field_y: float):
    """
    Add firm logo to the merged cell with proper aspect ratio and sizing
    """
    from .background_view import get_background_view_and_factory
    from application.pycatia_scripts.settings import load_settings
    from pathlib import Path
    from PIL import Image
    import os

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    pictures = background_view.pictures

    # Load settings to get logo path
    settings_data = load_settings()
    logo_filename = settings_data.get('drawing_template', {}).get('logo_filename', '')

    if not logo_filename:
        return  # No logo configured

    # Get userdata path and construct full logo path
    app_root = Path(__file__).parent.parent.parent.parent
    userdata_path = Path(app_root, 'userdata')
    logo_file = Path(userdata_path, logo_filename)

    if not logo_file.exists():
        return  # Logo file not found

    try:
        # Cell dimensions: 12mm width, 20mm height (merged rows 2-3)
        cell_width_mm = 12.0
        cell_height_mm = 20.0

        # Load image to get dimensions
        with Image.open(logo_file) as img:
            img_width, img_height = img.size

        # Calculate aspect ratio
        aspect_ratio = img_width / img_height

        # Calculate optimal size to fit within cell
        if aspect_ratio > (cell_width_mm / cell_height_mm):
            # Wider image - fit to width
            final_width = cell_width_mm
            final_height = cell_width_mm / aspect_ratio
        else:
            # Taller or square image - fit to height
            final_height = cell_height_mm
            final_width = cell_height_mm * aspect_ratio

        # Center the logo in the cell
        cell_x = text_field_x + 1  # Left edge of cell
        cell_y = text_field_y + 10  # Center of merged cell (20mm height)

        # Calculate centered position
        logo_x = cell_x + (cell_width_mm - final_width) / 2
        logo_y = cell_y + (cell_height_mm - final_height) / 2

        # Add picture to CATIA
        pictures.add(str(logo_file), logo_x, logo_y)

        # Set picture size (CATIA uses different units, may need conversion)
        # This might require additional CATIA API calls to set dimensions

    except Exception as e:
        # Fail silently if logo can't be processed
        pass


def add_text_field_values(sheet: DrawingSheet, text_field_x: float, text_field_y: float):
    """
    Add text values from settings underneath the labels in text field cells
    """
    from .background_view import get_background_view_and_factory
    from pycatia.enumeration.enumeration_types import cat_text_anchor_position
    from application.pycatia_scripts.settings import load_settings

    # Load settings to get template parameters
    settings_data = load_settings()
    template_params = settings_data.get('drawing_template', {}).get('parameters', {})

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
    texts = background_view.texts

    # Font size for values (larger than labels)
    fnt_size = 2.5

    # First row values
    first_row_y = text_field_y + 21
    # Second row values
    second_row_y = text_field_y + 12
    # Third row values
    third_row_y = text_field_y + 1

    # Scale value
    scale_value = template_params.get('SCALE', '') or " "
    scale_text = texts.add(scale_value, text_field_x + 1, first_row_y)
    scale_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(scale_text, size=fnt_size)

    # Document type value
    doc_type_value = template_params.get('DOCUMENT-TYPE', '') or " "
    doc_text = texts.add(doc_type_value, text_field_x + 13, first_row_y)
    doc_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(doc_text, size=fnt_size)

    # Material value
    material_value = template_params.get('MATERIAL', '') or " "
    material_text = texts.add(material_value, text_field_x + 65, first_row_y)
    material_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(material_text, size=fnt_size)

    # Created by value
    created_by_value = template_params.get('CREATED-BY', '') or " "
    created_text = texts.add(created_by_value, text_field_x + 35, second_row_y)
    created_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(created_text, size=fnt_size)

    # Approved by value
    approved_by_value = template_params.get('APPROVED-BY', '') or " "
    approved_text = texts.add(approved_by_value, text_field_x + 35, third_row_y)
    approved_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(approved_text, size=fnt_size)

    # Title value
    title_value = template_params.get('TITLE', '') or " "
    title_text = texts.add(title_value, text_field_x + 78, second_row_y)
    title_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(title_text, size=fnt_size)

    # Extra Title value
    extra_title_value = template_params.get('EXTRA-TITLE', '') or " "
    extra_title_text = texts.add(extra_title_value, text_field_x + 78, third_row_y)
    extra_title_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(extra_title_text, size=fnt_size)

    # Blank value
    blank_value = template_params.get('BLANK', '') or " "
    blank_text = texts.add(blank_value, text_field_x + 101, first_row_y)
    blank_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(blank_text, size=fnt_size)

    # Number value
    number_value = template_params.get('NUMBER', '') or " "
    number_text = texts.add(number_value, text_field_x + 133, second_row_y)
    number_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(number_text, size=fnt_size)

    # Revision value - always create text element
    revision_value = template_params.get('REVISION', '') or " "
    revision_text = texts.add(revision_value, text_field_x + 133, third_row_y)
    revision_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(revision_text, size=fnt_size)

    # Date value - always create text element
    date_value = datetime.now().strftime("%d/%m/%y")
    date_text = texts.add(date_value, text_field_x + 139, third_row_y)
    date_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(date_text, size=fnt_size)

    # Format value - always create text element
    format_value = template_params.get('FORMAT', '') or " "
    format_text = texts.add(format_value, text_field_x + 159, third_row_y)
    format_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(format_text, size=fnt_size)

    # Page value - always create text element
    page_value = template_params.get('PAGE', '') or " "
    page_text = texts.add(page_value, text_field_x + 168, third_row_y)
    page_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
    set_text_properties(page_text, size=fnt_size)


def add_text_field_labels(sheet: DrawingSheet, text_field_x: float, text_field_y: float, language: str = 'EN'):
    """
    Add text labels to the text field cells with multilingual support
    """
    from .background_view import get_background_view_and_factory
    from pycatia.enumeration.enumeration_types import cat_text_anchor_position, cat_text_property
    from pathlib import Path
    import os
    import json

    # Load settings data first (moved here to fix UnboundLocalError)
    from application.pycatia_scripts.settings import load_settings
    settings_data = load_settings()

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

    # Cell 5: Projection Method (100-163mm) - Add PM image if available
    projection_method = settings_data.get('drawing_template', {}).get('projection_method', 'PM_EU.jpg')
    # print(f"DEBUG: Projection method from settings: {projection_method}")

    if projection_method:
        try:
            pm_file = Path(path_prefix, 'static', 'images', projection_method)

            if pm_file.exists():
                # Position PM image in 5th cell (100-163mm width, 10mm height)
                pm_image = pictures.add(pm_file, text_field_x + 163, y_position_row1-4)
                # Set logo properties to maintain aspect ratio and fit in cell
                pm_image.ratio_lock = True
                pm_image.width = 16.0  # Max width for 12mm cell
                pm_image.height = 9.0
                print(f"DEBUG: Successfully added PM image at position ({text_field_x + 101}, {text_field_y + 10})")
            else:
                print(f"DEBUG: PM image file not found at {pm_file}")
        except Exception as e:
            print(f"DEBUG: Error adding PM image: {e}")
            pass  # Fail silently if PM image can't be loaded
    else:
        print("DEBUG: No projection method setting found")

    # Second row labels (using lower region vertical lines: 34, 77, 132)
    y_position_row2 = text_field_y + 17 - fnt_size  # Middle of upper row

    # Cell 1: Logo (merged rows 2-3, 0-12mm) - Add logo if available
    logo_filename = settings_data.get('drawing_template', {}).get('logo', '')
    # print(f"DEBUG: Logo filename from settings: {logo_filename}")

    if logo_filename:
        try:
            # Get userdata path and construct full logo path
            app_root = Path(__file__).parent.parent.parent.parent.parent
            userdata_path = Path(app_root, 'userdata')
            logo_file = Path(userdata_path, logo_filename)

            # print(f"DEBUG: App root: {app_root}")
            # print(f"DEBUG: Userdata path: {userdata_path}")
            # print(f"DEBUG: Full logo path: {logo_file}")
            # print(f"DEBUG: File exists: {logo_file.exists()}")

            if logo_file.exists():
                # Position logo in merged cell (0-12mm width, 20mm height)
                # print(f"DEBUG: Adding logo to CATIA at position ({text_field_x + 1}, {text_field_y + 10})")
                logo_picture = pictures.add(logo_file, text_field_x + 1, text_field_y + 1)

                # Set logo properties to maintain aspect ratio and fit in cell
                logo_picture.ratio_lock = True
                logo_picture.width = 31.0  # Max width for 12mm cell
                logo_picture.height = 17.0

                print(f"DEBUG: Logo added successfully with ratio_lock=True and width=10.0")
            else:
                print(f"DEBUG: Logo file not found at {logo_file}")
        except Exception as e:
            print(f"DEBUG: Error loading logo: {e}")
            pass  # Fail silently if logo can't be loaded
    else:
        print("DEBUG: No logo filename found in settings")

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

    # Add text values from settings
    add_text_field_values(sheet, text_field_x, text_field_y)
