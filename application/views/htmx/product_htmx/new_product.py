from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.pycatia_scripts.product.new_product import create_new_product
from application.support.properties import update_user_defined_properties
from application.support.documents import get_product_document

@app.route(f'{htmx}/product/create_new', methods=['POST'])
def htmx_create_new_product():
    try:
        # Create the product
        result = create_new_product(request.form)

        # Get the created product document
        pt_product_document, errors = get_product_document()
        product = pt_product_document.product

        # Reload properties after saving
        from application.support.properties import get_properties
        default_properties = get_properties(product, 'default')
        user_defined_properties = get_properties(product, 'user')

        return render_template(
            'partials/form_product_properties.html',
            default_properties=default_properties,
            user_defined_properties=user_defined_properties,
            data=result.get('data', ''),
            errors=result.get('errors', [])
        )
    except Exception as e:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            data='',
            errors=[f'Error creating product: {str(e)}']
        )
