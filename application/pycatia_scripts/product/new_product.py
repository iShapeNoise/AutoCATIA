from pycatia.product_structure_interfaces.product_document import ProductDocument
from werkzeug.datastructures import ImmutableMultiDict
from application.support.properties import update_properties_enum
from application.pycatia_scripts.common import get_output
from application.pycatia_scripts.com_objects import get_app_object
from application.pycatia_scripts.settings import product_template

import os
from pathlib import Path

def check_product_number_exists(documents, output, product_number):
    """Check if product number already exists in open documents"""
    for i in range(documents.count):
        document = documents.item(i + 1)
        if document.name == f"{product_number}.CATProduct":
            output['errors'].append(f"Product '{product_number}' already exists")
            return output
    return output

def check_file_exists(project_path, product_number):
    """Check if file already exists on disk"""
    if project_path:
        file_path = Path(project_path) / f"{product_number}.CATProduct"
        return file_path.exists()
    return False


def create_new_product(form: ImmutableMultiDict):
    """
    Create a new CATIA product with enum-based properties
    """
    output = get_output()

    # Extract form data
    number = form.get('number', '001')
    title = form.get('title', 'Product')
    revision = form.get('revision', 'P01')

    # Generate filename from form fields
    product_number = f"{number}_{title}_{revision}"

    print(f"=== DEBUG: Generated product_number: '{product_number}' ===")

    application = get_app_object()
    documents = application.documents

    output = check_product_number_exists(documents, output, product_number)

    if output['errors']:
        return output

    # Create product document
    product_document = ProductDocument(documents.add('Product').com_object)

    # Update properties using enum-based approach
    update_properties_enum(product_document.product, form)

    # Set product_number directly after enum update
    product_document.product.part_number = product_number
    print(f"=== DEBUG: Final product_number set: {product_number} ===")

    # Products don't have geometric sets or parameters like parts
    # Skip part-specific creation logic

    # Save document
    project_path = form.get('project_path', '')
    if project_path:
        try:
            from pathlib import Path
            full_path = Path(project_path) / f"{product_number}.CATProduct"
            product_document.save_as(str(full_path))
            print(f"=== DEBUG: Document saved to: {full_path} ===")
        except Exception as e:
            print(f"=== DEBUG: Save error: {e} ===")

    output['data'] = f'New Product "{product_number}" created.'
    return output
