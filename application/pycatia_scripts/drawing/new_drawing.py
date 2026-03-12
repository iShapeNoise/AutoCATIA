from pycatia.drafting_interfaces.drawing_document import DrawingDocument
from application.pycatia_scripts.common import get_output
from application.support.documents import get_drawing_document
from application.pycatia_scripts.drawing.drawing_template import insert_drawing_template

def create_new_drawing(paper_size: str):
    """Create a new drawing with specific paper size template"""

    pt_drawing_document, errors = get_drawing_document()
    output = get_output()

    output['errors'] = output['errors'] + errors

    if output['errors']:
        return output

    # Set up form parameters for the specific paper size
    form_parameters = {
        'DRAWING-NUMBER': '[ drawing number ]',
        'TITLE': '[ title ]',
        'DRAWN-BY': '[ drawn by ]',
        'REVISION': 'XX',
        'CREATED-ON': '',  # Will be auto-populated by JavaScript
        'AUTHOR': '[ author ]',
        'MANAGER': '[ manager ]',
        'PART-NUMBER': '[ part number ]',
        'MATERIAL': '[ material ]',
        'COMMENTS': '[ comments ]',
        'DOCUMENT-TYPE': '[ document type ]',
    }

    # Create the drawing template
    result = insert_drawing_template(form_parameters)

    output['data'] = f'New {paper_size.upper()} drawing created successfully.'
    output['errors'] = result['errors']

    return output
