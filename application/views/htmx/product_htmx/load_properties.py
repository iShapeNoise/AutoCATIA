from flask import request, render_template
from application import app
from application.views.url_prefixes import htmx
from application.support.documents import get_product_document
from application.support.properties import get_properties
from pycatia.exception_handling import CATIAApplicationException
from pycatia.knowledge_interfaces.parameters import com_error


@app.route(f'{htmx}/product/load_properties', methods=['POST'])
def htmx_load_product_properties():
    """Load properties from selected product and render form"""
    selected_product = request.form.get('selected_product')
    print(f"=== DEBUG: Loading product: {selected_product} ===")

    if not selected_product:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=['No product selected'],
            form_type='product'
        )

    try:
        # Get the CATIA application
        from application.pycatia_scripts.com_objects import get_app_object
        application = get_app_object()
        documents = application.documents
        print(f"=== DEBUG: Found {documents.count} open documents ===")

        # Find and activate the selected product
        doc = None
        for i in range(documents.count):
            test_doc = documents.item(i + 1)
            doc_name = test_doc.name
            print(f"=== DEBUG: Checking document: {doc_name} ===")

            if (doc_name == selected_product or
                doc_name == selected_product.replace('.CATProduct', '') or
                doc_name == selected_product + '.CATProduct'):
                doc = test_doc
                print(f"=== DEBUG: Found matching document: {doc_name} ===")
                break

        if not doc:
            error_msg = f'Product "{selected_product}" not found'
            print(f"=== DEBUG: {error_msg} ===")
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=[error_msg],
                form_type='product'
            )

        # Activate the document
        print(f"=== DEBUG: Activating document ===")
        doc.activate()

        # Get product document wrapper
        print(f"=== DEBUG: Getting product document wrapper ===")
        pt_product_document, errors = get_product_document(product_only=False)

        if errors:
            print(f"=== DEBUG: Document wrapper errors: {errors} ===")
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=errors,
                form_type='product'
            )

        # Get properties
        print(f"=== DEBUG: Getting properties from product ===")
        product = pt_product_document.product
        default_properties = get_properties(product, 'default')
        user_defined_properties = get_properties(product, 'user')

        print(f"=== DEBUG: Retrieved {len(default_properties)} default properties ===")
        print(f"=== DEBUG: Retrieved {len(user_defined_properties)} user properties ===")

        return render_template(
            'partials/form_product_properties.html',
            default_properties=default_properties,
            user_defined_properties=user_defined_properties,
            form_type='product'
        )

    except (CATIAApplicationException, com_error) as e:
        error_msg = f'CATIA Error loading product properties: {str(e)}'
        print(f"=== DEBUG: {error_msg} ===")
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[error_msg],
            form_type='product'
        )
    except Exception as e:
        error_msg = f'Unexpected error loading product properties: {str(e)}'
        print(f"=== DEBUG: {error_msg} ===")
        import traceback
        print(f"=== DEBUG: Traceback: {traceback.format_exc()} ===")
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[error_msg],
            form_type='product'
        )
