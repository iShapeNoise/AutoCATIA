from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.support.documents import get_product_document
from application.support.properties import get_properties

@app.route(f'{htmx}/product/load_properties', methods=['POST'])
def htmx_product_load_properties():
    selected_product = request.form.get('selected_product')

    if not selected_product:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=['No product selected']
        )

    try:
        pt_product_document, errors = get_product_document(product_only=False)
        if errors:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=errors
            )

        product = pt_product_document.product
        default_properties = get_properties(product, 'default')
        user_defined_properties = get_properties(product, 'user')

        return render_template(
            'partials/form_product_properties.html',
            default_properties=default_properties,
            user_defined_properties=user_defined_properties
        )

    except Exception as e:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[f'Error loading properties: {str(e)}']
        )
