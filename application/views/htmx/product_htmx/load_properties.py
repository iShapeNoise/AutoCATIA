from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.support.documents import get_product_document
from application.support.properties import get_properties
from pycatia.exception_handling import CATIAApplicationException
from pycatia.knowledge_interfaces.parameters import com_error


@app.route(f'{htmx}/product/load_properties', methods=['POST'])
def htmx_load_product_properties():
    """
    Load properties from selected product and render form
    """
    selected_product = request.form.get('selected_product')

    if not selected_product:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=['No product selected'],
            form_type='product'
        )

    try:
        # Get the product document by name
        from application.pycatia_scripts.com_objects import get_app_object
        application = get_app_object()
        documents = application.documents

        # Find and activate the selected product
        doc = None
        for i in range(documents.count):
            test_doc = documents.item(i + 1)
            if test_doc.name == selected_product:
                doc = test_doc
                doc.activate()  # Activate the document
                break

        if not doc:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=[f'Product "{selected_product}" not found'],
                form_type='product'
            )

        # Get product document and properties
        pt_product_document, errors = get_product_document(product_only=False)

        if errors:
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=errors,
                form_type='product'
            )

        product = pt_product_document.product

        # Get properties with error handling
        try:
            default_properties = get_properties(product, 'default')
        except Exception as e:
            default_properties = {}

        try:
            user_defined_properties = get_properties(product, 'user')
        except Exception as e:
            user_defined_properties = {}

        return render_template(
            'partials/form_product_properties.html',
            default_properties=default_properties,
            user_defined_properties=user_defined_properties,
            form_type='product'
        )

    except (CATIAApplicationException, com_error) as e:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[f'Error loading product properties: {str(e)}'],
            form_type='product'
        )
    except Exception as e:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[f'Unexpected error: {str(e)}'],
            form_type='product'
        )
