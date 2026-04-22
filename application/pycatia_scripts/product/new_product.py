from pycatia.product_structure_interfaces.product_document import ProductDocument
from werkzeug.datastructures import ImmutableMultiDict

from application.pycatia_scripts.common import get_output
from application.pycatia_scripts.common import check_part_number_exists
from application.pycatia_scripts.com_objects import get_app_object
from application.support.properties import update_properties


def create_new_product(form: ImmutableMultiDict):
    """
    Create a new CATIA product with form data - UPDATED VERSION
    """
    output = get_output()

    # DEBUG: Print all form data received
    print("=== DEBUG: Form Data Received ===")
    for key, value in form.items():
        print(f"{key}: {value}")
    print("================================")

    application = get_app_object()
    documents = application.documents

    # Get part number and project path from form
    part_number = form.get('part_number', '')
    project_path = form.get('project_path', '')

    print(f"=== DEBUG: Extracted part_number: '{part_number}' ===")
    print(f"=== DEBUG: Extracted project_path: '{project_path}' ===")

    if not part_number:
        print("=== DEBUG: Part number is empty! ===")
        output['errors'].append('Part number is required')
        return output

    output = check_part_number_exists(documents, output, part_number)

    if output['errors']:
        return output

    # Normalize project path (ensure it ends with \)
    if project_path and not project_path.endswith('\\'):
        project_path += '\\'

    # Construct full file path
    if project_path:
        full_path = f"{project_path}{part_number}.CATProduct"
    else:
        full_path = f"{part_number}.CATProduct"

    print(f"=== DEBUG: Full file path: '{full_path}' ===")

    try:
        # Create new product document
        product_document = ProductDocument(documents.add('Product').com_object)
        product = product_document.product

        print("=== DEBUG: Product document created ===")

        # Set product name first (this is crucial for CATIA)
        try:
            product.name = part_number
            print(f"=== DEBUG: Product name set to: '{part_number}' ===")
        except Exception as e:
            print(f"=== DEBUG: ERROR setting product name: {e} ===")
            output['errors'].append(f'Failed to set product name: {e}')

        # Set product part_number
        try:
            product.part_number = part_number
            print(f"=== DEBUG: Product part_number set to: '{part_number}' ===")
        except Exception as e:
            print(f"=== DEBUG: ERROR setting product part_number: {e} ===")
            output['errors'].append(f'Failed to set product part_number: {e}')

        # Update properties with form data
        try:
            update_properties(product, form)
            print("=== DEBUG: Properties updated successfully ===")
        except Exception as e:
            print(f"=== DEBUG: Error updating properties: {e} ===")
            output['errors'].append(f'Failed to set properties: {e}')

        # Save document to specified path if provided
        if project_path:
            try:
                print(f"=== DEBUG: Saving document to: {full_path} ===")
                product_document.save_as(full_path)
                print("=== DEBUG: Document saved successfully ===")
            except Exception as e:
                print(f"=== DEBUG: Error saving document: {e} ===")
                output['errors'].append(f'Failed to save document: {e}')

        output['data'] = f'New Product "{part_number}" created.'
        print("=== DEBUG: Product creation completed ===")

        return output

    except Exception as e:
        print(f"=== DEBUG: Unexpected error: {e} ===")
        output['errors'].append(f'There was a problem: {e}')
        return output
