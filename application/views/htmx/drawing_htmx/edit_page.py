from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.drawing.add_page import get_sheets_for_drawing
from pycatia import catia
from pycatia.drafting_interfaces.drawing_document import DrawingDocument


@app.route(f'{htmx}/drawing/load_edit_page', methods=['POST'])
def htmx_load_edit_page():
    """Load edit form for a specific page"""
    selected_drawing = request.form.get('selected_drawing')
    page_name = request.form.get('page_name')

    if not selected_drawing or not page_name:
        return render_template('partials/errors.html', errors=['Missing drawing or page name'])

    try:
        # Get CATIA application and documents
        caa = catia()
        documents = caa.documents

        # Find the drawing document
        target_drawing = None
        for i in range(documents.count):
            doc = documents.item(i + 1)
            display_name = doc.name.replace('.CATDrawing', '').replace('.catdrawing', '')
            if display_name == selected_drawing:
                target_drawing = doc
                break

        if not target_drawing:
            return render_template('partials/errors.html', errors=['Drawing not found'])

        # Get drawing document and sheets
        drawing_document = DrawingDocument(target_drawing.com_object)
        drawing = drawing_document.drawing_root
        sheets_collection = drawing.sheets

        # Find the specific sheet
        target_sheet = None
        for i in range(1, sheets_collection.count + 1):
            sheet = sheets_collection.item(i)
            if sheet.name == page_name:
                target_sheet = sheet
                break

        if not target_sheet:
            return render_template('partials/errors.html', errors=['Page not found'])

        # Extract data from sheet
        part_number = get_part_number_from_sheet(target_sheet)
        format_key = get_sheet_format_key(target_sheet)
        document_type = get_document_type_from_sheet(target_sheet)

        return render_template('partials/page_edit_form.html',
                             selected_drawing=selected_drawing,
                             page_name=page_name,
                             part_number=part_number,
                             format_key=format_key,
                             document_type=document_type)

    except Exception as e:
        return render_template('partials/errors.html', errors=[f'Error loading page: {str(e)}'])


@app.route(f'{htmx}/drawing/update_page_properties', methods=['POST'])
def htmx_update_page_properties():
    """Update page properties in CATIA"""
    selected_drawing = request.form.get('selected_drawing')
    page_name = request.form.get('page_name')
    new_page_name = request.form.get('edit_page_name')
    document_type = request.form.get('edit_document_type')
    format_key = request.form.get('edit_format')

    if not selected_drawing or not page_name:
        return render_template('partials/errors.html', errors=['Missing drawing or page name'])

    if not new_page_name:
        return render_template('partials/errors.html', errors=['No sheet name provided'])

    try:
        # Get CATIA application and documents
        caa = catia()
        documents = caa.documents

        # Find the drawing document
        target_drawing = None
        for i in range(documents.count):
            doc = documents.item(i + 1)
            display_name = doc.name.replace('.CATDrawing', '').replace('.catdrawing', '')
            if display_name == selected_drawing:
                target_drawing = doc
                break

        if not target_drawing:
            return render_template('partials/errors.html', errors=['Drawing not found'])

        # Get drawing document and sheets
        drawing_document = DrawingDocument(target_drawing.com_object)
        drawing = drawing_document.drawing_root
        sheets_collection = drawing.sheets

        # Find the specific sheet
        target_sheet = None
        for i in range(1, sheets_collection.count + 1):
            sheet = sheets_collection.item(i)
            if sheet.name == page_name:
                target_sheet = sheet
                break

        if not target_sheet:
            return render_template('partials/errors.html', errors=['Page not found'])

        # Update sheet name if changed
        if new_page_name != page_name:
            target_sheet.name = new_page_name
            target_sheet.force_update()

        # Update format if changed
        if format_key:
            paper_size_mapping = {
                'A0': 2, 'A1': 3, 'A2': 4, 'A3': 5, 'A4': 6
            }
            catia_paper_size = paper_size_mapping.get(format_key, 5)
            target_sheet.paper_size = catia_paper_size
            target_sheet.force_update()

        # Update text fields if document_type provided
        if document_type:
            # Implementation for updating text fields would go here
            # You could use the text field update logic from new_drawing_support
            pass

        return render_template('partials/success.html', data=f'Page "{new_page_name}" updated successfully')

    except Exception as e:
        return render_template('partials/errors.html', errors=[f'Error updating page: {str(e)}'])


def get_sheet_format_key(sheet):
    """Convert CATIA paper size enum to format key"""
    paper_size = sheet.paper_size
    format_mapping = {
        2: 'A0', 3: 'A1', 4: 'A2', 5: 'A3', 6: 'A4'
    }
    base_format = format_mapping.get(paper_size, 'A3')

    # Check orientation for A4
    if base_format == 'A4' and sheet.orientation == 0:
        return 'A4-portrait'
    elif base_format == 'A4':
        return 'A4-landscape'
    return base_format


def get_part_number_from_sheet(sheet):
    """Extract part number from sheet text fields"""
    try:
        # Get background view to access text fields
        from .new_drawing_support.background_view import get_background_view_and_factory
        background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
        texts = background_view.texts

        # Look for text that matches part number pattern (digits_underscores)
        for i in range(1, texts.count + 1):
            text = texts.item(i)
            text_string = text.text

            # Check if text looks like a part number (contains digits and underscores)
            if any(char.isdigit() for char in text_string) and '_' in text_string:
                return text_string

        return ""
    except:
        return ""


def get_sheet_format_key(sheet):
    """Convert CATIA paper size enum to format key"""
    try:
        paper_size = sheet.paper_size
        orientation = getattr(sheet, 'orientation', 1)  # Default to landscape

        # Map CATIA enum values to format keys
        size_mapping = {
            2: 'A0',   # catPaperA0
            3: 'A1',   # catPaperA1
            4: 'A2',   # catPaperA2
            5: 'A3',   # catPaperA3
            6: 'A4'    # catPaperA4
        }

        base_format = size_mapping.get(paper_size, 'A3')

        # Check orientation for A4
        if base_format == 'A4':
            if orientation == 0:  # Portrait
                return 'A4-portrait'
            else:  # Landscape
                return 'A4-landscape'

        return base_format
    except:
        return 'A3'


def get_document_type_from_sheet(sheet):
    """Extract document type from sheet text fields"""
    try:
        # Get background view to access text fields
        from application.pycatia_scripts.drawing.new_drawing_support.background_view import get_background_view_and_factory
        background_view, factory_2d, main_view = get_background_view_and_factory(sheet)
        texts = background_view.texts

        # Look for text that matches document type patterns
        # Common document types: "Assembly", "Detail", "Scheme", etc.
        document_type_patterns = ['assembly', 'detail', 'scheme', 'drawing', 'manufacturing', 'inspection']

        for i in range(1, texts.count + 1):
            text = texts.item(i)
            text_string = text.text.lower().strip()

            # Check if text matches any document type pattern
            for pattern in document_type_patterns:
                if pattern in text_string:
                    # Return with proper capitalization
                    return pattern.title()

        return ""  # No document type found

    except Exception as e:
        print(f"Error extracting document type: {str(e)}")
        return ""
