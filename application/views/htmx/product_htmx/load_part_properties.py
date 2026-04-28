from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.support.properties import get_properties
from pycatia.exception_handling import CATIAApplicationException
from pycatia.knowledge_interfaces.parameters import com_error
from pycatia.product_structure_interfaces.product import Product
from pycatia.product_structure_interfaces.products import Products


@app.route(f'{htmx}/product/load_part_properties', methods=['POST'])
def htmx_load_part_properties():
    """
    Load properties from a part within the active product
    """
    selected_part = request.form.get('selected_part')

    if not selected_part:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=['No part selected'],
            form_type='part'
        )

    try:
        # Get the active product document
        from application.support.documents import get_product_document
        pt_product_document, errors = get_product_document(product_only=False)

        if errors:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=errors,
                form_type='part'
            )

        product = pt_product_document.product

        # Find the part in the product structure
        part_product = find_part_in_product(product, selected_part)

        if not part_product:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=[f'Part "{selected_part}" not found in product'],
                form_type='part'
            )

        # Get the part document from the part product
        part_document = part_product.reference_product
        if part_document:
            # Activate the part document
            part_document.activate()

            # Get properties from the activated part
            default_properties = get_properties(part_product, 'default')
            user_defined_properties = get_properties(part_product, 'user')

            return render_template(
                'partials/form_product_properties.html',
                default_properties=default_properties,
                user_defined_properties=user_defined_properties,
                form_type='part'
            )
        else:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=[f'Could not access document for part "{selected_part}"'],
                form_type='part'
            )

    except (CATIAApplicationException, com_error) as e:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[f'Error loading part properties: {str(e)}'],
            form_type='part'
        )
    except Exception as e:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[f'Unexpected error: {str(e)}'],
            form_type='part'
        )


def find_part_in_product(product: Product, part_name: str) -> Product:
    """
    Recursively search for a part within the product structure
    """
    # Check direct children
    products = product.products
    for prod in products:
        if prod.part_number == part_name or prod.name == part_name:
            return prod

    # Recursively check sub-products
    for prod in products:
        if hasattr(prod, 'products'):
            result = find_part_in_product(prod, part_name)
            if result:
                return result

    return None
