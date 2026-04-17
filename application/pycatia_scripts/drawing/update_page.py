def update_page_scale(sheet_name, drawing_name=None):
    """Update scale text field based on the main view scale of the selected sheet"""
    from application.pycatia_scripts.com_objects import get_app_object

    try:
        application = get_app_object()
        if not application:
            raise Exception("CATIA application not found")

        documents = application.documents
        target_drawing = None

        # Step 1: Find the Document
        if drawing_name:
            # Search for the specific drawing document
            for i in range(documents.count):
                doc = documents.item(i + 1)
                if doc.name == drawing_name:
                    target_drawing = doc
                    break
        else:
            # Use active document if no specific drawing specified
            target_drawing = application.active_document

        if not target_drawing:
            raise Exception(f"Drawing document '{drawing_name}' not found")

        # Convert to DrawingDocument interface
        drawing_document = target_drawing.com_object
        from pycatia.drafting_interfaces.drawing_document import DrawingDocument
        drawing_doc = DrawingDocument(drawing_document)

        # Step 2: Find the Sheet
        sheet = drawing_doc.sheets.get_item_by_name(sheet_name)
        if not sheet:
            raise Exception(f"Sheet '{sheet_name}' not found in drawing")

        # Step 3: Find the Main View
        main_view = None
        views = sheet.views
        for i in range(views.count):
            view = views.item(i + 1)
            if view.name == "Main View":
                main_view = view
                break

        if not main_view:
            print(f"DEBUG: No Main View found in sheet '{sheet_name}'")
            return {"success": False, "error": "No Main View found in sheet"}

        # Step 4: Get Scale Property from Main View
        if hasattr(main_view, 'scale'):
            scale_value = main_view.scale
            print(f"DEBUG: Raw scale value from CATIA: {scale_value}")

            # Step 5: Convert to ratio format and update text field
            if scale_value == 1.0:
                scale_ratio = "1:1"
            elif scale_value >= 1.0:
                scale_ratio = f"{int(scale_value)}:1"
            else:
                # For scales like 0.5, 0.25, etc.
                denominator = int(1 / scale_value)
                scale_ratio = f"1:{denominator}"

            # Update the scale text in the background view
            update_scale_text(sheet, scale_ratio)
            return {"success": True, "message": f"Scale updated to {scale_ratio}"}
        else:
            print(f"DEBUG: Main View has no scale property")
            return {"success": False, "error": "Main View has no scale property"}

    except Exception as e:
        print(f"DEBUG: Error in update_page_scale: {str(e)}")
        return {"success": False, "error": f"Error updating page scale: {str(e)}"}


def get_view_scale(view):
    """Extract scale ratio from a CATIA view"""
    try:
        if hasattr(view, 'scale'):
            scale_value = view.scale

            # Convert scale value to ratio format
            if scale_value >= 1:
                # For scales like 2:1, 5:1
                ratio = f"{int(scale_value)}:1"
            else:
                # For scales like 1:2, 1:5
                denominator = int(1 / scale_value)
                ratio = f"1:{denominator}"

            return ratio
        else:
            return "1:1"
    except:
        return "1:1"


def update_scale_text(sheet, new_scale):
    """Update the scale text in the background view"""
    from application.pycatia_scripts.drawing.new_drawing_support.background_view import get_background_view_and_factory
    from application.pycatia_scripts.drawing.new_drawing_support.paper_size import get_sheet_size_info
    from pycatia.enumeration.enumeration_types import cat_text_anchor_position

    background_view, factory_2d, main_view = get_background_view_and_factory(sheet)

    # Get sheet dimensions for text field positioning
    try:
        size_info = get_sheet_size_info(sheet)
        text_field_x = size_info['sheet_x'] - 180
        text_field_y = size_info['sheet_y']
    except:
        # Fallback to default positioning
        text_field_x = 420
        text_field_y = 297

    # Find existing scale text
    texts = background_view.texts
    scale_text = None

    # Look for existing scale text at the expected position
    for text in texts:
        if abs(text.x - (text_field_x + 1)) < 1 and abs(text.y - (text_field_y + 21)) < 1:
            scale_text = text
            break

    if scale_text:
        # Update existing text
        scale_text.text = new_scale
        scale_text.update()
    else:
        # Create new scale text
        scale_text = texts.add(new_scale, text_field_x + 1, text_field_y + 21)
        scale_text.anchor_position = cat_text_anchor_position.index('catBottomLeft')
        props = scale_text.text_properties
        props.font_size = 2.5
        props.update()
