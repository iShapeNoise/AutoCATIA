from pycatia.mec_mod_interfaces.part_document import PartDocument
from pycatia.product_structure_interfaces.product_document import ProductDocument
from werkzeug.datastructures import ImmutableMultiDict
from application.support.properties import update_properties
from application.pycatia_scripts.common import check_part_number_exists
from application.pycatia_scripts.common import get_output
from application.pycatia_scripts.com_objects import get_app_object
from application.pycatia_scripts.settings import part_template


def create_new_part(form: ImmutableMultiDict):
    """
    Create a new CATIA part with form data
    """
    output = get_output()

    # Extract form data with debug
    number = form.get('number', '001')
    title = form.get('title', 'Part')
    revision = form.get('revision', 'P01')

    # Generate filename from form fields
    part_number = f"{number}_{title}_{revision}"

    print(f"=== DEBUG: Extracted number: '{number}' ===")
    print(f"=== DEBUG: Generated part_number: '{part_number}' ===")

    application = get_app_object()
    documents = application.documents

    # Check for existing part number
    output = check_part_number_exists(documents, output, part_number)
    if output['errors']:
        return output

    try:
        # Create part document
        part_document = PartDocument(documents.add('Part').com_object)

        # Update form with generated part_number for properties
        form_data = dict(form)
        form_data['part_number'] = part_number

        # Update properties using the modified form data
        update_properties(part_document.product, form_data)

        # Apply template structure
        part = part_document.part
        if part_template['geometric_sets']:
            hybrid_bodies = part.hybrid_bodies
            for gs_name in part_template['geometric_sets']:
                new_gs = hybrid_bodies.add()
                new_gs.name = gs_name

        if part_template['parameters']:
            parameters = part.parameters
            for parm in part_template['parameters']:
                name = parm
                type_ = part_template['parameters'][parm]['type'].upper()
                value = part_template['parameters'][parm]['value']
                allowed_dimensions = ['LENGTH']
                if type_ in allowed_dimensions:
                    parameters.create_dimension(name, type_, value)

        part.update()
        output['data'] = f'New Part "{part_number}" created.'

    except Exception as e:
        output['errors'].append(f'Failed to create part: {e}')
        print(f"=== DEBUG: Part creation error: {e} ===")

    return output
