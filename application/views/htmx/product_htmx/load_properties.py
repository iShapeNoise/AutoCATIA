from flask import request, render_template
from application import app
from application.support.load_properties import load_product_properties
from application.views.url_prefixes import htmx


@app.route(f'{htmx}/product/load_properties', methods=['POST'])
def htmx_product_load_properties():  # Changed from htmx_load_product_properties
    """
    Load properties from selected product and render form
    """
    selected_product = request.form.get('selected_product')

    if not selected_product:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=['No product selected']
        )

    default_properties, user_defined_properties, errors = load_product_properties(selected_product)

    return render_template(
        'partials/form_product_properties.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties,
        errors=errors
    )
