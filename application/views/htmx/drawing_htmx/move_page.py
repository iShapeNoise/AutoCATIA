from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.add_page import get_sheets_for_drawing
from pycatia import catia
from pycatia.enumeration.enumeration_types import cat_work_mode_type
from pycatia.exception_handling import CATIAApplicationException


@app.route(f'{htmx}/drawing/move_page_up', methods=['POST'])
def htmx_move_page_up():
    """Move a page up in the drawing sheet order"""
    selected_drawing = request.form.get('selected_drawing')
    page_name = request.form.get('page_name')

    if not selected_drawing or not page_name:
        return render_template(
            'partials/drawing_pages_table.html',
            pages=[],
            selected_drawing=selected_drawing,
            errors=['Missing drawing or page name']
        )

    try:
        # Get CATIA application and documents
        caa = catia()
        documents = caa.documents

        # Find the drawing document by display name
        target_drawing = None
        for i in range(documents.count):
            doc = documents.item(i + 1)
            display_name = doc.name.replace('.CATDrawing', '').replace('.catdrawing', '')
            if display_name == selected_drawing:
                target_drawing = doc
                break

        if not target_drawing:
            return render_template(
                'partials/drawing_pages_table.html',
                pages=[],
                selected_drawing=selected_drawing,
                errors=['Drawing not found']
            )

        # Get drawing and sheets
        drawing_document = target_drawing.drawing_document()
        drawing = drawing_document.drawing_root
        sheets_collection = drawing.sheets

        # Get all sheets as list
        sheets_list = [sheets_collection.item(i) for i in range(1, sheets_collection.count + 1)]

        # Find current position of the page
        current_index = -1
        for i, sheet in enumerate(sheets_list):
            if sheet.name == page_name:
                current_index = i
                break

        if current_index <= 0:
            # Already at top or not found
            pages = get_sheets_for_drawing(selected_drawing)
            return render_template(
                'partials/drawing_pages_table.html',
                pages=pages,
                selected_drawing=selected_drawing
            )

        # Move up by swapping with previous sheet
        new_order = sheets_list.copy()
        new_order[current_index], new_order[current_index - 1] = new_order[current_index - 1], new_order[current_index]

        # Apply new order
        drawing.reorder_sheets(tuple(new_order))

        # Get updated pages list
        pages = get_sheets_for_drawing(selected_drawing)

        return render_template(
            'partials/drawing_pages_table.html',
            pages=pages,
            selected_drawing=selected_drawing
        )

    except (CATIAApplicationException, Exception) as e:
        return render_template(
            'partials/drawing_pages_table.html',
            pages=[],
            selected_drawing=selected_drawing,
            errors=[f'Error moving page up: {str(e)}']
        )


@app.route(f'{htmx}/drawing/move_page_down', methods=['POST'])
def htmx_move_page_down():
    """Move a page down in the drawing sheet order"""
    selected_drawing = request.form.get('selected_drawing')
    page_name = request.form.get('page_name')

    if not selected_drawing or not page_name:
        return render_template(
            'partials/drawing_pages_table.html',
            pages=[],
            selected_drawing=selected_drawing,
            errors=['Missing drawing or page name']
        )

    try:
        # Get CATIA application and documents
        caa = catia()
        documents = caa.documents

        # Find the drawing document by display name
        target_drawing = None
        for i in range(documents.count):
            doc = documents.item(i + 1)
            display_name = doc.name.replace('.CATDrawing', '').replace('.catdrawing', '')
            if display_name == selected_drawing:
                target_drawing = doc
                break

        if not target_drawing:
            return render_template(
                'partials/drawing_pages_table.html',
                pages=[],
                selected_drawing=selected_drawing,
                errors=['Drawing not found']
            )

        # Get drawing and sheets
        drawing_document = target_drawing.drawing_document()
        drawing = drawing_document.drawing_root
        sheets_collection = drawing.sheets

        # Get all sheets as list
        sheets_list = [sheets_collection.item(i) for i in range(1, sheets_collection.count + 1)]

        # Find current position of the page
        current_index = -1
        for i, sheet in enumerate(sheets_list):
            if sheet.name == page_name:
                current_index = i
                break

        if current_index == -1 or current_index >= len(sheets_list) - 1:
            # Already at bottom or not found
            pages = get_sheets_for_drawing(selected_drawing)
            return render_template(
                'partials/drawing_pages_table.html',
                pages=pages,
                selected_drawing=selected_drawing
            )

        # Move down by swapping with next sheet
        new_order = sheets_list.copy()
        new_order[current_index], new_order[current_index + 1] = new_order[current_index + 1], new_order[current_index]

        # Apply new order
        drawing.reorder_sheets(tuple(new_order))

        # Get updated pages list
        pages = get_sheets_for_drawing(selected_drawing)

        return render_template(
            'partials/drawing_pages_table.html',
            pages=pages,
            selected_drawing=selected_drawing
        )

    except (CATIAApplicationException, Exception) as e:
        return render_template(
            'partials/drawing_pages_table.html',
            pages=[],
            selected_drawing=selected_drawing,
            errors=[f'Error moving page down: {str(e)}']
        )
