from flask import request, render_template
from application import app
from application.support.load_properties import load_part_properties
from application.views.url_prefixes import htmx


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
        # Load properties from the selected part
        default_properties, user_defined_properties, errors = load_part_properties(selected_part)

        # DEBUG: Print what's being passed to template
        print(f"=== DEBUG: Passing to template - source: '{default_properties.get('source', 'NOT_FOUND')}' ===")

        if errors:
            return render_template(
                'partials/form_product_properties.html',
                default_properties=default_properties,
                user_defined_properties=user_defined_properties,
                errors=errors,
                form_type='part'
            )

        return render_template(
            'partials/form_product_properties.html',
            default_properties=default_properties,
            user_defined_properties=user_defined_properties,
            form_type='part'
        )

    except Exception as e:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[f'Error loading part properties: {str(e)}'],
            form_type='part'
        )
