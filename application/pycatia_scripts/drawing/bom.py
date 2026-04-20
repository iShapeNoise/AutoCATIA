from pathlib import Path
from pycatia import catia
from pycatia.drafting_interfaces.drawing_document import DrawingDocument
from pycatia.drafting_interfaces.drawing_tables import DrawingTables
from pycatia.product_structure_interfaces.product_document import ProductDocument

from application.pycatia_scripts.com_objects import get_app_object
from application.pycatia_scripts.common import get_output
from application.support.documents import get_drawing_document


def check_drawing_bom(drawing_name: str):
    """Check if B.O.M. exists in drawing"""
    output = get_output()

    try:
        application = get_app_object()
        if not application:
            output['errors'].append('CATIA application is not running')
            return output

        documents = application.documents

        # Find the drawing document
        drawing_doc = None
        for doc in documents:
            if doc.name == drawing_name:
                drawing_doc = doc
                break

        if not drawing_doc:
            output['errors'].append(f'Drawing {drawing_name} not found')
            return output

        drawing = DrawingDocument(drawing_doc.com_object)
        sheets = drawing.sheets

        # Check for existing B.O.M. tables in all sheets
        bom_found = False
        for sheet in sheets:
            tables = sheet.tables
            for table in tables:
                if 'BOM' in table.name or 'Bill of Materials' in table.name:
                    bom_found = True
                    break
            if bom_found:
                break

        output['data'] = {'has_bom': bom_found}
        return output

    except Exception as e:
        output['errors'].append(f'Failed to check B.O.M.: {str(e)}')
        return output


def create_drawing_bom(drawing_name: str, selected_columns: list):
    """Create B.O.M. table in drawing"""
    output = get_output()

    try:
        application = get_app_object()
        if not application:
            output['errors'].append('CATIA application is not running')
            return output

        documents = application.documents

        # Find the drawing document
        drawing_doc = None
        for doc in documents:
            if doc.name == drawing_name:
                drawing_doc = doc
                break

        if not drawing_doc:
            output['errors'].append(f'Drawing {drawing_name} not found')
            return output

        drawing = DrawingDocument(drawing_doc.com_object)
        active_sheet = drawing.sheets.active_sheet

        # Get B.O.M. data from related product
        bom_data = get_related_product_bom_data(drawing_name)

        if not bom_data:
            output['errors'].append('No B.O.M. data available from related product')
            return output

        # Create B.O.M. table
        tables = active_sheet.tables
        table = tables.add()
        table.name = "BOM"

        # Set table size (columns x rows)
        num_columns = len(selected_columns)
        num_rows = len(bom_data) + 1  # +1 for header

        table.set_size(num_columns, num_rows)

        # Fill header row
        for i, column in enumerate(selected_columns):
            cell = table.get_cell(i + 1, 1)
            cell.text = column.replace('_', ' ').title()

        # Fill data rows
        for row_idx, row_data in enumerate(bom_data):
            for col_idx, column in enumerate(selected_columns):
                cell = table.get_cell(col_idx + 1, row_idx + 2)
                cell.text = str(row_data.get(column, ''))

        output['data'] = {
            'message': f'B.O.M. created in drawing {drawing_name}',
            'bom_data': bom_data
        }
        return output

    except Exception as e:
        output['errors'].append(f'Failed to create B.O.M.: {str(e)}')
        return output


def save_drawing_bom_changes(drawing_name: str, bom_data: list):
    """Save B.O.M. changes to drawing"""
    output = get_output()

    try:
        application = get_app_object()
        if not application:
            output['errors'].append('CATIA application is not running')
            return output

        documents = application.documents

        # Find the drawing document
        drawing_doc = None
        for doc in documents:
            if doc.name == drawing_name:
                drawing_doc = doc
                break

        if not drawing_doc:
            output['errors'].append(f'Drawing {drawing_name} not found')
            return output

        drawing = DrawingDocument(drawing_doc.com_object)
        sheets = drawing.sheets

        # Find B.O.M. table
        bom_table = None
        for sheet in sheets:
            tables = sheet.tables
            for table in tables:
                if 'BOM' in table.name:
                    bom_table = table
                    break
            if bom_table:
                break

        if not bom_table:
            output['errors'].append('B.O.M. table not found in drawing')
            return output

        # Update table with new data
        for row_idx, row_data in enumerate(bom_data):
            for col_idx, (key, value) in enumerate(row_data.items()):
                cell = bom_table.get_cell(col_idx + 1, row_idx + 2)
                cell.text = str(value)

        # Save the drawing
        drawing_doc.save()

        output['data'] = 'B.O.M. changes saved to drawing'
        return output

    except Exception as e:
        output['errors'].append(f'Failed to save B.O.M.: {str(e)}')
        return output


def get_related_product_bom_data(drawing_name: str):
    """Extract B.O.M. data from related product"""
    try:
        application = get_app_object()
        if not application:
            return []

        documents = application.documents

        # Find the drawing document first to get related product
        drawing_doc = None
        for doc in documents:
            if doc.name == drawing_name:
                drawing_doc = doc
                break

        if not drawing_doc:
            return []

        # TODO: Implement logic to find related product
        # For now, return sample data
        return [
            {
                'part_number': 'PN-001',
                'quantity': '1',
                'description': 'Sample Part 1',
                'material': 'Steel'
            },
            {
                'part_number': 'PN-002',
                'quantity': '2',
                'description': 'Sample Part 2',
                'material': 'Aluminum'
            }
        ]

    except Exception:
        return []


def get_drawing_bom_data(drawing_name: str):
    """Get existing B.O.M. data from drawing"""
    output = get_output()

    try:
        application = get_app_object()
        if not application:
            output['errors'].append('CATIA application is not running')
            return output

        # Find the drawing document
        documents = application.documents
        drawing_doc = None

        for i in range(documents.count):
            doc = documents.item(i + 1)
            if doc.name == drawing_name and doc.name.endswith('.CATDrawing'):
                drawing_doc = doc
                break

        if not drawing_doc:
            output['errors'].append(f'Drawing {drawing_name} not found')
            return output

        # TODO: Extract actual B.O.M. data from drawing tables
        # For now, return sample data
        bom_data = [
            {
                'part_number': 'PART-001',
                'quantity': 1,
                'description': 'Sample Part 1',
                'material': 'Steel'
            },
            {
                'part_number': 'PART-002',
                'quantity': 2,
                'description': 'Sample Part 2',
                'material': 'Aluminum'
            }
        ]

        return bom_data

    except Exception as e:
        output['errors'].append(f'Error getting B.O.M. data: {str(e)}')
        return output
