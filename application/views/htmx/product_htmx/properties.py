from flask import request, render_template
from application import app
from application.support.documents import get_product_document
from application.support.properties import update_properties, get_properties
from application.views.url_prefixes import htmx


@app.route(f'{htmx}/product/properties', methods=['POST'])
def htmx_product_properties():
    print("=== DEBUG: HTMX product properties endpoint called ===")

    pt_product_document, errors = get_product_document(product_only=False)

    if errors:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=errors
        )

    # Update properties with document reference for saving
    update_properties(pt_product_document.product, request.form)

    # Reload properties after saving
    default_properties = get_properties(pt_product_document.product, 'default')
    user_defined_properties = get_properties(pt_product_document.product, 'user')

    print(f"=== DEBUG: Reloaded properties - source: {default_properties.get('source', 'NOT_FOUND')} ===")

    return render_template(
        'partials/form_product_properties.html',
        default_properties=default_properties,
        user_defined_properties=user_defined_properties
    )
