from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.support.documents import get_part_document
from application.support.properties import get_properties
from pycatia.exception_handling import CATIAApplicationException
from pycatia.knowledge_interfaces.parameters import com_error
from pycatia import catia
from pycatia.enumeration.enumeration_types import cat_work_mode_type


@app.route(f'{htmx}/part/load_properties', methods=['POST'])
def htmx_load_part_properties():
    """
    Load properties from selected part and render form
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
        # Get CATIA application and active document
        caa = catia()
        document = caa.active_document
        product = document.product

        # Ensure all components are loaded
        product.apply_work_mode(cat_work_mode_type.index("DESIGN_MODE"))

        # Find the selected part in the product structure
        part_path = None
        for sub_product in product.products:
            if sub_product.is_catpart():
                # Get the reference product (the actual CATPart document)
                reference_product = sub_product.reference_product
                current_part_path = reference_product.path()

                # Check if this matches the selected part
                if selected_part in str(current_part_path) or sub_product.name in selected_part:
                    part_path = current_part_path
                    break

        if not part_path:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=['Part not found in product structure'],
                form_type='part'
            )

        # Open the part file
        caa.documents.open(part_path)

        # Now get the part document and properties
        pt_part_document, errors = get_part_document()

        if errors:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=errors,
                form_type='part'
            )

        part = pt_part_document.part
        default_properties = get_properties(part, 'default')
        user_defined_properties = get_properties(part, 'user')

        return render_template(
            'partials/form_product_properties.html',
            default_properties=default_properties,
            user_defined_properties=user_defined_properties,
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
