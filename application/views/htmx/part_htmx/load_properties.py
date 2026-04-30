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
    """Load properties from selected part and render form"""
    selected_part = request.form.get('selected_part')
    print(f"=== DEBUG: Loading part: {selected_part} ===")

    if not selected_part:
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=['No part selected'],
            form_type='part'
        )

    try:
        # Get CATIA application
        caa = catia()
        documents = caa.documents
        print(f"=== DEBUG: Found {documents.count} open documents ===")

        # Find and activate the part directly
        target_doc = None
        for i in range(documents.count):
            doc = documents.item(i + 1)
            doc_name = doc.name
            print(f"=== DEBUG: Checking document: {doc_name} ===")

            # Check for exact match or match without extension
            if (doc_name == selected_part or
                doc_name == selected_part.replace('.CATPart', '') or
                doc_name == selected_part + '.CATPart'):
                target_doc = doc
                print(f"=== DEBUG: Found matching document: {doc_name} ===")
                break

        if not target_doc:
            error_msg = f'Part "{selected_part}" not found in open documents'
            print(f"=== DEBUG: {error_msg} ===")
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=[error_msg],
                form_type='part'
            )

        # Activate the document
        print(f"=== DEBUG: Activating document ===")
        target_doc.activate()

        # Get the part document wrapper
        print(f"=== DEBUG: Getting part document wrapper ===")
        pt_part_document, doc_errors = get_part_document()

        if doc_errors:
            print(f"=== DEBUG: Document wrapper errors: {doc_errors} ===")
            return render_template(
                'partials/form_product_properties.html',
                default_properties={},
                user_defined_properties={},
                errors=doc_errors,
                form_type='part'
            )

        # Get properties
        print(f"=== DEBUG: Getting properties from product ===")
        product = pt_part_document.product
        default_properties = get_properties(product, 'default')
        user_defined_properties = get_properties(product, 'user')

        print(f"=== DEBUG: Retrieved {len(default_properties)} default properties ===")
        print(f"=== DEBUG: Retrieved {len(user_defined_properties)} user properties ===")

        return render_template(
            'partials/form_product_properties.html',
            default_properties=default_properties,
            user_defined_properties=user_defined_properties,
            form_type='part'
        )

    except (CATIAApplicationException, com_error) as e:
        error_msg = f'CATIA Error loading part properties: {str(e)}'
        print(f"=== DEBUG: {error_msg} ===")
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[error_msg],
            form_type='part'
        )
    except Exception as e:
        error_msg = f'Unexpected error loading part properties: {str(e)}'
        print(f"=== DEBUG: {error_msg} ===")
        import traceback
        print(f"=== DEBUG: Traceback: {traceback.format_exc()} ===")
        return render_template(
            'partials/form_product_properties.html',
            default_properties={},
            user_defined_properties={},
            errors=[error_msg],
            form_type='part'
        )
