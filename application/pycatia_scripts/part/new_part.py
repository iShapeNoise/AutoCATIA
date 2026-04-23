from pycatia.mec_mod_interfaces.part_document import PartDocument
from pycatia.product_structure_interfaces.product_document import ProductDocument
from werkzeug.datastructures import ImmutableMultiDict
from application.support.properties import update_properties
from application.pycatia_scripts.common import check_part_number_exists
from application.pycatia_scripts.common import get_output
from application.pycatia_scripts.com_objects import get_app_object
from application.pycatia_scripts.settings import part_template

import os
from pathlib import Path

def check_part_number_exists(documents, output, part_number):
    """Check if part number already exists in open documents"""
    for i in range(documents.count):
        document = documents.item(i + 1)
        if document.name == f"{part_number}.CATPart":
            output['errors'].append(f"Part '{part_number}' already exists")
            return output
    return output

def check_file_exists(project_path, part_number):
    """Check if file already exists on disk"""
    if project_path:
        file_path = Path(project_path) / f"{part_number}.CATPart"
        return file_path.exists()
    return False


def create_new_part(form: ImmutableMultiDict):
    """
    Create a new CATIA part with enum-based properties
    """
    output = get_output()

    # Extract form data
    number = form.get('number', '001')
    title = form.get('title', 'Part')
    revision = form.get('revision', 'P01')

    # Generate filename from form fields
    part_number = f"{number}_{title}_{revision}"

    print(f"=== DEBUG: Generated part_number: '{part_number}' ===")

    application = get_app_object()
    documents = application.documents

    output = check_part_number_exists(documents, output, part_number)

    if output['errors']:
        return output

    # Create part document
    part_document = PartDocument(documents.add('Part').com_object)

    # Update properties using enum-based approach
    from application.support.properties import update_properties_enum
    update_properties_enum(part_document.product, form)

    # Set part_number directly after enum update
    part_document.product.part_number = part_number
    print(f"=== DEBUG: Final part_number set: {part_number} ===")

    # Rest of part creation logic...
    part = part_document.part

    # Create geometric sets
    if part_template['geometric_sets']:
        hybrid_bodies = part.hybrid_bodies
        for gs_name in part_template['geometric_sets']:
            new_gs = hybrid_bodies.add()
            new_gs.name = gs_name

    # Create parameters
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

    # Save document
    project_path = form.get('project_path', '')
    if project_path:
        try:
            from pathlib import Path
            full_path = Path(project_path) / f"{part_number}.CATPart"
            part_document.save_as(str(full_path))
            print(f"=== DEBUG: Document saved to: {full_path} ===")
        except Exception as e:
            print(f"=== DEBUG: Save error: {e} ===")

    output['data'] = f'New Part "{part_number}" created.'
    return output
