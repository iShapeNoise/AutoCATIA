from typing import Dict, List, Tuple, Optional
from pycatia.product_structure_interfaces.product import Product
from application.support.documents import get_part_document, get_product_document
from application.support.properties import get_properties
from application.pycatia_scripts.part.edit_part import check_open_parts
from application.pycatia_scripts.product.edit_product import check_open_products


def get_open_parts() -> List[str]:
    """
    Get list of open CATPart documents
    Returns list of part names without extension
    """
    return check_open_parts()


def get_open_products() -> List[str]:
    """
    Get list of open CATProduct documents
    Returns list of product names without extension
    """
    return check_open_products()


def load_part_properties(part_name: str) -> Tuple[Dict, Dict, List]:
    """
    Load properties from a specific open part document
    """
    from application.support.documents import get_part_document
    from application.pycatia_scripts.com_objects import get_app_object

    errors = []

    try:
        # Get the CATIA application
        application = get_app_object()
        if not application:
            errors.append('CATIA application not found')
            return {}, {}, errors

        documents = application.documents
        target_doc = None

        # Find the target part document
        for i in range(documents.count):
            doc = documents.item(i + 1)
            doc_name = doc.name
            # Remove .CATPart extension if present for comparison
            clean_name = doc_name.replace('.CATPart', '').replace('.catpart', '')
            if clean_name == part_name.replace('.CATPart', '').replace('.catpart', ''):
                target_doc = doc
                break

        if not target_doc:
            errors.append(f'Part "{part_name}" not found in open documents')
            return {}, {}, errors

        # Activate the document using the correct method
        target_doc.activate()  # This is the correct way to switch documents

        # Now get the part document properties
        pt_part_document, doc_errors = get_part_document()
        errors.extend(doc_errors)

        if doc_errors:
            return {}, {}, errors

        part = pt_part_document.part
        product = pt_part_document.product

        # Get properties using the existing function
        from application.support.properties import get_properties
        default_properties = get_properties(product, 'default')
        user_defined_properties = get_properties(product, 'user')

        return default_properties, user_defined_properties, errors

    except Exception as e:
        errors.append(f'Error loading part properties: {str(e)}')
        return {}, {}, errors


def load_product_properties(product_name: str) -> Tuple[Dict, Dict, List[str]]:
    """
    Load properties for a specific product

    :param product_name: Name of the product (without .CATProduct extension)
    :return: Tuple of (default_properties, user_defined_properties, errors)
    """
    errors = []
    default_properties = {}
    user_defined_properties = {}

    try:
        # Get the active product document
        pt_product_document, doc_errors = get_product_document(product_only=False)
        if doc_errors:
            errors.extend(doc_errors)
            return default_properties, user_defined_properties, errors

        # Verify this is the correct product
        current_product_name = pt_product_document.product.name
        if current_product_name != product_name:
            errors.append(f'Selected product "{product_name}" does not match active product "{current_product_name}"')
            return default_properties, user_defined_properties, errors

        # Load properties
        product = pt_product_document.product
        default_properties = get_properties(product, 'default')
        user_defined_properties = get_properties(product, 'user')

    except Exception as e:
        errors.append(f'Error loading product properties: {str(e)}')

    return default_properties, user_defined_properties, errors


def get_active_document_info() -> Dict[str, any]:
    """
    Get information about the currently active document
    Returns dict with document type, name, and whether it can be edited
    """
    info = {
        'type': None,
        'name': None,
        'can_edit': False,
        'error': None
    }

    try:
        # Try part first
        pt_part_document, part_errors = get_part_document()
        if not part_errors:
            info['type'] = 'part'
            info['name'] = pt_part_document.part.name
            info['can_edit'] = True
            return info

        # Try product
        pt_product_document, product_errors = get_product_document(product_only=False)
        if not product_errors:
            info['type'] = 'product'
            info['name'] = pt_product_document.product.name
            info['can_edit'] = True
            return info

        info['error'] = 'No active part or product document found'

    except Exception as e:
        info['error'] = f'Error getting document info: {str(e)}'

    return info
